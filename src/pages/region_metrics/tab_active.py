import streamlit as st
from src.graphs import region_graphs


def get_active_df(df, group_by_col):
    active_df = (
        df[df["total_harvest_pp"] > 0]
        .groupby(group_by_col)
        .size()
        .reset_index(name="active")
    )
    total_df = (
        df.groupby(group_by_col)
        .size()
        .reset_index(name="total")
    )
    df = total_df.merge(active_df, on=group_by_col, how="left")
    df["active"] = df["active"].fillna(0).astype(int)
    df["inactive"] = df["total"] - df["active"]
    return df


def get_page(filtered_all_data, date_str):
    unique_regions = filtered_all_data.region_uid.unique().tolist()

    if len(unique_regions) > 1:
        # Overview by region
        group_by_col = "region_uid"
        active_df = get_active_df(filtered_all_data, group_by_col)
        region_graphs.create_land_region_active_graph(active_df, date_str, group_by_col)
    else:
        # Breakdown by tract for selected region
        group_by_col = "tract_uid" if "tract_uid" in filtered_all_data.columns else "tract_number"
        active_df = get_active_df(filtered_all_data, group_by_col)
        region_graphs.create_land_region_active_graph(active_df, date_str, group_by_col)

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
            hide_index=True
        )
