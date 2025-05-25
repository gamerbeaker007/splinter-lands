from enum import Enum

import streamlit as st

from src.utils.log_util import configure_logger


class FilterKey(str, Enum):
    REGIONS = "filter_regions"
    TRACTS = "filter_tracts"
    PLOTS = "filter_plots"
    RARITY = "filter_rarity"
    RESOURCES = "filter_resources"
    WORKSITES = "filter_worksites"
    DEED_TYPE = "filter_deed_type"
    PLOT_STATUS = "filter_plot_status"
    PLAYERS = "filter_players"
    DEVELOPED = "filter_developed"
    UNDER_CONSTRUCTION = "filter_under_construction"

# Mapping of filter keys to column names
SESSION_FILTER_COLUMNS = {
    FilterKey.REGIONS: "region_uid",
    FilterKey.TRACTS: "tract_number",
    FilterKey.PLOTS: "plot_number",
    FilterKey.RARITY: "rarity",
    FilterKey.RESOURCES: "token_symbol",
    FilterKey.WORKSITES: "worksite_type",
    FilterKey.DEED_TYPE: "deed_type",
    FilterKey.PLOT_STATUS: "plot_status",
    FilterKey.PLAYERS: "player",
}

log = configure_logger(__name__)


def apply_filters(df, only: list[FilterKey] | None = None):
    filters = set(only) if only is not None else set(FilterKey)

    for key, column in SESSION_FILTER_COLUMNS.items():
        if key in filters:
            df = filter_by_session(df, key.value, column)

    if FilterKey.DEVELOPED in filters and st.session_state.get(FilterKey.DEVELOPED.value):
        df = df[(df["worksite_type"].isna() | (df["worksite_type"] == ""))]

    if FilterKey.UNDER_CONSTRUCTION in filters and st.session_state.get(FilterKey.UNDER_CONSTRUCTION.value):
        df = df[df["is_construction_worksite_details"].fillna(False)]

    return df


def filter_by_session(df, session_key, column_name):
    values = st.session_state.get(session_key)
    if values:
        return df[df[column_name].isin(values)]
    return df


def reset_filters():
    for key in FilterKey:
        st.session_state.pop(key.value, None)


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
