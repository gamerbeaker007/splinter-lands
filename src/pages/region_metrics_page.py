import logging

import pandas as pd
import streamlit as st

from src.api.db import pp_tracking
from src.graphs import region_graphs
from src.pages.region_metrics import overall_region_info, region_header
from src.utils.data_loader import load_cached_data, get_last_updated

transaction_fee = 0.90  # 10% fee


def get_production(df):
    if not df.empty:
        columns = [
            "region_uid",
            "plot_id",
            "deed_type",
            "deed_uid",
            "token_symbol",
            "resource_symbol",
            "worksite_type",
            "in_use",
            "total_base_pp_after_cap",
            "total_construction_pp",
            "total_harvest_pp"
        ]

        resources_df = df[columns]

        if not resources_df.empty:
            # Split into non-TAX and TAX
            non_tax_df = resources_df[resources_df["token_symbol"] != "TAX"]
            tax_df = resources_df[resources_df["token_symbol"] == "TAX"]

            # Group non-TAX by token_symbol only (ignore worksite_type)
            non_tax_grouped = non_tax_df.groupby(
                ["region_uid", "token_symbol"], as_index=False
            )[["total_base_pp_after_cap", "total_harvest_pp"]].sum()

            # Add a placeholder worksite_type for consistency
            non_tax_grouped["worksite_type"] = ""

            # Group TAX by token_symbol and worksite_type
            tax_grouped = tax_df.groupby(
                ["region_uid", "token_symbol", "worksite_type"], as_index=False
            )[["total_base_pp_after_cap", "total_harvest_pp"]].sum()

            # Combine both
            grouped_df = pd.concat([non_tax_grouped, tax_grouped], ignore_index=True)

            # Step 2: Rename columns
            grouped_df = grouped_df.rename(columns={
                "total_base_pp_after_cap": "raw_pp",
                "total_harvest_pp": "boosted_pp"
            })

            if not grouped_df.empty:
                # Step 3: Pivot to wide format (flattened)
                pivot_df = grouped_df.pivot(
                    index=["region_uid"],
                    columns=["token_symbol", "worksite_type"]
                )[["raw_pp", "boosted_pp"]]

                # Step 4: Flatten MultiIndex columns
                pivot_df.columns = [
                    f"{token}_{col}".lower() if token != "TAX" else f"{token}_{worksite}_{col}".lower()
                    for col, token, worksite in pivot_df.columns
                ]

                # Reset index make region_uid as column again
                pivot_df = pivot_df.reset_index()
                # Step 4b: Calculate 'active' plots per region
                active_per_region = resources_df[resources_df.total_harvest_pp > 0].groupby(
                    "region_uid"
                ).size().reset_index(name="active")

                # Merge into pivot_df
                pivot_df = pivot_df.merge(active_per_region, on="region_uid", how="left")
                pivot_df["active"] = pivot_df["active"].fillna(0).astype(int)
                return pivot_df
            else:
                logging.warning("emnpty filtering check what todo with it?")
    return pd.DataFrame()


def prepare_data():
    deeds = load_cached_data('deeds')
    worksite_details = load_cached_data('worksite_details')
    staking_details = load_cached_data('staking_details')

    df = pd.merge(
        deeds,
        worksite_details,
        how='left',
        on='deed_uid',
        suffixes=('', '_worksite_details')
    )
    df = pd.merge(
        df,
        staking_details,
        how='left',
        on='deed_uid',
        suffixes=('', '_staking_details')

    )
    df = df.reindex(sorted(df.columns), axis=1)
    return df

def group_by_resource(df, group_field):
    return df.groupby(group_field).agg({
        'total_harvest_pp': 'sum',
        'total_base_pp_after_cap': 'sum'
    }).reset_index()


def get_per_resource_data(df):
    # Non-tax resources
    none_tax_df = df[df.token_symbol != 'TAX']
    grouped_non_tax = group_by_resource(none_tax_df, 'token_symbol')
    grouped_non_tax['resource'] = grouped_non_tax['token_symbol']

    # Tax resources
    tax_df = df[df.token_symbol == 'TAX']
    grouped_tax = group_by_resource(tax_df, 'worksite_type')
    grouped_tax['resource'] = 'TAX ' + grouped_tax['worksite_type'].str.removeprefix('TAX ')

    # Combine
    combined_df = pd.concat([
        grouped_non_tax[['resource', 'total_harvest_pp', 'total_base_pp_after_cap']],
        grouped_tax[['resource', 'total_harvest_pp', 'total_base_pp_after_cap']]
    ], ignore_index=True)
    return combined_df

def get_page():
    date_str = get_last_updated()
    if date_str:
        st.title(f"Region from: {date_str.strftime('%Y-%m-%d')}")

        all_df = prepare_data()
        region_header.get_page(all_df)
        overall_region_info.get_page(all_df)

        with st.container(border=True):
            st.subheader("Filter Options:")
            col1, col2, col3 = st.columns(3)
            filtered_all_data = all_df.copy()
            with col1:
                filter_regions = st.multiselect('Regions', options=filtered_all_data.region_uid.unique().tolist())
                if filter_regions:
                    filtered_all_data = filtered_all_data.loc[filtered_all_data.region_uid.isin(filter_regions)]
            with col2:
                filter_tract = st.multiselect('Tracts', options=filtered_all_data.tract_number.unique().tolist())
                if filter_tract:
                    filtered_all_data = filtered_all_data.loc[filtered_all_data.tract_number.isin(filter_tract)]
            with col3:
                filter_plot = st.multiselect('Plots', options=filtered_all_data.plot_number.unique().tolist())
                if filter_plot:
                    filtered_all_data = filtered_all_data.loc[filtered_all_data.plot_number.isin(filter_plot)]

        tab1, tab2, tab3 = st.tabs(['Active', 'Production', 'Region Production Overview'])
        with tab1:
            if not filtered_all_data.empty:
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

            with tab2:
                if not filtered_all_data.empty:
                    col1, col2 = st.columns([1, 3])
                    df = get_per_resource_data(filtered_all_data)
                    with col1:
                        st.write("TODO TOTAL SUM")
                    # # total_harvest_pp, total_base_pp_after_cap
                    # df = df.agg({'total_harvest_pp': 'sum', 'total_base_pp_after_cap': 'sum'}).reset_index()
                    # region_graphs.create_total_production_power(df)
                    with col2:
                        region_graphs.create_pp_per_source_type(df)


                    df = get_production(filtered_all_data)
                    raw_cols = [col for col in df.columns if col.endswith("_raw_pp")]

                    resources = [col.replace("_raw_pp", "") for col in raw_cols]
                    selected_resource = st.selectbox("Select a resource", resources)
                    region_graphs.create_land_region_production_graph(df, selected_resource)


        with tab3:
            if not df.empty:
                st.write('This is always all region data not filtered')

                df_1 = pp_tracking.get_latest_resources()
                region_graphs.create_land_region_production_sum_graph(df_1, date_str)


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
