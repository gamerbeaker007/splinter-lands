import streamlit as st

from src.api import spl
from src.pages.player_overview import resources_cost_earning, resource_player


def get_page():
    metrics_df = spl.get_land_resources_pools()
    prices_df = spl.get_prices()

    player = st.text_input("Enter account name")
    tab1, tab2 = st.tabs([
        "Resource Production",
        "Region Overview"
    ])
    with tab1:
        resources_cost_earning.get_resource_cost(player, metrics_df)
    with tab2:
        resource_player.get_resource_region_overview(player, metrics_df, prices_df)
