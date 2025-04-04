import logging

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.api import spl
from src.static.static_values_enum import consume_rates, resource_list

log = logging.getLogger("Resource player")

max_cols = 2
tax_rate = 0.9


def get_player_info():
    player = st.text_input("Enter account name for overview")
    if player:
        log.info(f"Request region information for player: {player}")
        deeds, worksite_details, staking_details = spl.get_land_region_details_player(player)

        if worksite_details.empty:
            st.warning(f'No worksites found for player {player}')
        else:
            merged_df = pd.merge(
                worksite_details,
                staking_details,
                how='left',
                on=['region_uid', 'deed_uid'],
                suffixes=('', '_staking_xxx_details')
            )
            grouped_df = merged_df.groupby(["region_uid", 'token_symbol']).agg(
                {'total_harvest_pp': 'sum',
                 'total_base_pp_after_cap': 'sum',
                 'rewards_per_hour': 'sum'}
            ).reset_index()
            return grouped_df
    return pd.DataFrame()


def calc_costs(row):
    resource = row["token_symbol"]
    base = row["base_pp"]
    costs = {f'cost_per_h_{res.lower()}': 0 for res in ['GRAIN', 'WOOD', 'STONE', 'IRON']}

    if resource in {"GRAIN", "WOOD", "STONE", "IRON"}:
        costs['cost_per_h_grain'] = base * consume_rates["GRAIN"]
    elif resource in ["RESEARCH", "SPS"]:
        for dep in ["GRAIN", "WOOD", "STONE", "IRON"]:
            key = f'cost_per_h_{dep.lower()}'
            costs[key] = base * consume_rates[dep]
    return pd.Series(costs)


def color_cell(val):
    color = "green" if val >= 0 else "red"
    return f'<span style="color:{color}">{val:.3f}</span>'


def adjust_fee(val):
    return val * 1.125 if val < 0 else val


def get_price(metrics_df, prices_df, token, amount) -> float:
    if token == 'RESEARCH':
        return 0
    if token == "SPS":
        usd_value = amount * prices_df['sps'].values[0]
        dec_total = usd_value / prices_df['dec'].values[0]
        return dec_total
    print("")
    return amount / metrics_df[metrics_df['token_symbol'] == token]['dec_price'].values[0]


def get_resource_region_overview(metrics_df, prices_df):
    st.markdown("## Region production overview")
    df = get_player_info()

    if df.empty:
        return

    df = df.rename(columns={
        "total_harvest_pp": "boosted_pp",
        "total_base_pp_after_cap": "base_pp",
        "rewards_per_hour": "production_per_hour"
    })

    df = pd.concat([df, df.apply(calc_costs, axis=1)], axis=1)

    produced = df.pivot_table(
        index='region_uid',
        columns='token_symbol',
        values='production_per_hour',
        aggfunc='sum',
        fill_value=0
    ).add_prefix('produced_').reset_index()

    include_taxes = st.checkbox("Include taxes (10%)", value=False)
    if include_taxes:
        produced = produced.set_index('region_uid') * tax_rate
        produced = produced.reset_index()

    cost_cols = [f'cost_per_h_{res.lower()}' for res in ['GRAIN', 'WOOD', 'STONE', 'IRON']]
    cost_df = df.groupby('region_uid')[cost_cols].sum().reset_index()

    # Add taxes
    cost_df = cost_df.rename(columns={
        'cost_per_h_grain': 'cost_grain',
        'cost_per_h_wood': 'cost_wood',
        'cost_per_h_stone': 'cost_stone',
        'cost_per_h_iron': 'cost_iron'
    })

    summary = pd.merge(produced, cost_df, on='region_uid')

    for res in ['GRAIN', 'WOOD', 'STONE', 'IRON', 'RESEARCH', 'SPS']:
        col = f'produced_{res}'
        if col not in summary.columns:
            summary[col] = 0

    summary["net_grain"] = summary["produced_GRAIN"] - summary["cost_grain"]
    summary["net_wood"] = summary["produced_WOOD"] - summary["cost_wood"]
    summary["net_stone"] = summary["produced_STONE"] - summary["cost_stone"]
    summary["net_iron"] = summary["produced_IRON"] - summary["cost_iron"]
    summary["net_research"] = summary["produced_RESEARCH"]
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
            'sps': row["net_research"]
        }

        for key, value in net_vals.items():
            summary.loc[summary['region_uid'] == region, f'adj_net_{key}'] = value

        row_produce = (
            f"| **Produce**  | {row['produced_GRAIN']:.3f} | {row['produced_WOOD']:.3f} | "
            f"{row['produced_STONE']:.3f} | {row['produced_IRON']:.3f} | {row['produced_RESEARCH']:.3f} | "
            f"{row['produced_SPS']:.3f} |"
        )
        row_consume = (
            f"| **Consume**  | -{row['cost_grain']:.3f} | -{row['cost_wood']:.3f} | "
            f"-{row['cost_stone']:.3f} | -{row['cost_iron']:.3f} | 0 | 0 |"
        )
        row_net = (
            f"| **Net**      | {color_cell(net_vals['grain'])} | {color_cell(net_vals['wood'])} | "
            f"{color_cell(net_vals['stone'])} | {color_cell(net_vals['iron'])} | {color_cell(net_vals['research'])} | "
            f"{color_cell(net_vals['sps'])} |"
        )
        markdown = f"""
        ### Region {region}

        |              | GRAIN | WOOD | STONE | IRON | RESEARCH | SPS |
        |--------------|:-----:|:----:|:-----:|:----:|:--------:|:---:|
        {row_produce}
        {row_consume}
        {row_net}
        """
        with cols[col_idx]:
            st.markdown(markdown, unsafe_allow_html=True)

    total_net = {
        key.upper(): summary[f"adj_net_{key}"].sum()
        for key in ['grain', 'wood', 'stone', 'iron', 'research', 'sps']
    }

    row_total_net = (
        f" | **Total Net** | {color_cell(total_net['GRAIN'])} | {color_cell(total_net['WOOD'])} | "
        f"{color_cell(total_net['STONE'])} | {color_cell(total_net['IRON'])} | {color_cell(total_net['RESEARCH'])} | "
        f"{color_cell(total_net['SPS'])} |"
    )

    dec_net = {
        key.upper(): get_price(metrics_df, prices_df, key.upper(), summary[f"adj_net_{key}"].sum())
        for key in ['grain', 'wood', 'stone', 'iron', 'research', 'sps']
    }

    dec_total_net = (
        f" | **Total Net (DEC)** | {color_cell(dec_net['GRAIN'])} | {color_cell(dec_net['WOOD'])} | "
        f"{color_cell(dec_net['STONE'])} | {color_cell(dec_net['IRON'])} | {color_cell(dec_net['RESEARCH'])} | "
        f"{color_cell(dec_net['SPS'])} |"
    )

    markdown_total = f"""
    ### 🌍 Total Net (All Regions)

    |                 | GRAIN | WOOD | STONE | IRON | RESEARCH | SPS |
    |-----------------|:-----:|:----:|:-----:|:----:|:--------:|:---:|
    {row_total_net}
    {dec_total_net}
    """
    st.markdown(markdown_total, unsafe_allow_html=True)

    net_vals = list(dec_net.values())
    net_sum = sum(net_vals)

    # Adjust this number to control how much deficit is acceptable before hitting 0%
    TOLERANCE_DEC = 1000

    # Calculate a score based on acceptable loss
    if net_sum >= 0:
        self_sufficiency_score = 100
    else:
        self_sufficiency_score = max(0, 100 - abs(net_sum) / TOLERANCE_DEC * 100)

    st.markdown(f"## 🧪 Self-Sufficiency Score: **{self_sufficiency_score:.2f}%**")
    st.info("Self-Sufficiency is considered when you can pay the other resources with the excess DEC")

    # Color zones
    color = "green" if self_sufficiency_score > 80 else "orange" if self_sufficiency_score > 50 else "red"

    # Gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=self_sufficiency_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall Self-Sufficiency"},
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
