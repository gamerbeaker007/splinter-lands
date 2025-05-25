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
    HAS_PP = "filter_has_pp"


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

    if FilterKey.HAS_PP in filters and st.session_state.get(FilterKey.HAS_PP.value):
        df = df[df["total_harvest_pp"] > 0]

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


def render_location_filters(df, only):
    if only is None or any(k in only for k in [FilterKey.REGIONS, FilterKey.TRACTS, FilterKey.PLOTS]):
        all_regions = df.region_uid.dropna().unique().tolist()
        all_tracts = df.tract_number.dropna().unique().tolist()
        all_plots = df.plot_number.dropna().unique().tolist()

        with st.expander("📍 Location Filters", expanded=False):
            if only is None or FilterKey.REGIONS in only:
                st.multiselect("Regions", options=all_regions,
                               key="filter_regions",
                               default=get_valid_session_values("filter_regions", all_regions))
            if only is None or FilterKey.TRACTS in only:
                st.multiselect("Tracts", options=all_tracts,
                               key="filter_tracts",
                               default=get_valid_session_values("filter_tracts", all_tracts))
            if only is None or FilterKey.PLOTS in only:
                st.multiselect("Plots", options=all_plots,
                               key="filter_plots",
                               default=get_valid_session_values("filter_plots", all_plots))


def render_attribute_filters(df, only):
    if only is None or any(k in only for k in [
        FilterKey.RARITY, FilterKey.RESOURCES, FilterKey.WORKSITES,
        FilterKey.DEED_TYPE, FilterKey.PLOT_STATUS,
        FilterKey.DEVELOPED, FilterKey.UNDER_CONSTRUCTION,
        FilterKey.HAS_PP,
    ]):
        all_rarity = df.rarity.dropna().unique().tolist()
        all_resources = df.token_symbol.dropna().unique().tolist()
        all_worksites = df[df.worksite_type.notna() & (df.worksite_type != "")].worksite_type.unique().tolist()
        all_deed_type = df.deed_type.dropna().unique().tolist()
        all_plot_status = df.plot_status.dropna().unique().tolist()

        with st.expander("🔎 Attributes", expanded=False):
            if only is None or FilterKey.RARITY in only:
                st.multiselect("Rarity", options=all_rarity,
                               key="filter_rarity",
                               default=get_valid_session_values("filter_rarity", all_rarity))
            if only is None or FilterKey.RESOURCES in only:
                st.multiselect("Resources", options=all_resources,
                               key="filter_resources",
                               default=get_valid_session_values("filter_resources", all_resources))
            if only is None or FilterKey.WORKSITES in only:
                st.multiselect("Worksites", options=all_worksites,
                               key="filter_worksites",
                               default=get_valid_session_values("filter_worksites", all_worksites))
            if only is None or FilterKey.DEED_TYPE in only:
                st.multiselect("Deed Type", options=all_deed_type,
                               key="filter_deed_type",
                               default=get_valid_session_values("filter_deed_type", all_deed_type))
            if only is None or FilterKey.PLOT_STATUS in only:
                st.multiselect("Plot Status", options=all_plot_status,
                               key="filter_plot_status",
                               default=get_valid_session_values("filter_plot_status", all_plot_status))
            if only is None or FilterKey.DEVELOPED in only:
                st.checkbox("Undeveloped", key="filter_developed",
                            value=st.session_state.get("filter_developed", False))
            if only is None or FilterKey.UNDER_CONSTRUCTION in only:
                st.checkbox("Under Construction", key="filter_under_construction",
                            value=st.session_state.get("filter_under_construction", False))
            if only is None or FilterKey.HAS_PP in only:
                st.checkbox("Has PP", key="filter_has_pp",
                            value=st.session_state.get("filter_has_pp", False))


def render_player_filters(df, only):
    if only is None or FilterKey.PLAYERS in only:
        all_players = sorted(df.player.dropna().unique().tolist())
        with st.expander("🧑 Players", expanded=False):
            if only is None or FilterKey.PLAYERS in only:
                st.multiselect("Players", options=all_players,
                               key="filter_players",
                               default=get_valid_session_values("filter_players", all_players))


def get_page(df, only: list[FilterKey] | None = None):
    filtered_df = df.copy()

    with st.sidebar:
        st.markdown("## 🎛️ Filters")

        render_location_filters(df, only)
        render_attribute_filters(df, only)
        render_player_filters(df, only)

        if st.button("🔄 Reset Filters"):
            reset_filters()
            st.rerun()

    return apply_filters(filtered_df, only=only)
