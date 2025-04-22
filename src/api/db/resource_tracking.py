from datetime import date

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

from src.api.db import upload
from src.models.models import RESOURCE_TRACKING_TABLE_NAME
from src.utils.log_util import configure_logger
from src.utils.resource_util import calc_costs

# Same URL as in alembic.ini
db_url = st.secrets["database"]["url"]
engine = create_engine(db_url)

log = configure_logger(__name__)


def group_by_resource(df, group_field):
    return df.groupby(group_field).agg({
        'total_harvest_pp': 'sum',
        'total_base_pp_after_cap': 'sum',
       'rewards_per_hour': 'sum',
    }).reset_index()


def upload_daily_resource_metrics(df, supply_df):
    # Non-tax resources

    none_tax_df = df[df.token_symbol != 'TAX']
    grouped_non_tax = group_by_resource(none_tax_df, 'token_symbol')
    grouped_non_tax['resource'] = grouped_non_tax['token_symbol']

    # Tax resources
    tax_df = df[df.token_symbol == 'TAX']
    grouped_tax = group_by_resource(tax_df, ['worksite_type', 'token_symbol'])
    grouped_tax['resource'] = 'TAX ' + grouped_tax['worksite_type'].str.removeprefix('TAX ')

    # Combine
    combined_df = pd.concat([
        grouped_non_tax[
            [
                'resource',
                'token_symbol',
                'total_harvest_pp',
                'total_base_pp_after_cap',
                'rewards_per_hour',
            ]
        ],

        grouped_tax[
            [
                'resource',
                'token_symbol',
                'total_harvest_pp',
                'total_base_pp_after_cap',
                'rewards_per_hour',
            ]
        ]
    ], ignore_index=True)

    # Add total supply

    combined_df['total_supply'] = combined_df['token_symbol'].apply(
        lambda symbol: supply_df.loc[
            supply_df.resource == symbol
            ].amount.sum()

    )

    # Daily production and consumption
    combined_df = pd.concat([combined_df, combined_df.apply(calc_costs, axis=1)], axis=1)

    # Finalize
    combined_df.insert(0, "date", date.today())
    columns = [
        'date',
        'resource',
        'token_symbol',
        'total_harvest_pp',
        'total_base_pp_after_cap',
        'total_supply',
        'rewards_per_hour',
        'cost_per_h_grain',
        'cost_per_h_wood',
        'cost_per_h_stone',
        'cost_per_h_iron',
    ]
    combined_df = combined_df[columns]
    upload.commit(combined_df, RESOURCE_TRACKING_TABLE_NAME)


@st.cache_data(ttl="1h")
def get_historical_data() -> pd.DataFrame:
    query = f"SELECT * FROM {RESOURCE_TRACKING_TABLE_NAME}"
    return pd.read_sql(query, engine)


@st.cache_data(ttl="1h")
def get_latest_resources() -> pd.DataFrame:
    query = f"""
        SELECT *
        FROM {RESOURCE_TRACKING_TABLE_NAME}
        WHERE date = (SELECT MAX(date) FROM {RESOURCE_TRACKING_TABLE_NAME})
    """
    return pd.read_sql(query, engine)
