import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.static.static_values_enum import PRODUCING_RESOURCES, NATURAL_RESOURCE
from src.utils.log_util import configure_logger
from src.utils.resource_util import calc_costs, get_price

log = configure_logger(__name__)

max_cols = 2
tax_rate = 0.9


def get_resource_region_overview(df, player, metrics_df, prices_df):
    st.markdown("## Region production overview")

    df = prepare_data(df)
    if df.empty:
        return

    if 'include_taxes' not in st.session_state:
        st.session_state.include_taxes = True

    if 'include_fee' not in st.session_state:
        st.session_state.include_fee = True

    st.session_state.include_taxes = st.checkbox(
        "Include taxes (10%)",
        value=st.session_state.include_taxes,
        help="10% Taxes are deducted from the produced amount",
        key="region_overview_taxes"
    )
    st.session_state.include_fee = st.checkbox(
        "Include transfer fees (10%)",
        help="Negative DEC resources include a 10% fee to cover transfer costs.",
        value=st.session_state.include_fee
    )

    summary_df = prepare_summary(df, st.session_state.include_taxes, st.session_state.include_fee)
    amount_df = df[['region_uid', 'token_symbol', 'count']]

    render_regions(summary_df, amount_df)

    dec_net = total_section(summary_df, amount_df, metrics_df, prices_df)
    add_self_sufficiency(dec_net, player)


def prepare_data(df):
    grouped_df = df.groupby(["region_uid", 'token_symbol']).agg(
        {'total_harvest_pp': 'sum',
         'total_base_pp_after_cap': 'sum',
         'total_dec_stake_needed': 'sum',
         'total_dec_stake_in_use': 'sum',
         'total_dec_staked': 'first',
         'rewards_per_hour': 'sum'}
    ).reset_index()

    # Count token_symbols per region_uid
    token_counts = (
        df.groupby(['region_uid', 'token_symbol'])
        .agg(count=('token_symbol', 'count'))
        .reset_index()
    )

    # Merge that count back in if you want it alongside the main data
    grouped_df = grouped_df.merge(token_counts, on=["region_uid", 'token_symbol'], how='left')
    return grouped_df


def prepare_summary(df, include_taxes, include_fee):
    df = pd.concat([df, df.apply(calc_costs, axis=1)], axis=1)

    produced = df.pivot_table(
        index='region_uid',
        columns='token_symbol',
        values='rewards_per_hour',
        aggfunc='sum',
        fill_value=0
    ).add_prefix('produced_').reset_index()

    if include_taxes:
        produced = produced.set_index('region_uid') * tax_rate
        produced = produced.reset_index()

    cost_cols = [f'cost_per_h_{res.lower()}' for res in NATURAL_RESOURCE]
    cost_df = df.groupby('region_uid')[cost_cols].sum().reset_index()

    summary = pd.merge(produced, cost_df, on='region_uid')

    # Ensure all columns exist
    for res in PRODUCING_RESOURCES:
        col = f'produced_{res}'
        if col not in summary.columns:
            summary[col] = 0

    # Net calculations
    summary["net_grain"] = summary["produced_GRAIN"] - summary["cost_per_h_grain"]
    summary["net_wood"] = summary["produced_WOOD"] - summary["cost_per_h_wood"]
    summary["net_stone"] = summary["produced_STONE"] - summary["cost_per_h_stone"]
    summary["net_iron"] = summary["produced_IRON"] - summary["cost_per_h_iron"]
    summary["net_research"] = summary["produced_RESEARCH"]
    summary["net_aura"] = summary["produced_AURA"]
    summary["net_sps"] = summary["produced_SPS"]

    # Adjusted net values
    if include_fee:
        summary["adj_net_grain"] = summary["net_grain"].apply(adjust_fee)
        summary["adj_net_wood"] = summary["net_wood"].apply(adjust_fee)
        summary["adj_net_stone"] = summary["net_stone"].apply(adjust_fee)
        summary["adj_net_iron"] = summary["net_iron"].apply(adjust_fee)
    else:
        summary["adj_net_grain"] = summary["net_grain"]
        summary["adj_net_wood"] = summary["net_wood"]
        summary["adj_net_stone"] = summary["net_stone"]
        summary["adj_net_iron"] = summary["net_iron"]

    summary["adj_net_research"] = summary["net_research"]
    summary["adj_net_aura"] = summary["net_aura"]
    summary["adj_net_sps"] = summary["net_sps"]

    return summary


def color_cell(val):
    color = "green" if val >= 0 else "red"
    return f'<span style="color:{color}">{val:.3f}</span>'


def adjust_fee(val):
    return val * 1.10 if val < 0 else val


def build_region_markdown(row, region_df):
    region = row["region_uid"]

    # Count per resource
    region_counts = region_df.groupby("token_symbol")["count"].sum().to_dict()

    header_row = "|              |"
    sub_header_row = "|--------------|"
    for res in PRODUCING_RESOURCES:
        count = region_counts.get(res, 0)
        header_row += f" {res} ({count}) |"
        sub_header_row += ":----:|"

    row_produce = (
        f"| **Produce**  | {row['produced_GRAIN']:.3f} | {row['produced_WOOD']:.3f} | "
        f"{row['produced_STONE']:.3f} | {row['produced_IRON']:.3f} | {row['produced_RESEARCH']:.3f} | "
        f"{row['produced_AURA']:.3f} | {row['produced_SPS']:.3f} |"
    )
    row_consume = (
        f"| **Consume**  | -{row['cost_per_h_grain']:.3f} | -{row['cost_per_h_wood']:.3f} | "
        f"-{row['cost_per_h_stone']:.3f} | -{row['cost_per_h_iron']:.3f} | 0 | 0 | 0 | "
    )
    row_net = (
        f"| **Net**      | {color_cell(row['adj_net_grain'])} | {color_cell(row['adj_net_wood'])} | "
        f"{color_cell(row['adj_net_stone'])} | {color_cell(row['adj_net_iron'])} | "
        f"{color_cell(row['adj_net_research'])} | {color_cell(row['adj_net_aura'])} | "
        f"{color_cell(row['adj_net_sps'])} |"
    )

    return f"""
    ### Region {region}

    {header_row}
    {sub_header_row}
    {row_produce}
    {row_consume}
    {row_net}
    """


def render_regions(summary, amount_df):
    cols = st.columns(max_cols)
    for idx, row in summary.iterrows():
        region = row["region_uid"]
        region_df = amount_df[amount_df['region_uid'] == region]
        markdown = build_region_markdown(row, region_df)
        with cols[idx % max_cols]:
            with st.container():
                st.markdown(markdown, unsafe_allow_html=True)


def add_self_sufficiency(dec_net, player):
    net_vals = list(dec_net.values())
    net_sum = sum(net_vals)
    total_activity = sum(abs(v) for v in net_vals)
    if net_sum >= 0:
        self_sufficiency_score = 100
    elif total_activity == 0:
        self_sufficiency_score = 0  # Edge case: all zeros
    else:
        imbalance_ratio = abs(net_sum) / total_activity
        self_sufficiency_score = max(0, 100 - imbalance_ratio * 100)
    st.markdown(f"## 🧪 Self-Sufficiency Score: **{self_sufficiency_score:.2f}%**")
    st.info("Self-Sufficiency is considered when you can pay the other resources with the excess DEC")
    # Color zones
    color = "green" if self_sufficiency_score > 80 else "orange" if self_sufficiency_score > 50 else "red"
    # Gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=self_sufficiency_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Overall Self-Sufficiency for {player}"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 50], 'color': "rgba(255,0,0,0.3)"},
                {'range': [50, 80], 'color': "rgba(255,165,0,0.3)"},
                {'range': [80, 100], 'color': "rgba(0,255,0,0.3)"}
            ]
        }
    ))
    st.plotly_chart(fig, use_container_width=True)


def total_section(summary_df, amount_df, metrics_df, prices_df):
    total_net = {
        key.lower(): summary_df[f"adj_net_{key.lower()}"].sum()
        for key in PRODUCING_RESOURCES
    }
    row_total_net = (
        f" | **Total Net** | {color_cell(total_net['grain'])} | {color_cell(total_net['wood'])} | "
        f"{color_cell(total_net['stone'])} | {color_cell(total_net['iron'])} | {color_cell(total_net['research'])} | "
        f"{color_cell(total_net['aura'])} | {color_cell(total_net['sps'])} |"
    )
    dec_net = {
        key.lower(): get_price(metrics_df, prices_df, key, summary_df[f"adj_net_{key.lower()}"].sum())
        for key in PRODUCING_RESOURCES
    }
    dec_total_net = (
        f" | **Total Net (DEC)** | {color_cell(dec_net['grain'])} | {color_cell(dec_net['wood'])} | "
        f"{color_cell(dec_net['stone'])} | {color_cell(dec_net['iron'])} | {color_cell(dec_net['research'])} | "
        f"{color_cell(dec_net['aura'])} | {color_cell(dec_net['sps'])} |"
    )
    # Build the markdown header with counts
    header_row = "|              |"
    sub_header_row = "|--------------|"
    for res in PRODUCING_RESOURCES:
        count = amount_df[amount_df['token_symbol'] == res]['count'].sum()
        header_row += f" {res} ({count}) |"
        sub_header_row += ":-----:|"
    markdown_total = f"""
    ### 🌍 Total Net (All Regions)

    {header_row}
    {sub_header_row}
    {row_total_net}
    {dec_total_net}
    """
    st.markdown(markdown_total, unsafe_allow_html=True)
    return dec_net
