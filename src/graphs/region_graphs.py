import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def create_land_region_active_graph(df, date_str):
    df = df.copy()
    df['inactive'] = 1000 - df['active']

    # Step 4: Sort by active ascending
    df = df.sort_values(by='active', ascending=False)

    # Step 5: Create the stacked bar chart
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
        marker_color='steelblue',
        offsetgroup=0
    ))

    fig.add_trace(go.Bar(
        y=plot_df["region_uid"],
        x=plot_df[boosted_col],
        name='Boosted PP',
        orientation='h',
        marker_color='orange',
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


def create_land_region_production_sum_graph(df, date_str):
    # 1. Prepare non-tax data
    none_tax_df = df[df.token_symbol != 'TAX']
    grouped_non_tax = none_tax_df.groupby('token_symbol').agg({
        'total_harvest_pp': 'sum',
        'total_base_pp_after_cap': 'sum'
    }).reset_index()
    grouped_non_tax['resource'] = grouped_non_tax['token_symbol']

    # 2. Prepare tax data (split by worksite_type)
    tax_df = df[df.token_symbol == 'TAX']
    grouped_tax = tax_df.groupby('worksite_type').agg({
        'total_harvest_pp': 'sum',
        'total_base_pp_after_cap': 'sum'
    }).reset_index()
    grouped_tax['resource'] = 'TAX ' + grouped_tax['worksite_type'].str.replace('TAX ', '', regex=False)

    # 3. Combine both
    combined_df = pd.concat([
        grouped_non_tax[['resource', 'total_harvest_pp', 'total_base_pp_after_cap']],
        grouped_tax[['resource', 'total_harvest_pp', 'total_base_pp_after_cap']]
    ], ignore_index=True)

    # 4. Convert to millions
    combined_df['total_harvest_pp_m'] = combined_df['total_harvest_pp'] / 1_000_000
    combined_df['total_base_pp_after_cap_m'] = combined_df['total_base_pp_after_cap'] / 1_000_000

    # 5. Plot
    st.write('Active and inactive based on PP')

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=combined_df['resource'],
        y=combined_df['total_base_pp_after_cap_m'],
        name='RAW PP (M)',
        marker_color='steelblue',
    ))

    fig.add_trace(go.Bar(
        x=combined_df['resource'],
        y=combined_df['total_harvest_pp_m'],
        name='BOOSTED PP (M)',
        marker_color='lightgray',
    ))

    fig.update_layout(
        barmode='group',
        yaxis_title="PP (in Millions)",
        xaxis_title="Resource / Worksite",
        title="PP Comparison by Token and Worksite",
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("DATA", expanded=False):
        st.dataframe(combined_df, hide_index=True)
