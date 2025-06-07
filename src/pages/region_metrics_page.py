import streamlit as st

from src.pages.components import filter_section
from src.pages.region_metrics import overall_region_info, region_header, main_container
from src.utils import data_helper
from src.utils.log_util import configure_logger

transaction_fee = 0.90  # 10% fee
log = configure_logger(__name__)


def get_page():
    date_str = data_helper.get_last_updated()
    if date_str:
        st.title(f"Region from: {date_str.strftime('%Y-%m-%d')}")

        all_df = data_helper.get_land_data_merged()
        region_header.get_page()
        overall_region_info.get_page(all_df)

        filtered_df = filter_section.get_page(all_df)
        if not filtered_df.empty:
            main_container.get_page(filtered_df, date_str)
        else:
            st.warning("No Data")
