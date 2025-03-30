import logging

import streamlit as st

from src.pages.resources_metrics import tab_production, tab_active, tab_region_overview

log = logging.getLogger("Region - main container")


def get_page(filtered_all_data, date_str):
    tab1, tab2, tab3 = st.tabs(['Active', 'Production', 'Region Production Overview'])
    with tab1:
        if not filtered_all_data.empty:
            tab_active.get_page(filtered_all_data, date_str)
    with tab2:
        if not filtered_all_data.empty:
            tab_production.get_page(filtered_all_data)
    with tab3:
        tab_region_overview.get_page(date_str)
