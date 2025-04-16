import streamlit as st

from src.pages.region_metrics import tab_compare, tab_active, tab_summary, tab_production, tab_region_overview, \
    tab_castle_keep
from src.utils.log_util import configure_logger

log = configure_logger(__name__)


def get_page(filtered_all_data, date_str):
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            'Active',
            'Production',
            'Compare',
            'Summary',
            'Castle/Keeps',
            'Region Production Overview'
        ]
    )
    with tab1:
        if not filtered_all_data.empty:
            tab_active.get_page(filtered_all_data, date_str)
    with tab2:
        if not filtered_all_data.empty:
            tab_production.get_page(filtered_all_data)
    with tab3:
        if not filtered_all_data.empty:
            tab_compare.get_page(filtered_all_data)
    with tab4:
        if not filtered_all_data.empty:
            tab_summary.get_page(filtered_all_data)
    with tab5:
        if not filtered_all_data.empty:
            tab_castle_keep.get_page(filtered_all_data)
    with tab6:
        tab_region_overview.get_page(date_str)
