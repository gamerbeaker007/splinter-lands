import logging

import streamlit as st

from src.graphs import region_graphs
from src.pages.resources_metrics.tab_production import get_per_resource_data

log = logging.getLogger("Tab - production")


def plot_by_group(filtered_df, group_col, label_prefix):
    groups = filtered_df[group_col].unique().tolist()
    for group in groups:
        temp_df = filtered_df.loc[filtered_df[group_col] == group]
        title = f"{label_prefix}: {group}"
        temp_df = get_per_resource_data(temp_df)
        if not temp_df.empty:
            region_graphs.create_pp_per_source_type(temp_df, key=str(group), title=title)
        else:
            st.warning("No active deed found")


def get_page(filtered_all_data):
    plot_by = st.radio("Select compare method", options=["By Region", "By Tract"])

    if plot_by == "By Region":
        plot_by_group(filtered_all_data, group_col="region_number", label_prefix="Region")
    elif plot_by == "By Tract":
        plot_by_group(filtered_all_data, group_col="tract_number", label_prefix="Tract")
