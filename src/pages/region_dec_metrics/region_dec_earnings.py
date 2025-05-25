import streamlit as st

from src.graphs.region_dec_graphs import add_total_dec, add_plots_vs_dec, add_dec
from src.utils.log_util import configure_logger

log = configure_logger(__name__)


def get_page(df):

    add_dec(df)
    add_total_dec(df)
    add_plots_vs_dec(df)
    with st.expander("DATA", expanded=False):
        st.dataframe(df)
