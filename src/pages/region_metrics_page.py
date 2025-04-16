import time

import pandas as pd
import streamlit as st

from src.pages.region_metrics import overall_region_info, region_header, filter_section, main_container
from src.utils.data_loader import load_cached_data, get_last_updated
from src.utils.log_util import configure_logger

transaction_fee = 0.90  # 10% fee
log = configure_logger(__name__)


def prepare_data():
    start = time.time()
    deeds = load_cached_data('deeds')
    worksite_details = load_cached_data('worksite_details')
    staking_details = load_cached_data('staking_details')

    df = pd.merge(
        deeds,
        worksite_details,
        how='left',
        on='deed_uid',
        suffixes=('', '_worksite_details')
    )
    df = pd.merge(
        df,
        staking_details,
        how='left',
        on='deed_uid',
        suffixes=('', '_staking_details')

    )
    df = df.reindex(sorted(df.columns), axis=1)
    log.info(f'Prepare data took: {time.time() - start:.02f}s')
    return df


def get_page():
    date_str = get_last_updated()
    if date_str:
        st.title(f"Region from: {date_str.strftime('%Y-%m-%d')}")

        all_df = prepare_data()
        region_header.get_page()
        overall_region_info.get_page(all_df)

        # filtered_all_data = filter_section.get_page(all_df)
        # Display in main panel
        # Layout: left for main content, right for filters
        main_col, filter_col = st.columns([3, 1], gap="large")  # Adjust ratio as needed
        with filter_col:
            filtered_df = filter_section.get_page(all_df)
        with main_col:
            if not filtered_df.empty:
                main_container.get_page(filtered_df, date_str)
            else:
                st.warning("No Data")
