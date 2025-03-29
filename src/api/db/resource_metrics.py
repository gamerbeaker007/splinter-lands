import logging

import sqlalchemy
import streamlit as st
from datetime import date

import pandas as pd
from sqlalchemy import create_engine

from src.api import spl
from src.models.models import RESOURCE_METRICS_TABLE_NAME

# Same URL as in alembic.ini
db_url = st.secrets["database"]["url"]
engine = create_engine(db_url)

log = logging.getLogger("DB - Resource tracking")

conversion_ratios = {
    'WOOD': 4,
    'STONE': 10,
    'IRON': 40
}


def calculate_grain_equivalent_and_factor(row, grain_price):
    if row['token_symbol'] == 'GRAIN':
        return pd.Series([1, 1])
    else:
        if grain_price:
            grain_equiv = row['resource_price'] / grain_price
            factor = grain_equiv / conversion_ratios[row['token_symbol']]
            return pd.Series([grain_equiv, factor])
        else:
            return pd.Series([None, None])


def upload_land_resources_info():
    resources_df = spl.get_land_resources_pools()

    if not resources_df.empty:
        resources_df['dec_usd_value'] = spl.get_prices()['dec']
        grain_price = resources_df[resources_df['token_symbol'] == 'GRAIN']['resource_price'].values[0]

        resources_df[['grain_equivalent', 'factor']] = resources_df.apply(
            lambda row: calculate_grain_equivalent_and_factor(row, grain_price), axis=1
        )
        resources_df.insert(0, "date", date.today())

    # 5. Insert into DB
    try:
        resources_df.to_sql(
            name=RESOURCE_METRICS_TABLE_NAME,
            con=engine,
            if_exists="append",  # append rows to existing table
            index=False,
            method="multi"  # batch insert for performance
        )
        log.info(f"✅ Uploaded {len(resources_df)} records to 'resource_tracking'")
    except sqlalchemy.exc.IntegrityError as e:
        # This usually happens when a UNIQUE constraint is violated
        log.warning("⚠️ Duplicate entry detected. Likely already inserted.")
        log.debug("Details:", exc_info=e)
    except sqlalchemy.exc.OperationalError as e:
        log.error("❌ Database operational error (e.g. table does not exist)", exc_info=e)
    except Exception as e:
        log.error("❌ Unexpected failure during database upload", exc_info=e)


def get_historical_data() -> pd.DataFrame:
    query = f"SELECT * FROM {RESOURCE_METRICS_TABLE_NAME}"
    return pd.read_sql(query, engine)
