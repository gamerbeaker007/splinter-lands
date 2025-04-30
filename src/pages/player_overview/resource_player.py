import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.static.static_values_enum import PRODUCING_RESOURCES, NATURAL_RESOURCE
from src.utils.log_util import configure_logger
from src.utils.resource_util import calc_costs, get_price

log = configure_logger(__name__)

max_cols = 2
tax_rate = 0.9


def color_cell(val):
    color = "green" if val >= 0 else "red"
    return f'<span style="color:{color}">{val:.3f}</span>'


def adjust_fee(val):
    return val * 1.125 if val < 0 else val


def prepare_data(df):
    grouped_df = df.groupby(["region_uid", 'token_symbol']).agg(
        {'total_harvest_pp': 'sum',
         'total_base_pp_after_cap': 'sum',
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


def get_resource_region_overview(df, player, metrics_df, prices_df):
    st.markdown("## Region production overview")

    df = prepare_data(df)

    if df.empty:
        return

    df = pd.concat([df, df.apply(calc_costs, axis=1)], axis=1)
    amount_df = df[['region_uid', 'token_symbol', 'count']]

    produced = df.pivot_table(
        index='region_uid',
        columns='token_symbol',
        values='rewards_per_hour',
        aggfunc='sum',
        fill_value=0
    ).add_prefix('produced_').reset_index()

    include_taxes = st.checkbox("Include taxes (10%)", value=False)
    if include_taxes:
        produced = produced.set_index('region_uid') * tax_rate
        produced = produced.reset_index()

    cost_cols = [f'cost_per_h_{res.lower()}' for res in NATURAL_RESOURCE]
    cost_df = df.groupby('region_uid')[cost_cols].sum().reset_index()

    summary = pd.merge(produced, cost_df, on='region_uid')

    for res in PRODUCING_RESOURCES:
        col = f'produced_{res}'
        if col not in summary.columns:
            summary[col] = 0

    summary["net_grain"] = summary["produced_GRAIN"] - summary["cost_per_h_grain"]
    summary["net_wood"] = summary["produced_WOOD"] - summary["cost_per_h_wood"]
    summary["net_stone"] = summary["produced_STONE"] - summary["cost_per_h_stone"]
    summary["net_iron"] = summary["produced_IRON"] - summary["cost_per_h_iron"]
    summary["net_research"] = summary["produced_RESEARCH"]
    summary["net_aura"] = summary["produced_AURA"]
    summary["net_sps"] = summary["produced_SPS"]

    include_fee = st.checkbox("Include transfer fees(12.5%)", value=False)

    cols = st.columns(max_cols)
    for idx, (_, row) in enumerate(summary.iterrows()):
        col_idx = idx % max_cols
        region = row["region_uid"]

        net_vals = {
            'grain': adjust_fee(row["net_grain"]) if include_fee else row["net_grain"],
            'wood': adjust_fee(row["net_wood"]) if include_fee else row["net_wood"],
            'stone': adjust_fee(row["net_stone"]) if include_fee else row["net_stone"],
            'iron': adjust_fee(row["net_iron"]) if include_fee else row["net_iron"],
            'research': row["net_research"],
            'aura': row["net_aura"],
            'sps': row["net_sps"]
        }

        for key, value in net_vals.items():
            summary.loc[summary['region_uid'] == region, f'adj_net_{key}'] = value

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
            f"| **Net**      | {color_cell(net_vals['grain'])} | {color_cell(net_vals['wood'])} | "
            f"{color_cell(net_vals['stone'])} | {color_cell(net_vals['iron'])} | {color_cell(net_vals['research'])} | "
            f"{color_cell(net_vals['aura'])} | {color_cell(net_vals['sps'])} |"
        )

        # Filter for current region
        region_df = amount_df[amount_df['region_uid'] == region]

        # Build the markdown header with counts
        header_row = "|              |"
        sub_header_row = "|--------------|"
        for res in PRODUCING_RESOURCES:
            count = region_df[region_df['token_symbol'] == res]['count'].sum()
            header_row += f" {res} ({count}) |"
            sub_header_row += ":----:|"

        markdown = f"""
        ### Region {region}

        {header_row}
        {sub_header_row}
        {row_produce}
        {row_consume}
        {row_net}
        """
        with cols[col_idx]:
            with st.container():
                st.markdown(markdown, unsafe_allow_html=True)

    dec_net = total_section(amount_df, metrics_df, prices_df, summary)

    add_self_sufficiency(dec_net, player)


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


def total_section(amount_df, metrics_df, prices_df, summary):
    total_net = {
        key.lower(): summary[f"adj_net_{key.lower()}"].sum()
        for key in PRODUCING_RESOURCES
    }
    row_total_net = (
        f" | **Total Net** | {color_cell(total_net['grain'])} | {color_cell(total_net['wood'])} | "
        f"{color_cell(total_net['stone'])} | {color_cell(total_net['iron'])} | {color_cell(total_net['research'])} | "
        f"{color_cell(total_net['aura'])} | {color_cell(total_net['sps'])} |"
    )
    dec_net = {
        key.lower(): get_price(metrics_df, prices_df, key, summary[f"adj_net_{key.lower()}"].sum())
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
