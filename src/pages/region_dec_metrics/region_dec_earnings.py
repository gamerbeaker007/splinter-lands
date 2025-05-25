import streamlit as st

from src.graphs.region_dec_graphs import add_total_dec, add_plots_vs_dec, add_dec, add_ratio_rank_plot
from src.utils.log_util import configure_logger

log = configure_logger(__name__)


def get_page(df):
    tab1, tab2, tab3 = st.tabs([
        "DEC",
        "LCE",
        "LPE",
    ])
    with tab1:
        add_dec(df)
        add_total_dec(df)
        add_plots_vs_dec(df)
    with tab2:
        df['LCE_ratio_base'] = df.total_base_pp_after_cap / df.total_dec
        df['LCE_ratio_boosted'] = df.total_harvest_pp / df.total_dec
        df['LCE_base_rank'] = df['LCE_ratio_base'].rank(method='min', ascending=False).astype(int)
        df['LCE_boosted_rank'] = df['LCE_ratio_boosted'].rank(method='min', ascending=False).astype(int)

        name = st.text_input("Enter hive name to highlight", key="LCE_name")
        add_ratio_rank_plot(
            df,
            x_column='LCE_ratio_base',
            y_column='LCE_base_rank',
            highlight_player=name,
            title='LCE Ratio vs Rank (Bubble = Base PP)',
            xaxis_title='LCE_ratio_base',
            yaxis_title='LCE_base_rank',
            hover_label='LCE_base',
            customdata_column='total_base_pp_after_cap'
        )
    with tab3:
        df['LPE_ratio'] = df.total_dec / df['count']
        df['LPE_rank'] = df['LPE_ratio'].rank(method='min', ascending=False).astype(int)

        name = st.text_input("Enter hive name to highlight", key="LPE_name")
        add_ratio_rank_plot(
            df,
            x_column='LPE_ratio',
            y_column='LPE_rank',
            highlight_player=name,
            title='LPE Ratio vs Rank (Bubble = Base PP)',
            xaxis_title='LPE_ratio',
            yaxis_title='LPE_rank',
            hover_label='LPE_ratio',
            customdata_column='total_base_pp_after_cap'
        )
        add_ratio_rank_plot(
            df,
            x_column='count',
            y_column='total_dec',
            highlight_player=name,
            title='DEC generated per hour (Bubble = Base PP)',
            xaxis_title='Amount of Plots',
            yaxis_title='Total DEC',
            hover_label='DEC',
            customdata_column='total_base_pp_after_cap'
        )

    with st.expander("DATA", expanded=False):
        st.dataframe(df)
