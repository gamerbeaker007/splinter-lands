import streamlit as st

SORT_OPTIONS = {
    "Region Number": "region_number",
    "Tract Number": "tract_number",
    "Plot Number": "plot_number",
    "RAW PP": "total_base_pp_after_cap",
    "BOOSTED  PP": "total_harvest_pp",
    "Percentage complete": "percentage_done",
}
SORT_KEYS = ["sort_by", "sort_ascending"]


def get_sorting_section(df):
    with st.sidebar:
        with st.expander("## 🔽 Sorting", expanded=False):
            # Defaults
            default_sort_key = "Region Number"
            default_order = "Ascending"

            selected_display = st.selectbox(
                "Sort by",
                options=list(SORT_OPTIONS.keys()),
                index=list(SORT_OPTIONS.keys()).index(
                    st.session_state.get("sort_by", default_sort_key)
                ),
                key="sort_by"
            )

            ascending = st.radio(
                "Order",
                options=["Ascending", "Descending"],
                index=["Ascending", "Descending"].index(
                    st.session_state.get("sort_ascending", default_order)
                ),
                key="sort_ascending"
            )

            sort_column = SORT_OPTIONS[selected_display]
            is_ascending = ascending == "Ascending"

            if sort_column in df.columns:
                df = df.sort_values(by=sort_column, ascending=is_ascending)

            if st.button("🔄 Reset Sorting"):
                reset_sorting()
                st.rerun()

    return df


def reset_sorting():
    for key in SORT_KEYS:
        st.session_state.pop(key, None)
