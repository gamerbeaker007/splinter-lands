import logging

import pandas as pd
import streamlit as st

from src.graphs import region_graphs
from src.pages.region_metrics import overall_region_info, region_header
from src.utils.data_loader import load_cached_data, get_last_updated

transaction_fee = 0.90  # 10% fee


def get_overall_production_for_region(df):
    if not df.empty:
        columns = [
            "region_uid",
            "plot_id",
            "deed_type",
            "deed_uid",
            "token_symbol",
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

    suffixes = ('_worksite_details', '_staking_details')
    matching_columns = [col for col in df.columns if col.endswith(suffixes)]
    logging.info(f'Reminder whatch these columns {matching_columns}')
    return df


def get_page():
    date_str = get_last_updated()
    if date_str:
        st.title(f"Region from: {date_str.strftime('%Y-%m-%d')}")

        all_region_date_df = prepare_data()
        df = get_overall_production_for_region(all_region_date_df)

        region_header.get_page(all_region_date_df)
        overall_region_info.get_page(all_region_date_df)

        filter_regions = st.multiselect('Filter Regions', options=all_region_date_df.region_uid.unique().tolist())
        if filter_regions:
            df = df.loc[df.region_uid.isin(filter_regions)]

        tab1, tab2, tab3 = st.tabs(['Active', 'Production', 'Overall Production'])
        with tab1:
            if not df.empty:
                region_graphs.create_land_region_active_graph(df, date_str)
            with tab2:
                if not df.empty:
                    raw_cols = [col for col in df.columns if col.endswith("_raw_pp")]
                    resources = [col.replace("_raw_pp", "") for col in raw_cols]
                    selected_resource = st.selectbox("Select a resource", resources)
                    region_graphs.create_land_region_production_graph(df, selected_resource)
        with tab3:
            if not df.empty:
                region_graphs.create_land_region_production_sum_graph(all_region_date_df, date_str)

        st.dataframe(df, hide_index=True)
