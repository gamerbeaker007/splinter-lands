import pandas as pd
import streamlit as st

from src.graphs.region_dec_graphs import add_total_dec, add_plots_vs_dec, add_dec, add_ratio_rank_plot
from src.utils.log_util import configure_logger

log = configure_logger(__name__)


# Define display -> column mapping
metric_options = {
    "Amount of Plots": "count",
    "Base PP": "total_base_pp_after_cap",
    "Boosted PP": "total_harvest_pp"
}

limit_options = {
    "Top 100": 100,
    "Top 500": 500,
    "Top 1000": 1000,
    "All (Warning: might slow charts too much)": None
}


def filter_top(df):
    # Initialize session state
    if "selected_metric" not in st.session_state:
        st.session_state.selected_metric = "Amount of Plots"
    if "selected_limit" not in st.session_state:
        st.session_state.selected_limit = "Top 500"

    col1, col2 = st.columns([1, 3])
    with col1:
        # Metric selector
        selected_metric = st.selectbox(
            "Select metric to sort by:",
            options=list(metric_options.keys()),
            index=list(metric_options.keys()).index(st.session_state.selected_metric),
        )
        st.session_state.selected_metric = selected_metric
    with col2:
        # Limit selector
        selected_limit = st.radio(
            "Select number of top entries:",
            options=list(limit_options.keys()),
            index=list(limit_options.keys()).index(st.session_state.selected_limit),
            horizontal=True,
        )
        st.session_state.selected_limit = selected_limit

    metric_col = metric_options[selected_metric]
    limit_val = limit_options[selected_limit]

    sorted_df = df.sort_values(by=metric_col, ascending=False)
    if limit_val is not None:
        sorted_df = sorted_df.head(limit_val)

    return sorted_df


def add_ratios(df):
    df['LCE_ratio_base'] = df.total_base_pp_after_cap / df.total_dec
    df['LCE_ratio_boosted'] = df.total_harvest_pp / df.total_dec
    df['LCE_base_rank'] = df['LCE_ratio_base'].rank(method='min', ascending=False).astype(int)
    df['LCE_boosted_rank'] = df['LCE_ratio_boosted'].rank(method='min', ascending=False).astype(int)
    df['LPE_ratio'] = df.total_dec / df['count']
    df['LPE_rank'] = df['LPE_ratio'].rank(method='min', ascending=False).astype(int)
    df['LDE_ratio'] = df.total_dec_stake_in_use / (df.total_dec * 24)
    df['LDE_rank'] = df['LDE_ratio'].rank(method='min', ascending=False).astype(int)
    df['total_dec_rank'] = df['total_dec'].rank(ascending=False, method='min').astype(int)
    df['count_rank'] = df['count'].rank(ascending=False, method='min').astype(int)
    df['total_harvest_pp_rank'] = df['total_harvest_pp'].rank(ascending=False, method='min').astype(int)
    return df


def add_leaderboard_section(df, player_name=None):
    # Define leaderboards with renamed columns
    leaderboards = {
        "DEC/hr": df[['total_dec_rank', 'player', 'total_dec']]
        .sort_values(by='total_dec', ascending=False)
        .head(200)
        .rename(columns={'total_dec_rank': 'Rank', 'player': 'Player', 'total_dec': 'DEC/hr'}),

        "Active Plots": df[['count_rank', 'player', 'count']]
        .sort_values(by='count', ascending=False)
        .head(200)
        .rename(columns={'count_rank': 'Rank', 'player': 'Player', 'count': 'Active Plots'}),

        "Boosted PP": df[['total_harvest_pp_rank', 'player', 'total_harvest_pp']]
        .sort_values(by='total_harvest_pp', ascending=False)
        .head(200)
        .rename(columns={'total_harvest_pp_rank': 'Rank', 'player': 'Player', 'total_harvest_pp': 'BOOSTED PP'}),

        "LCE Boosted PP": df[['LCE_boosted_rank', 'player', 'LCE_ratio_boosted']]
        .sort_values(by='LCE_ratio_boosted', ascending=False)
        .head(200)
        .rename(columns={'LCE_boosted_rank': 'Rank', 'player': 'Player', 'LCE_ratio_boosted': 'LCE'}),

        "LPE": df[['LPE_rank', 'player', 'LPE_ratio']]
        .sort_values(by='LPE_ratio', ascending=False)
        .head(200)
        .rename(columns={'LPE_rank': 'Rank', 'player': 'Player', 'LPE_ratio': 'LPE'}),

        "LDE": df[['LDE_rank', 'player', 'LDE_ratio']]
        .sort_values(by='LDE_ratio', ascending=False)
        .head(200)
        .rename(columns={'LDE_rank': 'Rank', 'player': 'Player', 'LDE_ratio': 'LDE'}),
    }

    # Layout: 2 rows with 3 columns each
    layout = [
        st.columns(3),  # First row
        st.columns(3)  # Second row
    ]

    titles = list(leaderboards.keys())

    for i, title in enumerate(titles):
        row = layout[i // 3]
        col = row[i % 3]

        with col:
            st.markdown(f"### {title}")
            data = leaderboards[title]
            player_row = df[df['player'].str.lower() == player_name] if player_name else pd.DataFrame()

            if not player_row.empty:
                player_data = player_row.iloc[0]

                if title == "DEC/hr":
                    value = player_data['total_dec']
                    rank = player_data['total_dec_rank']
                    st.markdown(f"<h5 style='color:red;'>{player_data['player']} DEC: {value:,.2f} (Rank #{rank})</h5>",
                                unsafe_allow_html=True)
                elif title == "Active Plots":
                    value = player_data['count']
                    rank = player_data['count_rank']
                    st.markdown(
                        f"<h5 style='color:red;'>{player_data['player']} Active Plots: {value:.0f} (Rank #{rank})</h5>",
                        unsafe_allow_html=True)
                elif title == "Boosted PP":
                    value = player_data['total_harvest_pp']
                    rank = player_data['total_harvest_pp_rank']
                    st.markdown(
                        f"<h5 style='color:red;'>{player_data['player']} BOOSTED PP: {value:,.0f} (Rank #{rank})</h5>",
                        unsafe_allow_html=True)
                elif title == "LCE Boosted PP":
                    value = player_data['LCE_ratio_boosted']
                    rank = player_data['LCE_boosted_rank']
                    st.markdown(f"<h5 style='color:red;'>{player_data['player']} LCE: {value:.2f} (Rank #{rank})</h5>",
                                unsafe_allow_html=True)
                elif title == "LPE":
                    value = player_data['LPE_ratio']
                    rank = player_data['LPE_rank']
                    st.markdown(f"<h5 style='color:red;'>{player_data['player']} LPE: {value:.2f} (Rank #{rank})</h5>",
                                unsafe_allow_html=True)
                elif title == "LDE":
                    value = player_data['LDE_ratio']
                    rank = player_data['LDE_rank']
                    st.markdown(f"<h5 style='color:red;'>{player_data['player']} LDE: {value:.2f} (Rank #{rank})</h5>",
                                unsafe_allow_html=True)

            st.dataframe(data.reset_index(drop=True), hide_index=True, width=300)


def get_page(total_df):
    total_df = add_ratios(total_df)

    player_name = st.text_input("Enter hive name to highlight")
    st.title("Leaderboards (Top 200)")
    add_leaderboard_section(total_df, player_name)

    st.title("Charts")
    df = filter_top(total_df)

    tab1, tab2, tab3, tab4 = st.tabs([
        "DEC",
        "LCE",
        "LPE",
        "LDE"
    ])
    with tab1:
        add_dec(df)
        add_total_dec(df)
        add_plots_vs_dec(df)
    with tab2:
        st.info("Land Card Efficiency (LCE) = Total PP Employed (Boosted PP) / Total DEC earned per hour")

        add_ratio_rank_plot(
            df,
            x_column='LCE_ratio_boosted',
            y_column='LCE_boosted_rank',
            highlight_player=player_name,
            title='LCE Ratio vs Rank (Bubble = Boosted PP)',
            xaxis_title='LCE_ratio_boosted',
            yaxis_title='LCE_boosted_rank',
            hover_label='LCE_boosted',
            customdata_column='total_base_pp_after_cap'
        )
    with tab3:

        st.info("Land Plot Efficiency (LPE) = Total DEC earned per hour / Number of Active Plots")

        add_ratio_rank_plot(
            df,
            x_column='LPE_ratio',
            y_column='LPE_rank',
            highlight_player=player_name,
            title='LPE Ratio vs Rank (Bubble = Base PP)',
            xaxis_title='LPE_ratio',
            yaxis_title='LPE_rank',
            hover_label='LPE_ratio',
            customdata_column='total_base_pp_after_cap'
        )
        add_ratio_rank_plot(
            df,
            x_column='count',
            y_column='total_dec',
            highlight_player=player_name,
            title='DEC generated per hour (Bubble = Base PP)',
            xaxis_title='Amount of Plots',
            yaxis_title='Total DEC',
            hover_label='DEC',
            customdata_column='total_base_pp_after_cap'
        )
    with tab4:
        st.info("Land DEC Efficiency (LDE) = Total DEC Staked in Use / (DEC earned per hour * 24)")

        add_ratio_rank_plot(
            df,
            x_column='LDE_ratio',
            y_column='LDE_rank',
            highlight_player=player_name,
            title='LDE Ratio vs Rank (Bubble = Base PP)',
            xaxis_title='LDE_ratio',
            yaxis_title='LDE_rank',
            hover_label='LDE_ratio',
            customdata_column='total_base_pp_after_cap'
        )

    with st.expander("DATA", expanded=False):
        st.dataframe(total_df)
