import streamlit as st

from src.pages.resources_metrics.summary_components.boost_info import print_boost
from src.pages.resources_metrics.summary_components.deed_type_info import print_deed_types
from src.pages.resources_metrics.summary_components.player_info import print_player_info
from src.pages.resources_metrics.summary_components.plot_status_info import print_plot_status
from src.pages.resources_metrics.summary_components.rarity_info import print_rarity
from src.pages.resources_metrics.summary_components.worksite_type_info import print_worksite_types


def get_page(filtered_all_data):
    st.markdown("### Player Overview")

    print_player_info(filtered_all_data)
    print_rarity(filtered_all_data)
    print_deed_types(filtered_all_data)
    print_worksite_types(filtered_all_data)
    print_plot_status(filtered_all_data)
    print_boost(filtered_all_data)
