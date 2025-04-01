import streamlit as st


def get_page(all_region_date_df):
    active_amount = all_region_date_df.loc[all_region_date_df.total_harvest_pp > 0].index.size
    in_use_amount = all_region_date_df.loc[all_region_date_df.in_use].index.size
    st.markdown(f"""
        ### {round((active_amount / 150000) * 100, 2)} % ({active_amount}) Active based on PP.
        ### {round((in_use_amount / 150000) * 100, 2)} % ({in_use_amount}) Active based on in_use state.
        """
    )
