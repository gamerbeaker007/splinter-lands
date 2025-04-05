import logging
import streamlit as st

FILTER_KEYS = [
    "filter_regions", "filter_tracts", "filter_plots",
    "filter_rarity", "filter_resources", "filter_worksites",
    "filter_deed_type", "filter_plot_status", "filter_players"
]

log = logging.getLogger("filter section")


def apply_filters(df):
    """Apply all filters from session_state to the DataFrame."""
    if st.session_state.get("filter_regions"):
        df = df[df.region_uid.isin(st.session_state["filter_regions"])]
    if st.session_state.get("filter_tracts"):
        df = df[df.tract_number.isin(st.session_state["filter_tracts"])]
    if st.session_state.get("filter_plots"):
        df = df[df.plot_number.isin(st.session_state["filter_plots"])]
    if st.session_state.get("filter_rarity"):
        df = df[df.rarity.isin(st.session_state["filter_rarity"])]
    if st.session_state.get("filter_resources"):
        df = df[df.token_symbol.isin(st.session_state["filter_resources"])]
    if st.session_state.get("filter_worksites"):
        df = df[df.worksite_type.isin(st.session_state["filter_worksites"])]
    if st.session_state.get("filter_deed_type"):
        df = df[df.deed_type.isin(st.session_state["filter_deed_type"])]
    if st.session_state.get("filter_plot_status"):
        df = df[df.plot_status.isin(st.session_state["filter_plot_status"])]
    if st.session_state.get("filter_players"):
        df = df[df.player.isin(st.session_state["filter_players"])]
    return df


def get_page(df):
    filtered_df = df.copy()

    all_regions = df.region_uid.dropna().unique().tolist()
    all_tracts = df.tract_number.dropna().unique().tolist()
    all_plots = df.plot_number.dropna().unique().tolist()
    all_rarity = df.rarity.dropna().unique().tolist()
    all_resources = df.token_symbol.dropna().unique().tolist()
    all_worksites = df[df.worksite_type.notna() & (df.worksite_type != "")].worksite_type.unique().tolist()
    all_deed_type = df.deed_type.dropna().unique().tolist()
    all_plot_status = df.plot_status.dropna().unique().tolist()
    all_players = df.player.dropna().unique().tolist()

    st.markdown("### 🎛️ Filters")
    with st.expander("Location Filters", expanded=False):
        st.multiselect(
            "Regions",
            options=all_regions,
            key="filter_regions",
            default=st.session_state.get("filter_regions", []))
        st.multiselect(
            "Tracts",
            options=all_tracts,
            key="filter_tracts",
            default=st.session_state.get("filter_tracts", []))
        st.multiselect(
            "Plots",
            options=all_plots,
            key="filter_plots",
            default=st.session_state.get("filter_plots", []))

    with st.expander("Attributes",
                     expanded=False):
        st.multiselect(
            "Rarity",
            options=all_rarity,
            key="filter_rarity",
            default=st.session_state.get("filter_rarity", []))
        st.multiselect(
            "Resources",
            options=all_resources,
            key="filter_resources",
            default=st.session_state.get("filter_resources", []))
        st.multiselect(
            "Worksites",
            options=all_worksites,
            key="filter_worksites",
            default=st.session_state.get("filter_worksites", []))
        st.multiselect(
            "Deed Type",
            options=all_deed_type,
            key="filter_deed_type",
            default=st.session_state.get("filter_deed_type", []))
        st.multiselect(
            "Plot Status",
            options=all_plot_status, key="filter_plot_status",
            default=st.session_state.get("filter_plot_status", []))
        st.multiselect(
            "Players",
            options=all_players, key="filter_players",
            default=st.session_state.get("filter_players", []))

    if st.button("🔄 Reset Filters"):
        for key in FILTER_KEYS:
            st.session_state.pop(key, None)
        st.rerun()

    return apply_filters(filtered_df)
