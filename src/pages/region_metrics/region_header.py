import streamlit as st

from src.graphs import resources_graphs
from src.utils import data_helper

height = 600


def get_page():
    col1, col2 = st.columns([3, 2])
    with col1:
        df = data_helper.get_historical_active_data()
        resources_graphs.create_active_graph(df, height)
    with col2:
        df = data_helper.get_latest_active_data()
        if df.empty:
            st.warning("No data available to display the Active Land graph.")
            return

        active_amount = df.active_based_on_pp.iloc[0]
        in_use_amount = df.active_based_on_in_use.iloc[0]

        st.markdown(f"""
            <div style="height: {height}px; display: flex; align-items: center">
                <div>
                    <h3>{round((active_amount / 150000) * 100, 2)} % ({active_amount})
                     Active based on PP.</h3>
                    <h3>{round((in_use_amount / 150000) * 100, 2)} % ({in_use_amount})
                     Active based on in_use state.</h3>
                </div>
            </div>
        """, unsafe_allow_html=True)
