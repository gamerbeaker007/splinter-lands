import streamlit as st

from src.pages.components import filter_section
from src.pages.components.filter_section import FilterKey
from src.pages.region_dec_metrics import region_dec_earnings
from src.utils.data_loader import load_cached_data, get_last_updated
from src.utils.log_util import configure_logger

log = configure_logger(__name__)


def get_page():
    date_str = get_last_updated()
    if date_str:
        net_dec_df = load_cached_data('resource_net_dec')
        if not net_dec_df.empty:
            st.subheader(f'Data is created at: {date_str.strftime('%Y-%m-%d %H:%M:%S')}')

            filtered_df = filter_section.get_page(net_dec_df, only=[FilterKey.PLAYERS])
            if not filtered_df.empty:
                region_dec_earnings.get_page(filtered_df,)
            else:
                st.warning("No Data")
        else:
            st.warning("""
            No data found, app might me loading/processing the data.

            This process can take up to 10 minutes.

            If nothing shows up, feel free to check back in 10 minutes.""")
