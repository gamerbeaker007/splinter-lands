import logging

import streamlit as st

from src.pages.region_metrics import tab_compare, tab_active, tab_summary, tab_production, tab_region_overview

log = logging.getLogger("Region - main container")


def get_page(filtered_all_data, date_str):
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            'Active',
            'Production',
            'Compare',
            'Summary',
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
        tab_region_overview.get_page(date_str)
