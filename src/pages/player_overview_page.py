import pandas as pd
import streamlit as st

from src.api import spl
from src.pages.player_overview import resources_cost_earning, resource_player, resource_player_deed
from src.utils.log_util import configure_logger

log = configure_logger(__name__)


def prepare_data(player):
    if player:
        log.info(f"Land retrieval for account: {player}")
        deeds, worksite_details, staking_details = spl.get_land_region_details_player(player)

        if worksite_details.empty:
            st.warning(f'No worksites found for player {player}')
        else:
            merged_df = pd.merge(
                deeds,
                worksite_details,
                how='left',
                on=['region_uid', 'deed_uid'],
                suffixes=('', '_y_worksite_details')
            )
            merged_df = pd.merge(
                merged_df,
                staking_details,
                how='left',
                on=['region_uid', 'deed_uid'],
                suffixes=('', '_y_staking_details')

            )
            return merged_df
    return pd.DataFrame()


def get_page():
    metrics_df = spl.get_land_resources_pools()
    prices_df = spl.get_prices()

    player = st.text_input("Enter account name")
    df = prepare_data(player)

    if player:
        tab1, tab2, tab3 = st.tabs([
            "Resource Production",
            "Region Overview",
            "Deed Overview"
        ])
        with tab1:
            resources_cost_earning.get_resource_cost(df, metrics_df)
        with tab2:
            resource_player.get_resource_region_overview(df, player, metrics_df, prices_df)
        with tab3:
            resource_player_deed.get_page(df)
