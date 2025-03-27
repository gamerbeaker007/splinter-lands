import pandas as pd
import streamlit as st

from src.graphs import region_graphs
from src.utils.data_loader import load_cached_data

transaction_fee = 0.90  # 10% fee

def calc():
    deeds = load_cached_data('deeds')
    worksite_details = load_cached_data('worksite_details')
    staking_details = load_cached_data('staking_details')
    if not deeds.empty and not worksite_details.empty and not staking_details.empty:
        # Merge worksite_details with staking_details on deed_uid
        merged = pd.merge(
            worksite_details[["deed_uid", "token_symbol"]],
            staking_details[["deed_uid", "total_base_pp_after_cap", "total_construction_pp", "total_harvest_pp"]],
            on="deed_uid",
            how="inner"
        )

        # Merge in region_id from deeds
        resources_df = pd.merge(
            merged,
            deeds[["deed_uid", "region_uid", "worksite_type"]],
            on="deed_uid",
            how="left"
        )

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
        # pivot_df['date'] = date
        pivot_df['active'] = resources_df.loc[resources_df.total_base_pp_after_cap != 0].index.size
        return pivot_df


def get_page():
    st.title("Region")
    df = calc()
    region_graphs.create_land_region_active_graph(df)
