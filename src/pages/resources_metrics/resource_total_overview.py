import streamlit as st

from src.api.db import resource_tracking
from src.static.static_values_enum import resource_icon_map
from src.utils.data_loader import load_cached_data, merge_with_details
from src.utils.large_number_util import format_large_number


def prepare_data():
    deeds = load_cached_data('deeds')
    worksite_details = load_cached_data('worksite_details')
    staking_details = load_cached_data('staking_details')
    df = merge_with_details(deeds, worksite_details, staking_details)
    return df


def render_resource_card(row, df):
    token = row['token_symbol']
    icon_url = resource_icon_map.get(token, '')
    total_supply = format_large_number(row['total_supply'])

    # Daily production
    daily_production = row['rewards_per_hour'] * 24

    # Daily consumption (just this row)
    daily_costs = {
        "GRAIN": row["cost_per_h_grain"] * 24,
        "WOOD": row["cost_per_h_wood"] * 24,
        "STONE": row["cost_per_h_stone"] * 24,
        "IRON": row["cost_per_h_iron"] * 24,
    }

    # If resource is WOOD, IRON, or STONE, calculate total consumption across all rows
    extra_consumed = "N/A"
    if token in ["GRAIN", "WOOD", "STONE", "IRON"]:
        col_name = f"cost_per_h_{token.lower()}"
        total_used = df[col_name].sum() * 24
        extra_consumed = f'{format_large_number(total_used)}'

    with st.container(border=True):
        st.markdown(f"""
        ### <img src="{icon_url}" width="24" style="vertical-align:middle"> {token}
        - **Total Available**: `{total_supply}`
        - **Produced Daily**: `{format_large_number(daily_production)}`
        - **Consumed Daily**: `{extra_consumed}`

        **Consumes:**
        """, unsafe_allow_html=True)

        for res, val in daily_costs.items():
            if val > 0:
                st.markdown(f"""<img src="{resource_icon_map[res]}" width="16"> {res}: `{format_large_number(val)}`""",
                            unsafe_allow_html=True)


def add_section():
    st.subheader("Daily Production / Consumption Overview")
    resource_leaderboard = resource_tracking.get_latest_resources()
    resource_leaderboard = resource_leaderboard[resource_leaderboard["token_symbol"].notnull()]

    if resource_leaderboard.empty:
        st.warning("No data to present")
        return

    # Filter out 'TAX' and reorder
    desired_order = ["GRAIN", "WOOD", "STONE", "IRON", "RESEARCH", "SPS"]
    filtered_df = resource_leaderboard[resource_leaderboard["token_symbol"].isin(desired_order)]
    ordered_df = filtered_df.set_index("token_symbol").loc[desired_order].reset_index()

    max_cols = 4
    cols = st.columns(max_cols)
    for idx, (_, row) in enumerate(ordered_df.iterrows()):
        col_idx = idx % max_cols

        with cols[col_idx]:
            render_resource_card(row, resource_leaderboard)

    with st.expander("DATA", expanded=False):
        st.dataframe(ordered_df, hide_index=True)
