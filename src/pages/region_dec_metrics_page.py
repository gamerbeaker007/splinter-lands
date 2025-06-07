import pandas as pd
import streamlit as st

from src.pages.components import filter_section
from src.pages.components.filter_section import FilterKey
from src.pages.region_dec_metrics import region_dec_earnings
from src.utils import data_helper
from src.utils.log_util import configure_logger

log = configure_logger(__name__)


def add_dec_columns(land_df, player_df):
    df = land_df.groupby('player').agg({
        'total_dec_stake_needed': 'sum',
        'total_dec_stake_in_use': 'sum',
    }).reset_index()
    player_df = pd.merge(player_df, df, on='player')
    df1 = (
        land_df.groupby(['region_uid', 'player'], as_index=False)
        .agg({'total_dec_staked': 'first'})
        .groupby('player', as_index=False)
        .agg({'total_dec_staked': 'sum'})
    )
    return pd.merge(player_df, df1, on=['player'])


def get_page():
    date_str = data_helper.get_last_updated()
    if date_str:
        land_df = data_helper.get_land_data_merged()
        player_summary_df = data_helper.get_player_summary_data()
        player_summary_df = add_dec_columns(land_df, player_summary_df)
        if not player_summary_df.empty:
            st.subheader(f'Data snapshot is from: {date_str.strftime('%Y-%m-%d %H:%M:%S')}')

            filtered_df = filter_section.get_page(player_summary_df, only=[FilterKey.PLAYERS])
            if not filtered_df.empty:
                region_dec_earnings.get_page(filtered_df)
            else:
                st.warning("No Data")
        else:
            st.warning("""
            No data found, app might me loading/processing the data.

            This process can take up to 10 minutes.

            If nothing shows up, feel free to check back in 10 minutes.""")
