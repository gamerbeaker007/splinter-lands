import datetime

import streamlit as st

from src.api import spl
from src.api.db import resource_metrics
from src.graphs import resources_graphs
from src.pages.resources_metrics import resources_conversion, resources_cost_earning, resource_player


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

    resources_conversion.get_container(metrics_df, prices_df)

    resources_cost_earning.get_resource_cost(metrics_df)

    resource_player.get_resource_region_overview(metrics_df, prices_df)

    df = resource_metrics.get_historical_data()
    tab1, tab2, tab3 = st.tabs(["1000 Resource chart", "1000 DEC chart", "Grain factor chart"])
    with tab1:
        st.markdown("Below a chart that represent how much it cost (DEC) to get 1000 of the resource.")
        resources_graphs.create_land_resources_graph(df, True)
    with tab2:
        st.markdown("Below a chart that represent how much resources you will receive for 1000 DEC (1$)")
        resources_graphs.create_land_resources_dec_graph(df, True)
    with tab3:
        st.markdown("""
    Below a chart that represent what the factor is against grain based on the whitepaper
    * Grain: 0.02
    * Wood: 0.005 1 Wood = 4 Grain
    * Stone: 0.002 1 Stone = 10 Grain
    * Iron: 0.0005 1 Iron = 40 Grain
    """)
        resources_graphs.create_land_resources_factor_graph(df, False)
