import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.static.static_values_enum import PRODUCING_RESOURCES, RESOURCE_COLOR_MAP, \
    NATURAL_RESOURCE


def plot_total_supply(df):
    supply_fig = px.line(
        df,
        x="date",
        y="total_supply",
        color="token_symbol",
        color_discrete_map=RESOURCE_COLOR_MAP,
        log_y=True,
        title="Total Supply per Token (Log Scale)"
    )
    supply_fig.for_each_trace(lambda t: t.update(mode="lines+markers"))

    st.plotly_chart(supply_fig, use_container_width=True)


def plot_production_vs_consumption(df):
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Daily Production per Token", "Daily Consumption per Resource"),
        shared_yaxes=True
    )

    # --- Left Plot: Production ---
    for token in PRODUCING_RESOURCES:
        token_prod = df[df["token_symbol"] == token]
        fig.add_trace(
            go.Scatter(
                x=token_prod["date"],
                y=token_prod["daily_production"],
                mode="lines+markers",
                name=f"{token} Production",
                line=dict(color=RESOURCE_COLOR_MAP.get(token, "blue"))
            ),
            row=1, col=1
        )

    # --- Right Plot: Consumption ---
    for token in NATURAL_RESOURCE:
        token_cons = df[df["token_symbol"] == token]
        fig.add_trace(
            go.Scatter(
                x=token_cons["date"],
                y=token_cons["daily_consumption"],
                mode="lines+markers",
                name=f"{token} Consumption",
                line=dict(color=RESOURCE_COLOR_MAP[token], dash="dot")
            ),
            row=1, col=2
        )

    fig.update_layout(
        title_text="Daily Production vs Consumption (Log Scale)",
        yaxis_type="log",
        xaxis_title="Date",
        height=500,
        legend_title="Metric",
        showlegend=True
    )
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_xaxes(title_text="Date", row=1, col=2)
    fig.update_yaxes(title_text="Amount", type="log", row=1, col=1)
    fig.update_yaxes(title_text="Amount", type="log", row=1, col=2)

    st.plotly_chart(fig, use_container_width=True)


def plot_net_production(net_df):
    fig_net = go.Figure()
    for token in NATURAL_RESOURCE:
        token_net = net_df[net_df["token_symbol"] == token]
        fig_net.add_trace(go.Bar(
            x=token_net["date"],
            y=token_net["net_production"],
            name=token,
            marker_color=RESOURCE_COLOR_MAP[token]
        ))

    fig_net.update_layout(
        title="Net Daily Production (Production - Consumption)",
        xaxis_title="Date",
        yaxis_title="Net Production",
        barmode="group"
    )
    st.plotly_chart(fig_net, use_container_width=True)
