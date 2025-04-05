import streamlit as st

from src.api.db import pp_tracking
from src.graphs import region_graphs


def get_page(date_str):
    st.write('This is always all region data not filtered')
    st.write(f'Last updated {date_str}')

    latest_resource_df = pp_tracking.get_latest_resources()
    region_graphs.create_pp_per_source_type(latest_resource_df)

    historical_df = pp_tracking.get_historical_data()
    region_graphs.create_land_region_historical(historical_df)
