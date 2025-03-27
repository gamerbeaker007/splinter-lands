import streamlit as st

import datetime
import streamlit as st
import pandas as pd

from src.api import spl
from src.pages.resources_metrics import resources_conversion
from src.static.icons import grain_icon_url, wood_icon_url, stone_icon_url, iron_icon_url, dec_icon_url, sps_icon_url



# Initial load for metrics & prices
@st.cache_data(ttl=300)
def load_market_data():
    metrics_df = spl.get_land_resources_pools()
    prices_df = spl.get_prices()
    return metrics_df, prices_df


def get_page():
    st.title("Resources")
    st.subheader("Resource Converter")
    metrics_df, prices_df = load_market_data()

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.info(f"""
    Convert your resources to DEC/SPS.
    Prices updated: {timestamp}
    """)
    
    with st.container(height=300):
        resources_conversion.get_container(metrics_df, prices_df)

