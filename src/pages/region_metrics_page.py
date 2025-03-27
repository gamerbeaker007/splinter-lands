import pandas as pd
import streamlit as st

from src.graphs import region_graphs
from src.static.icons import grain_icon_url, wood_icon_url, stone_icon_url, iron_icon_url, sps_icon_url, \
    research_icon_url
from src.utils.card import create_card, card_style
from src.utils.data_loader import load_cached_data, get_last_updated

transaction_fee = 0.90  # 10% fee


def get_overall_production_for_region(deeds, worksite_details, staking_details):
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
            deeds[["deed_uid", "region_uid", "worksite_type", "in_use"]],
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
            # Step 4b: Calculate 'active' plots per region
            active_per_region = resources_df[resources_df.total_harvest_pp != 0].groupby(
                "region_uid"
            ).size().reset_index(name="active")

            # Merge into pivot_df
            pivot_df = pivot_df.merge(active_per_region, on="region_uid", how="left")
            pivot_df["active"] = pivot_df["active"].fillna(0).astype(int)
            return pivot_df
    return pd.DataFrame()


icon_map = {
    "GRAIN": grain_icon_url,
    "STONE": stone_icon_url,
    "WOOD": wood_icon_url,
    "IRON": iron_icon_url,
    "SPS": sps_icon_url,
    "RESEARCH": research_icon_url,
    "TAX": research_icon_url,
}


def get_page():
    st.title("Region")
    deeds = load_cached_data('deeds')
    worksite_details = load_cached_data('worksite_details')
    staking_details = load_cached_data('staking_details')
    date_str = get_last_updated()

    df = get_overall_production_for_region(deeds, worksite_details, staking_details)

    active_count = df.active.sum()
    st.write('Active by total harvest pp != 0')
    st.subheader(f'{round((active_count / 150000) * 100, 2)} % active ({active_count}) ')
    in_use_amount = deeds.loc[deeds.in_use == True].index.size
    st.write('In use by state in deed')
    st.subheader(
        f'{round((in_use_amount / 150000) * 100, 2)} % in_use ({in_use_amount}) ')

    st.markdown(card_style, unsafe_allow_html=True)
    merged = pd.merge(
        worksite_details[["deed_uid", "token_symbol", "worksite_type"]],
        deeds[["deed_uid", 'in_use']],
        on="deed_uid",
        how="inner"
    )
    # Loop in chunks of 4 tokens per row
    tokens = worksite_details.token_symbol.unique()
    st.write('Active and inactive based on in_use state')
    for i in range(0, len(tokens), 4):
        cols = st.columns(4)
        for j, token in enumerate(tokens[i:i + 4]):
            token_df = merged[merged["token_symbol"] == token]

            total_active_deeds = token_df.loc[token_df.in_use == True]
            total_inactive_deeds = token_df.loc[token_df.in_use == False]
            active_empty = token_df.loc[(token_df.in_use == True) & (token_df.worksite_type == "")]
            card_html = create_card(
                token,
                f"Total {token} deeds: {token_df.index.size}<br>" +
                f"Active: {total_active_deeds.index.size}<br>" +
                f"Inactive: {total_inactive_deeds.index.size}<br>" +
                f"Active w/o Type: {active_empty.index.size}<br>",
                icon_map.get(token)
            )

            cols[j].markdown(card_html, unsafe_allow_html=True)

    filter_regions = st.multiselect('Filter Regions', options=deeds.region_uid.unique().tolist())

    if filter_regions:
        df = df.loc[df.region_uid.isin(filter_regions)]
    tab1, tab2 = st.tabs(['Active', 'Production'])
    with tab1:
        if not df.empty:
            region_graphs.create_land_region_active_graph(df, date_str)
    with tab2:
        if not df.empty:
            raw_cols = [col for col in df.columns if col.endswith("_raw_pp")]
            resources = [col.replace("_raw_pp", "") for col in raw_cols]
            selected_resource = st.selectbox("Select a resource", resources)
            region_graphs.create_land_region_production_graph(df, selected_resource)

    st.dataframe(df, hide_index=True)
