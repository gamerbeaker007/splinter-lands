import streamlit as st

from src.graphs import resources_graphs

burn_rate = 0.05  # 10% trade fee 5% for providers and 5% burned


def add_section(df):
    st.title("Trade Hub information")
    st.write("""
    Welcome to the Trade Hub Insights page!

    Here’s what you’ll find:
    - **Chart 1:** Daily DEC burned across all resource pools, along with a cumulative burn line for context.
    - **Chart 2:** 24-hour trade volume for each individual resource pool.
    - **Chart 3:** Total DEC burned per day across all pools

    💡 The DEC burn is estimated as 5% of the 24h trade volume per resource.
    """)

    st.warning("""
    ⚠️ DEC Burn Disclaimer
    
    This chart shows estimated cumulative DEC burned,
    based on daily snapshots of a 24-hour rolling trade volume. \n
    Snapshots are taken once per day,
    but the exact timing and update frequency of the source data are unknown.\n
    As a result, some short-term activity may be missed,
    and totals should be treated as indicative rather than exact.""")

    df["dec_burned"] = df["dec_volume_1"] * burn_rate

    daily_df = df.groupby("date").agg(
        dec_volume_1=("dec_volume_1", "sum"),
        dec_burned=("dec_burned", "sum")
    ).reset_index()

    # Add cumulative burned
    daily_df["cumulative_burn"] = daily_df["dec_burned"].cumsum()

    resources_graphs.add_trade_hub_daily_graphs(daily_df)
    resources_graphs.add_trade_hub_volume_graph(df)
    resources_graphs.add_trade_hub_dec_burned(df)

    with st.expander("DATA", expanded=False):
        st.dataframe(df, hide_index=True)
