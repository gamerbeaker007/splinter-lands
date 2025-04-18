import streamlit as st

from src.static.static_values_enum import resource_icon_map
from src.utils.card import create_card, card_style
from src.utils.large_number_util import format_large_number


def get_page(df):
    tokens = df.token_symbol.dropna().unique()

    st.markdown(card_style, unsafe_allow_html=True)
    st.write('Active and inactive based on PP')
    for i in range(0, len(tokens), 4):
        cols = st.columns(4)
        for j, token in enumerate(tokens[i:i + 4]):
            token_df = df[df["token_symbol"] == token]

            total_active_deeds = token_df.loc[token_df.total_harvest_pp > 0]
            active_empty = token_df.loc[(token_df.total_harvest_pp > 0) & (token_df.worksite_type == "")]
            total_boosted_pp = format_large_number(total_active_deeds.total_harvest_pp.sum())
            total_raw_pp = format_large_number(total_active_deeds.total_base_pp_after_cap.sum())

            card_html = create_card(
                token,
                f"Deeds: {token_df.index.size} ({total_active_deeds.index.size} Active)<br>" +
                f"Active w/o Type: {active_empty.index.size}<br>" +
                f"RAW PP: {total_raw_pp}<br>" +
                f"BOOSTED PP: {total_boosted_pp}<br>",
                resource_icon_map.get(token)
            )

            cols[j].markdown(card_html, unsafe_allow_html=True)
