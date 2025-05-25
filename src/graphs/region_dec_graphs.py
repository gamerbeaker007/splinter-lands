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
            size=df['total_harvest_pp'] / 100000,
            sizemode='area',
            sizeref=2. * max(df['total_harvest_pp'] / 100000) / (100. ** 2),
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
    for label, value in zip(['10M', '40M', '100M'], [10_000_000, 40_000_000, 100_000_000]):
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(
                size=value / 100000,
                color='steelblue',
                line=dict(width=2, color='white'),
                sizemode='area',
                sizeref=2. * max(df['total_harvest_pp'] / 100000) / (100. ** 2),
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
