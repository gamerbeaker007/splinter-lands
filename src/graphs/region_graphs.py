import plotly.graph_objects as go
import streamlit as st
import plotly.express as px

COLOR_MAP = {
    'GRAIN': "orange",
    'IRON': "olive",
    'RESEARCH': "lightblue",
    'SPS': "yellow",
    'STONE': "gray",
    'WOOD': "saddlebrown",
    'TAX CASTLE': "purple",
    'TAX KEEP': "lightsalmon",
}


def create_land_region_active_graph(df, date_str):
    df = df.copy()

    df = df.sort_values(by='active', ascending=False)

    fig = go.Figure(data=[
        go.Bar(name='Active', x=df['region_uid'], y=df['active']),
        go.Bar(name='Inactive', x=df['region_uid'], y=df['inactive'])
    ])

    # Update layout for stacking
    fig.update_layout(
        barmode='stack',
        title=f'Active vs Inactive Deeds per Region (as of {date_str})',
        xaxis_title='Region UID',
        yaxis_title='Deeds',
        xaxis_tickangle=45,
        legend=dict(x=0.85, y=0.95),
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


def create_pp_per_source_type(df):
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['resource'],
        y=df['total_base_pp_after_cap'],
        name='RAW PP',
        marker=dict(color='steelblue'),
    ))

    fig.add_trace(go.Bar(
        x=df['resource'],
        y=df['total_harvest_pp'],
        name='BOOSTED PP',
        marker=dict(color='lightgray'),
    ))

    fig.update_layout(
        barmode='group',
        yaxis_title="PP",
        xaxis_title="Resource",
        title="PP Comparison by resource",
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("DATA", expanded=False):
        st.dataframe(df, hide_index=True)


def create_land_region_production_sum_graph(df):

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['resource'],
        y=df['total_base_pp_after_cap'],
        name='RAW PP',
        marker=dict(color='steelblue'),
    ))

    fig.add_trace(go.Bar(
        x=df['resource'],
        y=df['total_harvest_pp'],
        name='BOOSTED PP',
        marker=dict(color='lightgray'),
    ))

    fig.update_layout(
        barmode='group',
        yaxis_title="PP",
        xaxis_title="Resource",
        title="Production Power (PP) by resource",
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("DATA", expanded=False):
        st.dataframe(df, hide_index=True)


def create_land_region_historical(df, log_y=True):
    fig = px.line(
        df,
        x="date",
        y="total_harvest_pp",
        log_y=True if log_y else False,
        color="resource",
        title="Resource RAW PP history",
        color_discrete_map=COLOR_MAP,
        labels={"total_harvest_pp": "BOOSTED PP", "date": "Date"},
        hover_data=["resource", "total_harvest_pp"],
        height=600,
    )
    fig.for_each_trace(lambda t: t.update(mode="lines+markers"))

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("DATA", expanded=False):
        st.dataframe(df, hide_index=True)
