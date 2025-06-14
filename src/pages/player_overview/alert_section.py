import pandas as pd
import streamlit as st

from src.pages.player_overview.components.deed_type import deed_type_style, add_deed_type


def get_section(df):
    # Filter plots that are done or full
    alert_df = df[(df['percentage_done'] >= 100) & (df.resource_symbol != "TAX")]

    if not alert_df.empty:
        with st.expander("🚨 Attention Needed – Full or Finished Plots"):
            st.markdown("⚠️ **Alert:** These plots need immediate attention! "
                        "The storage is either full or the worksite has finished building.")

            # Inject CSS once
            st.markdown(deed_type_style, unsafe_allow_html=True)

            # Begin flexbox container
            container_html = '<div style="display: flex; flex-wrap: wrap; gap: 16px; justify-content: center;">'

            # Append each card
            for _, row in alert_df.iterrows():
                region = row.get("region_number")
                plot = row.get("plot_id")
                if pd.notna(region) and pd.notna(plot):
                    card_html = add_deed_type(row)
                    container_html += card_html

            # Close flexbox container
            container_html += '</div>'

            # Render full HTML
            st.markdown(container_html, unsafe_allow_html=True)
