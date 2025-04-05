import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

COLOR_MAP = {
    "GRAIN": "orange",
    "WOOD": "saddlebrown",  # a nice brown color name
    "STONE": "gray",
    "IRON": "olive"
}


def create_land_resources_dec_graph(df, log_y):
    df = df.copy()
    df['dec_price_1000'] = df['dec_price'] * 1000

    fig = px.line(
        df,
        x="date",
        y="dec_price_1000",
        log_y=True if log_y else False,
        color="token_symbol",
        title="1000 DEC",
        color_discrete_map=COLOR_MAP,
        labels={"dec_price_1000": "Amount of Resource", "date": "Date"},
        hover_data=["token_symbol", "dec_price_1000"],
        height=600,
    )
    fig.for_each_trace(lambda t: t.update(mode="lines+markers"))

    st.plotly_chart(fig, use_container_width=True)


def create_land_resources_graph(df, log_y):
    df = df.copy()
    df['resource_price_1000'] = df['resource_price'] * 1000
    fig = px.line(
        df,
        x="date",
        y="resource_price_1000",
        log_y=True if log_y else False,
        color="token_symbol",
        title="1000 Resources",
        color_discrete_map=COLOR_MAP,
        labels={"resource_price_1000": "Cost in DEC", "date": "Date"},
        hover_data=["token_symbol", "resource_price_1000"],
        height=600,
    )
    fig.for_each_trace(lambda t: t.update(mode="lines+markers"))

    st.plotly_chart(fig, use_container_width=True)


def create_land_resources_factor_graph(df, log_y):
    df['grain_equivalent'] = df['grain_equivalent'].round(3)
    df['factor'] = df['factor'].round(2)
    df_filtered = df[df['token_symbol'].isin(['WOOD', 'STONE', 'IRON'])].copy()

    fig = px.line(
        df_filtered,
        x="date",
        y="factor",
        log_y=True if log_y else False,
        color="token_symbol",
        title="Grain factor",
        color_discrete_map=COLOR_MAP,
        labels={"factor": "Factor", "date": "Date"},
        hover_data=["token_symbol", "factor"],
        height=600,
    )
    fig.add_hline(
        y=1.00,
        line_dash="dash",
        line_color="gray",
        annotation_text="1.00 (Grain baseline)",
        annotation_position="top left"
    )

    fig.for_each_trace(lambda t: t.update(mode="lines+markers"))

    st.plotly_chart(fig, use_container_width=True)


def create_active_graph(df, height):
    df["date"] = pd.to_datetime(df["date"])  # Ensure datetime type

    # Calculate percentage
    total = 150_000
    df["pp_percentage"] = (df["active_based_on_pp"] / total) * 100

    fig = go.Figure()

    # First Y-axis traces
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["active_based_on_pp"],
        mode='lines+markers',
        name='Active Based on PP',
        yaxis='y1'
    ))

    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["active_based_on_in_use"],
        mode='lines+markers',
        name='Active Based on in_use state',
        yaxis='y1'
    ))

    # Second Y-axis trace (percentage)
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["pp_percentage"],
        mode='lines+markers',
        name='Active % (Based on PP)',
        yaxis='y2',
        line=dict(dash='dot'),
    ))

    fig.update_layout(
        title='Active Land (Based on PP)',
        xaxis=dict(title='Date'),
        yaxis=dict(
            title='Count',
            side='left'
        ),
        yaxis2=dict(
            title='PP %',
            overlaying='y',
            showgrid=False,
            zeroline=False,
            side='right',
            tickformat=".1f",
            range=[0, 100]
        ),
        height=height,
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        )

    )

    st.plotly_chart(fig, use_container_width=True)
