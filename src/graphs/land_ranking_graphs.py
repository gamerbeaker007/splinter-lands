import streamlit as st
import plotly.graph_objects as go


def add_ranking_barchart(df, player, column_name):
    # Sort by the selected column
    df_sorted = df.sort_values(by=column_name, ascending=False).reset_index(drop=True)

    # Determine rank and stats
    rank = df_sorted[df_sorted['player'] == player].index[0] + 1
    total_players = len(df_sorted)
    max_val = df_sorted[column_name].max()
    selected_val = df_sorted[df_sorted['player'] == player][column_name].values[0]

    # Write ranking info
    st.write(f"**{player}** is placed **#{rank}** out of {total_players} unique owners based on **{column_name}**")

    # Assign base bar colors: blue for selected player, lightgray for others
    base_colors = ['blue' if p == player else 'lightgray' for p in df_sorted['player']]

    # Base bar chart
    base_bar = go.Bar(
        x=df_sorted['player'],
        y=df_sorted[column_name],
        marker=dict(color=base_colors),
        name='Value',
        hoverinfo='x+y'
    )

    # Red overlay bar (stacked) only for selected player
    highlight_y = [max_val - selected_val if p == player else 0 for p in df_sorted['player']]
    highlight_bar = go.Bar(
        x=df_sorted['player'],
        y=highlight_y,
        marker=dict(color='red'),
        name='Gap to Max',
        hoverinfo='skip',
    )

    # Combine bars and configure layout
    fig = go.Figure(data=[base_bar, highlight_bar])
    fig.update_layout(
        barmode='stack',
        title=f"Ranking by {column_name}",
        xaxis_title="Player",
        yaxis_title=f'{column_name} (log)',
        yaxis_type="log",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)
