import streamlit as st


def get_page(df):
    with st.container(border=True):
        st.subheader("Filter Options:")
        col1, col2, col3 = st.columns(3)
        filtered_all_data = df.copy()
        with col1:
            filter_regions = st.multiselect('Regions', options=filtered_all_data.region_uid.unique().tolist())
            if filter_regions:
                filtered_all_data = filtered_all_data.loc[filtered_all_data.region_uid.isin(filter_regions)]
        with col2:
            filter_tract = st.multiselect('Tracts', options=filtered_all_data.tract_number.unique().tolist())
            if filter_tract:
                filtered_all_data = filtered_all_data.loc[filtered_all_data.tract_number.isin(filter_tract)]
        with col3:
            filter_plot = st.multiselect('Plots', options=filtered_all_data.plot_number.unique().tolist())
            if filter_plot:
                filtered_all_data = filtered_all_data.loc[filtered_all_data.plot_number.isin(filter_plot)]

        col1, col2, col3 = st.columns(3)
        with col1:
            filter_rarity = st.multiselect(
                'Rarity',
                options=filtered_all_data.rarity.unique().tolist()

            )
            if filter_rarity:
                filtered_all_data = filtered_all_data.loc[filtered_all_data.rarity.isin(filter_rarity)]
        with col2:
            filter_resources = st.multiselect(
                'Resources',
                options=filtered_all_data.token_symbol.dropna().unique().tolist()

            )
            if filter_resources:
                filtered_all_data = filtered_all_data.loc[filtered_all_data.token_symbol.isin(filter_resources)]

        with col3:
            worksites_types_list = filtered_all_data[
                filtered_all_data.worksite_type.notna() & (filtered_all_data.worksite_type != "")
                ].worksite_type.unique().tolist()

            filter_worksites = st.multiselect(
                'Worksites',
                options=worksites_types_list

            )
            if filter_worksites:
                filtered_all_data = filtered_all_data.loc[filtered_all_data.worksite_type.isin(filter_worksites)]

        col1, col2, _ = st.columns(3)
        with col1:
            filter_deed_type = st.multiselect('Deed Type', options=filtered_all_data.deed_type.unique().tolist())
            if filter_deed_type:
                filtered_all_data = filtered_all_data.loc[filtered_all_data.deed_type.isin(filter_deed_type)]
        with col2:
            filter_plot_status = st.multiselect('Plot Status', options=filtered_all_data.plot_status.unique().tolist())
            if filter_plot_status:
                filtered_all_data = filtered_all_data.loc[filtered_all_data.plot_status.isin(filter_plot_status)]

    return filtered_all_data
