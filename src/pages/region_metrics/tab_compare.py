import logging

import streamlit as st

from src.graphs import region_graphs
from src.pages.region_metrics.tab_production import get_per_resource_data

log = logging.getLogger("Tab - production")

MAX_NUMBER_OF_PLOTS = 6


def plot_by_group(filtered_df, group_col, label_prefix):
    groups = filtered_df[group_col].unique().tolist()
    cols = st.columns(3)  # create 3 columns

    combined_df = None  # This will hold all data side-by-side
    if len(groups) > MAX_NUMBER_OF_PLOTS:
        st.warning(f"Refine filters to many plot limited to {MAX_NUMBER_OF_PLOTS}")

    for i, group in enumerate(groups):
        if i == MAX_NUMBER_OF_PLOTS:
            break

        group_df = filtered_df.loc[filtered_df[group_col] == group]
        title = f"{label_prefix}: {group}"
        group_df = get_per_resource_data(group_df)

        col = cols[i % 3]  # rotate through columns
        with col:
            if not group_df.empty:
                region_graphs.create_pp_per_source_type(group_df, key=str(group), title=title, slim=True)
            else:
                st.warning("No active deed found")

        renamed = group_df[['total_harvest_pp', 'total_base_pp_after_cap']].copy()
        renamed.columns = [f"total_harvest_pp_{group_col}_{group}", f"total_base_pp_after_cap_{group_col}_{group}"]
        # Add an index to align on — for example, resource name
        renamed.index = group_df['resource']  # Adjust if you have a different key column

        # Merge with the combined_df
        if combined_df is None:
            combined_df = renamed
        else:
            combined_df = combined_df.join(renamed, how='outer')

    with st.expander("DATA"):
        st.dataframe(combined_df)


def get_page(filtered_all_data):
    plot_by = st.radio("Select compare method", options=["By Region", "By Tract"])

    st.markdown("""
    ### PP comparison by resource
    <span style="display: inline-block;
    width: 12px; height: 12px; background-color: steelblue; margin-right: 6px;"></span>
    RAW PP
    <span style="display: inline-block;
    width: 20px; height: 3px; background-color: lightgray; margin-right: 6px; vertical-align: middle;"></span>
    BOOSTED PP
    """, unsafe_allow_html=True)

    st.markdown("""
    """, unsafe_allow_html=True)

    if plot_by == "By Region":
        plot_by_group(filtered_all_data, group_col="region_number", label_prefix="Region")
    elif plot_by == "By Tract":
        plot_by_group(filtered_all_data, group_col="tract_number", label_prefix="Tract")
