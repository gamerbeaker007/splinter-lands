import streamlit as st

from src.pages.region_metrics import overall_region_info, region_header, filter_section, main_container
from src.utils.data_loader import load_cached_data, get_last_updated, merge_with_details
from src.utils.log_util import configure_logger

transaction_fee = 0.90  # 10% fee
log = configure_logger(__name__)


def prepare_data():
    deeds = load_cached_data('deeds')
    worksite_details = load_cached_data('worksite_details')
    staking_details = load_cached_data('staking_details')
    df = merge_with_details(deeds, worksite_details, staking_details)
    return df


def get_page():
    date_str = get_last_updated()
    if date_str:
        st.title(f"Region from: {date_str.strftime('%Y-%m-%d')}")

        all_df = prepare_data()
        region_header.get_page()
        overall_region_info.get_page(all_df)

        filtered_df = filter_section.get_page(all_df)
        if not filtered_df.empty:
            main_container.get_page(filtered_df, date_str)
        else:
            st.warning("No Data")
