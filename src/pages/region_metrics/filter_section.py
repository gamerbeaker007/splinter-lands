import streamlit as st

from src.utils.log_util import configure_logger

FILTER_KEYS = [
    "filter_regions", "filter_tracts", "filter_plots",
    "filter_rarity", "filter_resources", "filter_worksites",
    "filter_deed_type", "filter_plot_status", "filter_players",
    "filter_developed", "filter_under_construction"
]

log = configure_logger(__name__)


def apply_filters(df):
    df = filter_by_session(df, "filter_regions", "region_uid")
    df = filter_by_session(df, "filter_tracts", "tract_number")
    df = filter_by_session(df, "filter_plots", "plot_number")
    df = filter_by_session(df, "filter_rarity", "rarity")
    df = filter_by_session(df, "filter_resources", "token_symbol")
    df = filter_by_session(df, "filter_worksites", "worksite_type")
    df = filter_by_session(df, "filter_deed_type", "deed_type")
    df = filter_by_session(df, "filter_plot_status", "plot_status")
    df = filter_by_session(df, "filter_players", "player")

    if st.session_state.get("filter_developed"):
        df = df[(df["worksite_type"].isna() | (df["worksite_type"] == ""))]

    if st.session_state.get("filter_under_construction"):
        df = df[df["is_construction_worksite_details"].fillna(False).copy()]

    return df


def filter_by_session(df, session_key, column_name):
    values = st.session_state.get(session_key)
    if values:
        return df[df[column_name].isin(values)]
    return df


def reset_filters():
    for key in FILTER_KEYS:
        st.session_state.pop(key, None)


def get_valid_session_values(key, valid_options):
    """Return only the valid session values that exist in current options."""
    return [v for v in st.session_state.get(key, []) if v in valid_options]


def get_page(df):
    filtered_df = df.copy()

    # Precompute filter options
    all_regions = df.region_uid.dropna().unique().tolist()
    all_tracts = df.tract_number.dropna().unique().tolist()
    all_plots = df.plot_number.dropna().unique().tolist()
    all_rarity = df.rarity.dropna().unique().tolist()
    all_resources = df.token_symbol.dropna().unique().tolist()
    all_worksites = df[df.worksite_type.notna() & (df.worksite_type != "")].worksite_type.unique().tolist()
    all_deed_type = df.deed_type.dropna().unique().tolist()
    all_plot_status = df.plot_status.dropna().unique().tolist()
    all_players = sorted(df.player.dropna().unique().tolist())

    with st.sidebar:
        st.markdown("## 🎛️ Filters")

        with st.expander("📍 Location Filters", expanded=False):
            st.multiselect(
                "Regions",
                options=all_regions,
                key="filter_regions",
                default=get_valid_session_values("filter_regions", all_regions))
            st.multiselect(
                "Tracts",
                options=all_tracts,
                key="filter_tracts",
                default=get_valid_session_values("filter_tracts", all_tracts))
            st.multiselect(
                "Plots",
                options=all_plots,
                key="filter_plots",
                default=get_valid_session_values("filter_plots", all_plots))

        with st.expander("🔎 Attributes", expanded=False):
            st.multiselect(
                "Rarity",
                options=all_rarity,
                key="filter_rarity",
                default=get_valid_session_values("filter_rarity", all_rarity))
            st.multiselect(
                "Resources",
                options=all_resources,
                key="filter_resources",
                default=get_valid_session_values("filter_resources", all_resources))
            st.multiselect(
                "Worksites",
                options=all_worksites,
                key="filter_worksites",
                default=get_valid_session_values("filter_worksites", all_worksites))
            st.multiselect(
                "Deed Type",
                options=all_deed_type,
                key="filter_deed_type",
                default=get_valid_session_values("filter_deed_type", all_deed_type))
            st.multiselect(
                "Plot Status",
                options=all_plot_status,
                key="filter_plot_status",
                default=get_valid_session_values("filter_plot_status", all_plot_status))
            st.checkbox(
                "Undeveloped",
                key="filter_developed",
                value=st.session_state.get("filter_developed", False))
            st.checkbox(
                "Under Construction",
                key="filter_under_construction",
                value=st.session_state.get("filter_under_construction", False))

        with st.expander("🧑 Players", expanded=False):
            st.multiselect(
                "Players",
                options=all_players,
                key="filter_players",
                default=get_valid_session_values("filter_players", all_players))

        if st.button("🔄 Reset Filters"):
            reset_filters()
            st.rerun()

    return apply_filters(filtered_df)
