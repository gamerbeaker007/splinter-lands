import streamlit as st
from src.graphs import region_graphs


def get_active_df(df):
    active_df = (
        df[df["total_harvest_pp"] > 0]
        .groupby("region_uid")
        .size()
        .reset_index(name="active")
    )
    # Count total plots per region
    total_df = (
        df.groupby("region_uid")
        .size()
        .reset_index(name="total")
    )
    # Merge active and total counts, then calculate inactive as total - active
    df = total_df.merge(active_df, on="region_uid", how="left")
    df["active"] = df["active"].fillna(0).astype(int)
    df["inactive"] = df["total"] - df["active"]
    return df


def get_page(filtered_all_data, date_str):
    active_df = get_active_df(filtered_all_data)
    region_graphs.create_land_region_active_graph(active_df, date_str)
    with st.expander('Inactive deeds'):
        inactive_deeds = filtered_all_data[
            (filtered_all_data["total_harvest_pp"].isna()) |
            (filtered_all_data["total_harvest_pp"] <= 0)
            ]
        st.dataframe(
            inactive_deeds[
                [
                    'region_number',
                    'tract_number',
                    'plot_number',
                    'total_harvest_pp'
                ]
            ],
            hide_index=True)
