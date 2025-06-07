import streamlit as st

from src.graphs import region_graphs
from src.utils import data_helper


def get_page(date_str):
    st.write('This is always all region data not filtered')
    st.write(f'Last updated {date_str.strftime("%Y-%m-%d %H:%M:%S")}')

    latest_resource_df = data_helper.get_latest_resource_tracking_data()
    # For backwards compatibility add the resource column back in
    latest_resource_df['resource'] = latest_resource_df['token_symbol']
    region_graphs.create_pp_per_source_type(latest_resource_df, key='region-overview')

    historical_df = data_helper.get_historical_resource_tracking_data()
    # For backwards compatibility add the resource column back in
    historical_df['resource'] = historical_df['token_symbol']
    region_graphs.create_land_region_historical(historical_df)
