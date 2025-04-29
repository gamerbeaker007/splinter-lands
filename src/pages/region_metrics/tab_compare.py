import pandas as pd
import streamlit as st

from src.graphs import region_graphs
from src.pages.region_metrics.tab_production import get_per_resource_data
from src.utils.log_util import configure_logger

log = configure_logger(__name__)

MAX_NUMBER_OF_PLOTS = 6


def plot_by_group(filtered_df, group_col, label_prefix):
    groups = filtered_df[group_col].unique().tolist()

    check_size(len(groups))

    cols = st.columns(3)  # create 3 columns
    combined_df = None  # This will hold all data side-by-side
    groups = groups[:MAX_NUMBER_OF_PLOTS]
    for i, group in enumerate(groups):

        group_df = filtered_df.loc[filtered_df[group_col] == group]
        title = f"{label_prefix}: {group}"

        group_df, renamed = process_group(group_df, f'{group_col}_{group}')

        col = cols[i % 3]  # rotate through columns
        with col:
            if not group_df.empty:
                region_graphs.create_pp_per_source_type(group_df, key=str(group), title=title, slim=True)
            else:
                st.warning("No active deed found")

        if combined_df is None:
            combined_df = renamed
        else:
            combined_df = combined_df.join(renamed, how='outer')

    with st.expander("DATA"):
        st.dataframe(combined_df)


def check_size(size):
    if size > MAX_NUMBER_OF_PLOTS:
        st.warning(
            f"Too many plot combinations found. "
            f"Showing only the first {MAX_NUMBER_OF_PLOTS}. "
            f"Refine filters to see more.")


def plot_split(df):
    # Get unique tract and region numbers
    tracts = df['tract_number'].unique()
    regions = df['region_number'].unique()

    # Create all combinations
    cross_df = pd.MultiIndex.from_product([tracts, regions], names=['tract_number', 'region_number']).to_frame(
        index=False)

    check_size(cross_df.index.size)

    cols = st.columns(3)  # create 3 columns
    combined_df = None  # This will hold all data side-by-side
    cross_df = cross_df.head(MAX_NUMBER_OF_PLOTS)
    for idx, (_, row) in enumerate(cross_df.iterrows()):
        region = row['region_number']
        tract = row['tract_number']
        group_df = df.loc[(df['region_number'] == region) & (df['tract_number'] == tract)]
        title = f"Region: {region} - Tract: {tract}"
        group = f'{region} + {tract}'

        group_df, renamed = process_group(group_df, group)

        col = cols[idx % 3]  # rotate through columns
        with col:
            if not group_df.empty:
                region_graphs.create_pp_per_source_type(group_df, key=str(f'{region}+{tract}'), title=title, slim=True)
            else:
                st.warning("No active deed found")

        if combined_df is None:
            combined_df = renamed
        else:
            combined_df = combined_df.join(renamed, how='outer')

    with st.expander("DATA"):
        st.dataframe(combined_df)


def process_group(group_df, group_title):
    group_df = get_per_resource_data(group_df)
    renamed = group_df[['total_harvest_pp', 'total_base_pp_after_cap']].copy()
    renamed.columns = [f"total_harvest_pp_{group_title}", f"total_base_pp_after_cap_{group_title}"]
    # Add an index to align on — for example, resource name
    renamed.index = group_df['resource']  # Adjust if you have a different key column
    return group_df, renamed


def get_page(filtered_all_data):
    plot_by = st.radio("Compare by", ["Region", "Tract", "Region - Tract"])

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

    if plot_by == "Region":
        plot_by_group(filtered_all_data, group_col="region_number", label_prefix="Region")
    elif plot_by == "Tract":
        plot_by_group(filtered_all_data, group_col="tract_number", label_prefix="Tract")
    elif plot_by == "Region - Tract":
        plot_split(filtered_all_data)
