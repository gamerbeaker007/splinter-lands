import numpy as np
import plotly.graph_objects as go
import streamlit as st


color_map = {
    'dec_grain': "orange",
    'dec_iron': "olive",
    'dec_sps': "yellow",
    'dec_stone': "gray",
    'dec_wood': "saddlebrown",
    'dec_aura': "mediumorchid",
}


def add_dec(df):
    df = df.sort_values(by='total_dec', ascending=False)

    dec_columns = [col for col in df.columns if col.startswith("dec_") and col in color_map]

    fig = go.Figure()

    for col in dec_columns:
        # Positive values
        fig.add_trace(go.Bar(
            x=df['player'],
            y=df[col].apply(lambda x: x if x > 0 else 0),
            name=col,
            legendgroup=col,
            marker_color=color_map[col],
            showlegend=True  # only this one shows in legend
        ))

        # Negative values
        fig.add_trace(go.Bar(
            x=df['player'],
            y=df[col].apply(lambda x: x if x < 0 else 0),
            name=col,  # same name
            legendgroup=col,  # same group
            marker_color=color_map[col],
            showlegend=False  # hidden from legend
        ))

    fig.update_layout(
        barmode='relative',
        title='Hourly Earning From Land Resources (resource value converted to DEC)',
        xaxis_title='Player',
        yaxis_title='Hourly DEC'
    )

    st.plotly_chart(fig)


def add_total_dec(df):
    # Second Chart: Sorted Bar
    df_sorted = df.sort_values(by='total_dec', ascending=False)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_sorted['player'],
        y=df_sorted['total_dec'],
        marker=dict(color='steelblue'),
    ))
    fig.update_layout(
        title='Hourly Earning From Land Resource (Resource value converted to DEC)',
        xaxis_title='Player',
        yaxis_title='Total DEC'
    )
    st.plotly_chart(fig)


def add_plots_vs_dec(df):
    fig = go.Figure()

    # Actual bubbles
    fig.add_trace(go.Scatter(
        x=df['count'],
        y=df['total_dec'],
        mode='markers',
        marker=dict(
            size=df['total_harvest_pp'] / 1000000,
            sizemode='area',
            sizeref=2. * max(df['total_harvest_pp'] / 1000000) / (100. ** 2),
            sizemin=4,
            color='steelblue',
            line=dict(width=2, color='white')
        ),
        text=df['player'],
        customdata=df[['total_harvest_pp']],
        hovertemplate="<b>%{text}</b><br>Plots: %{x}<br>Total DEC: %{y}<br>Boosted PP: %{customdata[0]:,.0f}",
        name='Players'
    ))

    # Add fake traces for legend bubbles
    for label, value in zip(['1M', '5M', '10M'], [1_000_000, 5_000_000, 10_000_000]):
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(
                size=value / 100000,
                color='lightgray',
                line=dict(width=2, color='white'),
                sizemode='area',
                sizeref=2. * max(df['total_base_pp_after_cap'] / 1000000) / (100. ** 2),
            ),
            showlegend=True,
            name=f'{label} PP'
        ))

    fig.update_layout(
        title='Bubble Chart: Total Harvest vs Total DEC',
        xaxis_title='Number of Plots',
        yaxis_title='Total DEC'
    )

    st.plotly_chart(fig)


def add_ratio_rank_plot(
    df,
    x_column: str,
    y_column: str,
    highlight_player: str = None,
    title: str = "Ratio vs Rank (Bubble = Base PP)",
    xaxis_title: str = "Ratio",
    yaxis_title: str = "Rank",
    hover_label: str = "Ratio",
    customdata_column: str = "total_base_pp_after_cap"
):
    highlight_enabled = highlight_player in df['player'].values
    if highlight_player and not highlight_enabled:
        st.warning(f"Hive name '{highlight_player}' not found (note only one name can be entered)")

    # Clean up ratio column
    df[x_column] = df[x_column].replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=[x_column])

    # Define fill and border colors
    fill_colors = []
    border_colors = []
    for player in df['player']:
        if not highlight_enabled:
            fill_colors.append('steelblue')
            border_colors.append('white')
        else:
            if player == highlight_player:
                fill_colors.append('red')
                border_colors.append('red')
            else:
                fill_colors.append('rgba(0,0,0,0)')  # Transparent
                border_colors.append('white')

    # Plot setup
    fig = go.Figure()
    size_column = df['total_base_pp_after_cap'] / 1_000_000
    sizeref_val = 2. * max(size_column) / (100. ** 2)

    # Bubble trace
    fig.add_trace(go.Scatter(
        x=df[x_column],
        y=df[y_column],
        mode='markers',
        marker=dict(
            size=size_column,
            sizemode='area',
            sizeref=sizeref_val,
            sizemin=4,
            color=fill_colors,
            line=dict(width=2, color=border_colors)
        ),
        text=df['player'],
        customdata=df[[customdata_column]],
        hovertemplate=f"<b>%{{text}}</b><br>{hover_label}: %{{x:.2f}}<br>Rank: %{{y}}<br>Base PP: %{{customdata[0]:,.0f}}",
        name='Players'
    ))

    # Bubble size legend
    for label, value in zip(['1M', '5M', '10M'], [1_000_000, 5_000_000, 10_000_000]):
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(
                size=value / 100_000,
                color='lightgray',
                line=dict(width=2, color='white'),
                sizemode='area',
                sizeref=sizeref_val,
            ),
            showlegend=True,
            name=f'{label} PP'
        ))

    # Highlight player lines
    if highlight_enabled:
        player_row = df[df['player'] == highlight_player].iloc[0]
        x_val = player_row[x_column]
        y_val = player_row[y_column]

        fig.add_shape(
            type="line",
            x0=x_val, x1=x_val,
            y0=df[y_column].min(), y1=df[y_column].max(),
            line=dict(color="red", width=2, dash="dash"),
            layer="below"
        )

        fig.add_shape(
            type="line",
            x0=df[x_column].min(), x1=df[x_column].max(),
            y0=y_val, y1=y_val,
            line=dict(color="red", width=2, dash="dash"),
            layer="below"
        )

    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
    )

    st.plotly_chart(fig)
