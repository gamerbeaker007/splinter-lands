from datetime import date

import pandas as pd
import streamlit as st

from src.api import spl
from src.api.db import upload
from src.api.db.session import get_session
from src.models.models import RESOURCE_HUB_METRICS_TABLE_NAME
from src.static.static_values_enum import grain_conversion_ratios
from src.utils.log_util import configure_logger

log = configure_logger(__name__)


def calculate_grain_equivalent_and_factor(row, grain_price):
    if row['token_symbol'] == 'GRAIN':
        return pd.Series([1, 1])
    else:
        if grain_price:
            grain_equiv = row['resource_price'] / grain_price
            factor = grain_equiv / grain_conversion_ratios[row['token_symbol']]
            return pd.Series([grain_equiv, factor])
        else:
            return pd.Series([None, None])


def upload_land_resources_info():
    resources_df = spl.get_land_resources_pools()

    if not resources_df.empty:
        dec_price = spl.get_prices()['dec'].values[0]
        resources_df['dec_usd_value'] = float(dec_price)
        grain_price = resources_df[resources_df['token_symbol'] == 'GRAIN']['resource_price'].values[0]

        resources_df[['grain_equivalent', 'factor']] = resources_df.apply(
            lambda row: calculate_grain_equivalent_and_factor(row, grain_price), axis=1
        )
        resources_df.insert(0, "date", date.today())

    upload.commit(resources_df, RESOURCE_HUB_METRICS_TABLE_NAME)


@st.cache_data(ttl="1h")
def get_historical_data() -> pd.DataFrame:
    Session = get_session()
    with Session() as session:
        query = f"SELECT * FROM {RESOURCE_HUB_METRICS_TABLE_NAME}"
        return pd.read_sql(query, con=session.bind)
