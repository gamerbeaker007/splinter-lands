import logging
from datetime import date

import pandas as pd
import sqlalchemy
import streamlit as st
from sqlalchemy import create_engine

from src.models.models import PP_TRACKING_TABLE_NAME

# Same URL as in alembic.ini
db_url = st.secrets["database"]["url"]
engine = create_engine(db_url)

log = logging.getLogger("DB - Resource tracking")


def group_by_resource(df, group_field):
    return df.groupby(group_field).agg({
        'total_harvest_pp': 'sum',
        'total_base_pp_after_cap': 'sum'
    }).reset_index()


def upload_daily_resource_metrics(df):
    # Non-tax resources
    none_tax_df = df[df.token_symbol != 'TAX']
    grouped_non_tax = group_by_resource(none_tax_df, 'token_symbol')
    grouped_non_tax['resource'] = grouped_non_tax['token_symbol']

    # Tax resources
    tax_df = df[df.token_symbol == 'TAX']
    grouped_tax = group_by_resource(tax_df, 'worksite_type')
    grouped_tax['resource'] = 'TAX ' + grouped_tax['worksite_type'].str.removeprefix('TAX ')

    # Combine
    combined_df = pd.concat([
        grouped_non_tax[['resource', 'total_harvest_pp', 'total_base_pp_after_cap']],
        grouped_tax[['resource', 'total_harvest_pp', 'total_base_pp_after_cap']]
    ], ignore_index=True)

    # Finalize
    combined_df.insert(0, "date", date.today())

    if not engine.dialect.has_table(engine.connect(), PP_TRACKING_TABLE_NAME):
        raise RuntimeError("Table 'resource_tracking' does not exist. Did you forget to run Alembic migrations?")

    # 5. Insert into DB
    try:
        combined_df.to_sql(
            name=PP_TRACKING_TABLE_NAME,
            con=engine,
            if_exists="append",  # append rows to existing table
            index=False,
            method="multi"  # batch insert for performance
        )
        log.info(f"✅ Uploaded {len(combined_df)} records to 'resource_tracking'")
    except sqlalchemy.exc.IntegrityError as e:
        # This usually happens when a UNIQUE constraint is violated
        log.warning("⚠️ Duplicate entry detected. Likely already inserted.")
        log.debug("Details:", exc_info=e)
    except sqlalchemy.exc.OperationalError as e:
        log.error("❌ Database operational error (e.g. table does not exist)", exc_info=e)
    except Exception as e:
        log.error("❌ Unexpected failure during database upload", exc_info=e)


def get_historical_data() -> pd.DataFrame:
    query = f"SELECT * FROM {PP_TRACKING_TABLE_NAME}"
    return pd.read_sql(query, engine)


def get_latest_resources() -> pd.DataFrame:
    query = f"""
        SELECT *
        FROM {PP_TRACKING_TABLE_NAME}
        WHERE date = (SELECT MAX(date) FROM {PP_TRACKING_TABLE_NAME})
    """
    return pd.read_sql(query, engine)
