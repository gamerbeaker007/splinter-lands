import streamlit as st

from src.graphs.region_dec_graphs import add_total_dec, add_plots_vs_dec, add_dec, add_lpe_base_rank_plot
from src.utils.log_util import configure_logger

log = configure_logger(__name__)


def get_page(df):

    tab1, tab2 = st.tabs([
        "DEC",
        "LPE",
    ])
    with tab1:
        add_dec(df)
        add_total_dec(df)
        add_plots_vs_dec(df)
    with tab2:
        df['LPE_ratio_base'] = df.total_base_pp_after_cap / df.total_dec
        df['LPE_ratio_boosted'] = df.total_harvest_pp / df.total_dec
        df['LPE_base_rank'] = df['LPE_ratio_base'].rank(method='min', ascending=False).astype(int)
        df['LPE_boosted_rank'] = df['LPE_ratio_boosted'].rank(method='min', ascending=False).astype(int)

        name = st.text_input("Enter hive name to highlight")
        add_lpe_base_rank_plot(df, name)

    with st.expander("DATA", expanded=False):
        st.dataframe(df)
