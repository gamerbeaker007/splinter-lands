import pandas as pd
import streamlit as st

from src.graphs import region_graphs
from src.utils.log_util import configure_logger

log = configure_logger(__name__)


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
                log.warning("emnpty filtering check what todo with it?")
    return pd.DataFrame()


def get_page(filtered_all_data):
    col1, col2 = st.columns([1, 3])
    resource_df = get_per_resource_data(filtered_all_data)
    if not resource_df.empty:
        with col1:
            totals = {
                'RAW PP': resource_df['total_base_pp_after_cap'].sum(),
                'BOOSTED PP': resource_df['total_harvest_pp'].sum()
            }
            total_resources_df = pd.DataFrame(list(totals.items()), columns=['Type', 'Total PP'])
            region_graphs.create_total_production_power(total_resources_df)
        with col2:
            region_graphs.create_pp_per_source_type(resource_df, key='production-overview')

        resource_df = get_production(filtered_all_data)
        raw_cols = [col for col in resource_df.columns if col.endswith("_raw_pp")]

        resources = [col.replace("_raw_pp", "") for col in raw_cols]
        selected_resource = st.selectbox("Select a resource", resources)
        region_graphs.create_land_region_production_graph(resource_df, selected_resource)
    else:
        st.warning("No active deed found")
