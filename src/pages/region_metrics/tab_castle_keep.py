import streamlit as st

from src.graphs.region_graphs import create_tax_income_chart
from src.static.icons import land_keep_icon_url, land_castle_icon_url

MAX_PLOTS = 10


def get_page(df):
    st.markdown("### Castle / Keep Overview")
    df_filtered = df[
        [
            'player',
            'region_uid',
            'region_number',
            'tract_number',
            'plot_number',
            'captured_tax_rate',
            'max_tax_rate',
            'tax_rate',
            'worksite_type',
            'token_symbol',
            'rewards_per_hour'
        ]
    ].copy()

    keeps_and_castles = df_filtered[df_filtered['worksite_type'].isin(['CASTLE', 'KEEP'])]
    add_top_taxes(keeps_and_castles)

    # Calculate taxed income for each plot (10% of rewards_per_hour)
    df_filtered['paid_taxes'] = df_filtered['rewards_per_hour'].astype(float) * df_filtered['tax_rate'].astype(float)

    all_resources = df_filtered[df_filtered['token_symbol'] != 'TAX']

    keeps_df = df_filtered[df_filtered['worksite_type'] == 'KEEP']
    add_keep_income(keeps_df, all_resources)

    castle_df = df_filtered[df_filtered['worksite_type'] == 'CASTLE']
    add_castle_income(castle_df, all_resources)


def add_castle_income(castles_df, all_resources):
    # Group all materials by region and tract to calculate total rewards per tract
    region_income = all_resources.groupby(['region_uid', 'token_symbol'])[
        'paid_taxes'].sum().reset_index()
    merged = region_income.merge(
        castles_df[
            [
                'player',
                'tax_rate',
                "region_uid",
                'tract_number',
                'plot_number'
            ]
        ],
        on="region_uid",
        how="left"
    )
    merged['tax_income'] = merged['paid_taxes'].astype(float) * merged['tax_rate'].astype(float)
    # drop the castle where no tax income (probably no castles in selection)
    merged = merged[merged["tax_income"].notna()]
    create_tax_income_per_type(merged, "CASTLE")
    with st.expander("DATA", expanded=False):
        st.dataframe(merged)


def add_keep_income(keeps_df, all_resources):
    # Group all materials by region and tract to calculate total rewards per tract
    tract_income = all_resources.groupby(['region_uid', 'tract_number', 'token_symbol'])[
        'paid_taxes'].sum().reset_index()

    merged = tract_income.merge(
        keeps_df[
            [
                'player',
                'tax_rate',
                "region_uid",
                'tract_number',
                'plot_number'
            ]
        ],
        on=["region_uid", 'tract_number'],
        how="left"
    )

    merged['tax_income'] = merged['paid_taxes'].astype(float) * merged['tax_rate'].astype(float)
    # drop the keep where no tax income (this is the castle)
    merged = merged[merged["tax_income"].notna()]

    create_tax_income_per_type(merged, "KEEP")
    with st.expander("DATA", expanded=False):
        st.dataframe(merged)


def create_tax_income_per_type(merged, keep_castle):
    st.title(f"Tax {keep_castle} Income")
    if merged.empty:
        st.warning(f"No {keep_castle} found with current filter")
        return

    unique_regions = merged["region_uid"].nunique()
    unique_tracts = merged["tract_number"].nunique()

    # Prepare list of (title, grouped_df)
    plot_data = []

    if unique_regions > MAX_PLOTS:
        summary_df = merged.groupby("token_symbol", as_index=False)["tax_income"].sum()
        plot_data.append(("Overall Tax Income", summary_df))
    elif unique_regions > 1:
        grouped = merged.groupby(["region_uid", "token_symbol"], as_index=False)["tax_income"].sum()
        for region, group_df in grouped.groupby("region_uid"):
            plot_data.append((f"Region {region}", group_df))
    elif unique_tracts > 1:
        grouped = merged.groupby(["tract_number", "token_symbol"], as_index=False)["tax_income"].sum()
        for tract, group_df in grouped.groupby("tract_number"):
            plot_data.append((f"Tract {tract}", group_df))
    else:
        summary_df = merged.groupby("token_symbol", as_index=False)["tax_income"].sum()
        plot_data.append(("Overall Tax Income", summary_df))

    # Limit to max 10 plots
    if len(plot_data) > MAX_PLOTS:
        st.warning(f"Limited to {MAX_PLOTS} Charts (filter selection)")
    plot_data = plot_data[:MAX_PLOTS]

    # Create 3 Streamlit columns
    cols = st.columns(3)

    for idx, (title, df) in enumerate(plot_data):
        with cols[idx % 3]:
            create_tax_income_chart(df, title=f'{title} ({keep_castle})')


def render_top_tax_list(df, label):
    df = df[df['worksite_type'] == label].copy()
    df['tax_rate'] = df['tax_rate'].astype(float) * 100
    df = df.sort_values(by='tax_rate', ascending=False).head(10)

    html = "<div style='line-height:1.6;'>"
    for idx, row in enumerate(df.itertuples(), start=1):
        html += (
            f"<strong>{idx}.</strong> "
            f"{row.tax_rate:.2f}% "
            f"<span style='color:gray'>"
            f"({row.player} / {row.region_uid}-{row.tract_number}-{row.plot_number})"
            f"</span><br>"
        )
    html += "</div>"
    return html


def add_top_taxes(df_filtered):

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"<h4><img src='{land_keep_icon_url}' style='height:1.5em;vertical-align:middle;margin-right:0.5em;'>"
            "Top 10 Highest Tax Rates - KEEPS</h4>",
            unsafe_allow_html=True
        )
        st.markdown(render_top_tax_list(df_filtered, "KEEP"), unsafe_allow_html=True)

    with col2:
        st.markdown(
            f"<h4><img src='{land_castle_icon_url}' style='height:1.5em;vertical-align:middle;margin-right:0.5em;'>"
            "Top 10 Highest Tax Rates - CASTLES</h4>",
            unsafe_allow_html=True
        )
        st.markdown(render_top_tax_list(df_filtered, "CASTLE"), unsafe_allow_html=True)

    return df_filtered
