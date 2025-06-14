import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.static.static_values_enum import RESOURCE_COLOR_MAP
from src.utils.resource_util import reorder_column


def create_land_region_active_graph(df, date_str, group_by_label):
    df = df.copy()
    df = df.sort_values(by='active', ascending=False)

    fig = go.Figure(data=[
        go.Bar(name='Active', x=df[group_by_label], y=df['active']),
        go.Bar(name='Inactive', x=df[group_by_label], y=df['inactive'])
    ])

    fig.update_layout(
        barmode='stack',
        title=f'Active vs Inactive Deeds per {"Tract" if "tract" in group_by_label else "Region"} '
              f'(as of {date_str.strftime("%Y-%m-%d %H:%M:%S")})',
        xaxis_title=group_by_label.replace("_", " ").title(),
        yaxis_title='Deeds',
        xaxis_tickangle=45,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        )
    )

    st.plotly_chart(fig, theme="streamlit")

    with st.expander("DATA", expanded=False):
        st.dataframe(df, hide_index=True)


def create_land_region_production_graph(df, selected_resource):
    raw_col = f"{selected_resource}_raw_pp"
    boosted_col = f"{selected_resource}_boosted_pp"

    plot_df = df[["region_uid", raw_col, boosted_col]].copy()
    plot_df = plot_df.sort_values(by=boosted_col, ascending=False)

    # --- Step 4: Plotly horizontal bar chart ---
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=plot_df["region_uid"],
        x=plot_df[raw_col],
        name='Raw PP',
        orientation='h',
        marker=dict(color='steelblue'),
        offsetgroup=0
    ))

    fig.add_trace(go.Bar(
        y=plot_df["region_uid"],
        x=plot_df[boosted_col],
        name='Boosted PP',
        orientation='h',
        marker=dict(color='lightgray'),
        offsetgroup=1
    ))

    fig.update_layout(
        title=f"{selected_resource.capitalize()} Production per Region",
        barmode='group',
        yaxis=dict(autorange="reversed"),  # So highest is on top
        xaxis_title="Production Points (PP)",
        height=400 + len(plot_df) * 20  # Adjust height based on number of regions
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("DATA", expanded=False):
        st.dataframe(df, hide_index=True)


def create_total_production_power(df):
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['Type'],
        y=df['Total PP'],
        name='RAW PP',
        marker=dict(color=['steelblue', 'lightgray'])
    ))

    fig.update_layout(
        barmode='group',
        yaxis_title="PP",
        xaxis_title="Resource",
        title="Total PP",
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("DATA"):
        st.dataframe(df)


def create_pp_per_source_type(df, key=None, title=None, slim=False):
    fig = go.Figure()

    # Create a mapping from resource to order index
    df = reorder_column(df, column='resource')

    fig.add_trace(go.Bar(
        x=df['resource'],
        y=df['total_base_pp_after_cap'],
        name='RAW PP',
        marker=dict(
            color=[RESOURCE_COLOR_MAP.get(res, 'steelblue') for res in df['resource']]
        ),
    ))

    fig.add_trace(go.Scatter(
        x=df['resource'],
        y=df['total_harvest_pp'],
        name='BOOSTED PP',
        mode='lines',
        marker=dict(color='lightgray'),
    ))

    plot_title = "PP Comparison by resource"
    if title:
        plot_title = f'{title}'

    fig.update_layout(
        barmode='group',
        yaxis_title="PP",
        xaxis_title="Resource",
        title=plot_title,
        showlegend=False if slim else True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        )

    )

    st.plotly_chart(fig, use_container_width=True, key=key)

    if not slim:
        with st.expander("DATA", expanded=False):
            st.dataframe(df, hide_index=True)


def create_land_region_historical(df, log_y=True):
    fig = px.line(
        df,
        x="date",
        y="total_harvest_pp",
        log_y=True if log_y else False,
        color="resource",
        title="Resource BOOSTED PP history",
        color_discrete_map=RESOURCE_COLOR_MAP,
        labels={"total_harvest_pp": "BOOSTED PP", "date": "Date"},
        hover_data=["resource", "total_harvest_pp"],
        height=600,
    )
    fig.for_each_trace(lambda t: t.update(mode="lines+markers"))

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("DATA", expanded=False):
        st.dataframe(df, hide_index=True)


def create_tax_income_chart(df, title):
    df = reorder_column(df)

    fig = go.Figure(
        data=[
            go.Bar(
                x=df["token_symbol"],
                y=df["tax_income"],
                marker=dict(color=[RESOURCE_COLOR_MAP.get(res, 'steelblue') for res in df["token_symbol"]])
            )
        ]
    )

    fig.update_layout(
        title=title,
        xaxis_title="Token Symbol",
        yaxis_title="Tax Income",
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        )
    )

    st.plotly_chart(fig, use_container_width=True, key=title)
