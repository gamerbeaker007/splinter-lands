import pandas as pd
import streamlit as st

from src.api import spl
from src.pages.player_overview import resources_cost_earning, resource_player, resource_player_deed, rankings
from src.pages.region_metrics import filter_section
from src.utils.data_loader import merge_with_details, load_cached_data
from src.utils.log_util import configure_logger

log = configure_logger(__name__)


def prepare_data(player):
    if player:
        log.info(f"Land retrieval for account: {player}")
        deeds, worksite_details, staking_details = spl.get_land_region_details_player(player)

        if worksite_details.empty:
            st.warning(f"""
            No land data found for player: {player}.

            Note: it's case-sensitive
            """)

        else:
            df = merge_with_details(deeds, worksite_details, staking_details)
            return df
    return pd.DataFrame()


@st.cache_data(ttl='1h')
def prepare_daily_data():
    deeds = load_cached_data('deeds')
    worksite_details = load_cached_data('worksite_details')
    staking_details = load_cached_data('staking_details')
    df = merge_with_details(deeds, worksite_details, staking_details)
    return df


def get_page():
    metrics_df = spl.get_land_resources_pools()
    prices_df = spl.get_prices()
    all_daily_df = prepare_daily_data()

    # Text input with default from session
    player_input = st.text_input("Enter account name", value=st.session_state.get("account", ""))

    # Handle account change
    if player_input:
        if st.session_state.get("account") != player_input:
            st.session_state["account"] = player_input
            filter_section.reset_filters()
            st.rerun()

    # Only run after rerun when session is correctly set
    player = st.session_state.get("account")
    if not player:
        st.info("Please enter a player account to begin.")
        return

    # Prepare and filter data
    spinner_placeholder = st.empty()
    df = prepare_data(player)
    if df.empty:
        return

    filtered_df = filter_section.get_page(df)

    # Tabs view
    tab1, tab2, tab3, tab4 = st.tabs([
        "Resource Production",
        "Region Overview",
        "Land Rankings",
        "Deed Overview",
    ])
    with tab1:
        add_spinner(spinner_placeholder, "📊 Calculating resource costs and earnings...")
        resources_cost_earning.get_resource_cost(filtered_df, metrics_df, prices_df)
    with tab2:
        add_spinner(spinner_placeholder, "🌍 Generating region overview...")
        resource_player.get_resource_region_overview(filtered_df, player, metrics_df, prices_df)
    with tab3:
        add_spinner(spinner_placeholder, "📊 Create land ranking overview ...")
        rankings.add_ranking_overview(all_daily_df, player)
    with tab4:
        add_spinner(spinner_placeholder, "📜 Building deed overview (fetching staked assets)...")
        resource_player_deed.get_player_deed_overview(filtered_df)

    spinner_placeholder.empty()


def add_spinner(spinner_placeholder, current_status):
    spinner_html = f"""
        <div style="display: flex; align-items: center;">
            <img src="https://i.imgur.com/llF5iyg.gif" width="24" style="margin-right: 10px;">
            <span>{current_status}</span>
        </div>
        """
    spinner_placeholder.markdown(spinner_html, unsafe_allow_html=True)
