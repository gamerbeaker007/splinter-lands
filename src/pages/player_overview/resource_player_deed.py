import pandas as pd
import streamlit as st

from src.api import spl
from src.pages.player_overview.components.biome import add_biome_boosts, biome_style
from src.pages.player_overview.components.cards import card_display_style, add_card, add_card_runi
from src.pages.player_overview.components.deed_type import add_deed_type, deed_type_style
from src.pages.player_overview.components.deed_type_boost import add_deed_type_boost
from src.pages.player_overview.components.items import add_items, item_boost_style
from src.pages.player_overview.components.production import add_production, production_card_style
from src.pages.player_overview.components.rarity import add_rarity_boost

deed_tile_wrapper_css = """
<style>
.deed-tile-wrapper {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
}

.deed-tile {
    border: 1px solid white;
    border-radius: 15px;
    padding: 10px;
    display: flex;
    flex-direction: column;
}

.info-wrapper {
    display: inline-flex;
    flex-direction: row;
    justify-content: center;
    align-items: flex-start;
    gap: 5px;
    flex-wrap: wrap;
    margin-top: 1px;
    min-height: 150px;
}

.wrapper p {
    margin-top: 5px;
    margin-bottom: 0px;
    font-size: 14pt;
    font-weight: bold;
}

.boost-section {
    text-align: left;
}
</style>
"""


def get_player_deed_overview(df: pd.DataFrame):
    st.markdown(f"## Deed Overview ({df.index.size})")

    if 'include_taxes_deeds' not in st.session_state:
        st.session_state.include_taxes_deeds = True

    st.session_state.include_taxes_deeds = st.checkbox(
        "Include taxes (10%)",
        value=st.session_state.include_taxes,
        key="deed_overview_taxes"
    )

    if df.index.size > 100:
        st.warning("To many deeds displaying the first 100 (please use filters)")
        df = df.head(100)

    # add styles once
    st.markdown(
        deed_tile_wrapper_css +
        deed_type_style +
        biome_style +
        item_boost_style +
        card_display_style +
        production_card_style,
        unsafe_allow_html=True)

    tiles_html = ""
    for _, row in df.iterrows():
        deed_uid = row['deed_uid']
        total_boost = row['total_boost']
        deed_type = row['deed_type']

        card_html = add_deed_type(row)
        production_html = add_production(row, st.session_state.include_taxes_deeds)
        if deed_type == 'Unsurveyed Deed':
            total_boost = 0
            biome_html = 'N/A'
            items_html = '<div></div>'
            rarity_html = '<div></div>'
            deed_type_html = '<div></div>'
            cards_html = 'N/A'
            runi_html = '<div></div>'

        else:
            if pd.isna(total_boost):
                total_boost = 0
            total_boost = int(float(total_boost) * 100)

            biome_html = add_biome_boosts(row)

            asset_info = spl.get_staked_assets(deed_uid)
            items = asset_info['items']
            cards = asset_info['cards']
            items_html = add_items(items)

            rarity_html = add_rarity_boost(row)
            deed_type_html = add_deed_type_boost(row)
            cards_html = add_card(cards)
            runi_html = add_card_runi(cards)

        tile = f"""<div class="deed-tile">
            {card_html}
            <div class="wrapper">
                <div>Boosts: <span style='color:gray'>({total_boost}%)</span><br></div>
                <div class="info-wrapper">
                    <div class="boost-section" style="text-align: left;">
                        {biome_html}
                    </div>
                    <div class="boost-section" style="text-align: left;">
                        {items_html}
                    </div>
                    <div class="boost-section" style="text-align: left;">
                        {rarity_html}
                    </div>
                    <div class="boost-section" style="text-align: left;">
                        {deed_type_html}
                    </div>
                    <div class="boost-section" style="text-align: left;">
                        {runi_html}
                    </div>
                </div>
            </div>
            <div class="wrapper">
                <p>Cards:</p>
                <div class="info-wrapper">
                    <div class="cards-section" style="text-align: left;">
                        {cards_html}
                    </div>
                </div>
            </div>
            <div class="wrapper">
                <p>Production:</p>
                <div class="info-wrapper">
                    <div class="production-section" style="text-align: left;">
                        {production_html}
                    </div>
                </div>
            </div>
        </div>
        """
        tiles_html += tile

    st.markdown(f'<div class="deed-tile-wrapper">{tiles_html}</div>', unsafe_allow_html=True)
