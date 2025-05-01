import pandas as pd
import streamlit as st

from src.api.db import resource_tracking
from src.graphs import resources_supply_graphs
from src.static.static_values_enum import resource_icon_map, NATURAL_RESOURCE
from src.utils.large_number_util import format_large_number
from src.utils.resource_util import reorder_column


def add_section():
    add_daily_overview_section()
    add_historical_section()


def add_daily_overview_section():
    st.subheader("Daily Production / Consumption Overview")
    df = resource_tracking.get_latest_resources()
    df = filter_rows(df)

    if df.empty:
        st.warning("No data to present")
        return

    df = add_daily_production(df)
    df = add_consumption_df(df)
    df = reorder_column(df)

    # Filter out resource TAX for this overview
    df = df.loc[df.token_symbol != "TAX"]

    max_cols = 4
    cols = st.columns(max_cols)
    for idx, (_, row) in enumerate(df.iterrows()):
        col_idx = idx % max_cols

        with cols[col_idx]:
            render_resource_card(row)

    with st.expander("DATA", expanded=False):
        st.dataframe(df, hide_index=True)


def add_historical_section():
    df = resource_tracking.get_historical_data()
    df = filter_rows(df)

    if df.empty:
        st.warning("No data to present")
        return

    df = reorder_column(df)
    df = add_daily_production(df)
    df = add_consumption_df(df)

    # Filter out resource TAX for this overview
    df = df.loc[df.token_symbol != "TAX"]

    st.subheader("1. Total Supply")
    resources_supply_graphs.plot_total_supply(df)

    st.subheader("2. Production vs Consumption")
    resources_supply_graphs.plot_production_vs_consumption(df)

    st.subheader("3. Net Daily Production")
    resources_supply_graphs.plot_net_production(df)

    with st.expander("DATA", expanded=False):
        st.dataframe(df)


def render_resource_card(row):
    token = row['token_symbol']
    daily_production = row['daily_production']
    daily_consumption = row['daily_consumption']
    icon_url = resource_icon_map.get(token, '')
    total_supply = format_large_number(row['total_supply'])

    # Daily consumption (just this row)
    daily_costs = {
        "GRAIN": row["cost_per_h_grain"] * 24,
        "WOOD": row["cost_per_h_wood"] * 24,
        "STONE": row["cost_per_h_stone"] * 24,
        "IRON": row["cost_per_h_iron"] * 24,
    }

    # If resource is WOOD, IRON, or STONE, calculate total consumption across all rows
    extra_consumed = "N/A"
    if token in NATURAL_RESOURCE:
        extra_consumed = format_large_number(daily_consumption)

    with st.container(border=True):
        st.markdown(f"""
        ### <img src="{icon_url}" width="35" style="vertical-align:middle"> {token}
        - **Total Available**: `{total_supply}`
        - **Produced Daily**: `{format_large_number(daily_production)}`
        - **Consumed Daily**: `{extra_consumed}`

        **Consumes:**
        """, unsafe_allow_html=True)

        # Build all resource lines into a single markdown block
        resource_lines = [
            f'<img src="{resource_icon_map[res]}" width="16"> {res}: `{format_large_number(val)}`'
            for res, val in daily_costs.items() if val > 0
        ]
        st.markdown("<br>".join(resource_lines), unsafe_allow_html=True)


def add_daily_production(df):
    df["daily_production"] = df["rewards_per_hour"] * 24
    return df


def add_consumption_df(df):
    consumable_fields = [f'cost_per_h_{resource.lower()}' for resource in NATURAL_RESOURCE]
    # Consumption: per day, sum columns by cost type
    consumption_by_day = df.groupby("date")[consumable_fields].sum() * 24  # multiply after groupby to keep logic clear
    consumption_by_day = consumption_by_day.reset_index()
    # Melt to long format for easier plotting
    cons_melted = consumption_by_day.melt(
        id_vars="date", var_name="resource", value_name="daily_consumption"
    )
    cons_melted["token_symbol"] = cons_melted["resource"].str.replace("cost_per_h_", "").str.upper()
    cons_melted.drop(columns="resource", inplace=True)
    net_df = pd.merge(
        df,
        cons_melted,
        on=["date", "token_symbol"],
        how="outer"
    ).fillna(0)
    net_df["net_production"] = net_df["daily_production"] - net_df["daily_consumption"]

    return net_df


def filter_rows(resource_leaderboard):
    resource_leaderboard = resource_leaderboard[resource_leaderboard["token_symbol"].notnull()]
    return resource_leaderboard
