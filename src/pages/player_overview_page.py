import pandas as pd
import streamlit as st

from src.api import spl
from src.pages.player_overview import resources_cost_earning, resource_player, resource_player_deed, rankings, \
    alert_section
from src.pages.components import filter_section, sorting_section
from src.pages.player_overview.helper.progress_helper import get_progress_info
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


def get_progress_info_row(row):
    projected_end_date = row.get('projected_end', None)
    projected_created_date = row.get('project_created_date', None)
    hours_since_last_op = row.get('hours_since_last_op', 0)
    boosted_pp = row.get('total_harvest_pp', 0)
    return get_progress_info(hours_since_last_op, projected_created_date, projected_end_date, boosted_pp)


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

    if filtered_df.empty:
        st.warning("No Deeds found with current filter")
        return


    # Add alert section for deeds that need attention:
    progress_info = filtered_df.apply(get_progress_info_row, axis=1)
    enriched_df = filtered_df.join(progress_info).copy()
    sorted_df = sorting_section.get_sorting_section(enriched_df)

    alert_section.get_section(sorted_df)

    # Tabs view
    tab1, tab2, tab3, tab4 = st.tabs([
        "Resource Production",
        "Region Overview",
        "Land Rankings",
        "Deed Overview",
    ])
    with tab1:
        add_spinner(spinner_placeholder, "📊 Calculating resource costs and earnings...")
        resources_cost_earning.get_resource_cost(sorted_df, metrics_df, prices_df)
    with tab2:
        add_spinner(spinner_placeholder, "🌍 Generating region overview...")
        resource_player.get_resource_region_overview(sorted_df, player, metrics_df, prices_df)
    with tab3:
        add_spinner(spinner_placeholder, "📊 Create land ranking overview ...")
        rankings.add_ranking_overview(all_daily_df, player)
    with tab4:
        add_spinner(spinner_placeholder, "📜 Building deed overview (fetching staked assets)...")
        resource_player_deed.get_player_deed_overview(sorted_df)

    spinner_placeholder.empty()


def add_spinner(spinner_placeholder, current_status):
    spinner_html = f"""
        <div style="display: flex; align-items: center;">
            <img src="https://i.imgur.com/llF5iyg.gif" width="24" style="margin-right: 10px;">
            <span>{current_status}</span>
        </div>
        """
    spinner_placeholder.markdown(spinner_html, unsafe_allow_html=True)
