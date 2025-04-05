import streamlit as st

from src.api.db import active_metrics
from src.graphs import resources_graphs


def get_page():
    col1, col2 = st.columns([1, 2])
    with col1:
        df = active_metrics.get_historical_data()
        resources_graphs.create_active_graph(df)
    with col2:
        df = active_metrics.get_latest_active()
        active_amount = df.active_based_on_pp.iloc[0]
        in_use_amount = df.active_based_on_in_use.iloc[0]
        st.markdown(f"""
            ### {round((active_amount / 150000) * 100, 2)} % ({active_amount}) Active based on PP.
            ### {round((in_use_amount / 150000) * 100, 2)} % ({in_use_amount}) Active based on in_use state.
            """
        )
