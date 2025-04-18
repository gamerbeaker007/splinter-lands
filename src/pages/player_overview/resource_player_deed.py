import pandas as pd
import streamlit as st

from src.api import spl
from src.pages.player_overview.components.biome import add_biome, biome_style
from src.pages.player_overview.components.cards import card_display_style, add_card, add_card_runi
from src.pages.player_overview.components.deed_type import add_deed_type, deed_type_style
from src.pages.player_overview.components.items import add_items, item_boost_style

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

.boosts-wrapper {
    display: inline-flex;
    flex-direction: row;
    justify-content: center;
    align-items: flex-start;
    gap: 16px;
    flex-wrap: wrap;
    margin-top: 8px;
}

.cards-wrapper {
    display: inline-flex;
    flex-direction: row;
    justify-content: center;
    align-items: flex-start;
    gap: 1px;
    flex-wrap: wrap;
    margin-top: 8px;
}

.wrapper h6 {
    margin: 6px 0 4px 0;
}

.boost-section {
    text-align: left;
}
</style>
"""

# def create_plot_tile(row):
#     with st.container(border=True):

# st.write(row)

# total_base_pp = row['total_base_pp']
# total_boosted_pp = row['total_harvest_pp']

# add_deed_type(row)

# worksite_type = row['worksite_type']
# if worksite_type == '':
#     worksite_type = 'Undeveloped'
#
# image_url = worksite_type_mapping.get(worksite_type)
# st.write(worksite_type)
# st.image(image_url)

# raw_pp = row['total_base_pp']
# boosted_pp = row['total_harvest_pp']
# extra_style_2 = """style="width: 30px; min-height: 30px" """
# hammer_img = f'<img src="{land_hammer_icon_url}" alt="region" {extra_style_2}>'


def get_page(df: pd.DataFrame):
    st.markdown("## Deed Overview")
    if df.index.size > 100:
        st.warning("To many deeds displaying the first 100 (please use filters)")
        df = df.head(100)

    # df = df.head(3)
    # st.dataframe(df)
    # st.write(df.columns.tolist())
    # filtered_df = df.filter(regex='_y_', axis=1)
    # st.write(filtered_df.columns.tolist())

    # add styles once
    st.markdown(
        deed_tile_wrapper_css +
        deed_type_style +
        biome_style +
        item_boost_style +
        card_display_style,
        unsafe_allow_html=True)

    tiles_html = ""
    for _, row in df.iterrows():
        deed_uid = row['deed_uid']

        asset_info = spl.get_staked_assets(deed_uid)
        items = asset_info['items']
        cards = asset_info['cards']
        items_html = add_items(items)

        card_html = add_deed_type(row)
        biome_html = add_biome(row)
        cards_html = add_card(cards)
        runi_html = add_card_runi(cards)

        tile = f"""<div class="deed-tile">
            {card_html}
            <div class="wrapper">
                <h6 style="margin-bottom: 1px;">Boosts</h6>
                <div class="boosts-wrapper">
                    <div class="boost-section" style="text-align: left;">
                        {biome_html}
                    </div>
                    <div class="boost-section" style="text-align: left;">
                        {items_html}
                    </div>
                    <div class="boost-section" style="text-align: left;">
                        {runi_html}
                    </div>
                </div>
            </div>
            <div class="wrapper">
                <h6 style="margin-bottom: 1px;">Cards</h6>
                <div class="cards-wrapper">
                    <div class="cards-section" style="text-align: left;">
                        {cards_html}
                    </div>
                </div>
            </div>
            <div class="wrapper">
                <h6 style="margin-bottom: 1px;">Production</h6>
                <div class="production-wrapper">
                    <div class="cards-section" style="text-align: left;">
                        <h1>TODO</h1>
                    </div>
                </div>
            </div>
        </div>
        """
        tiles_html += tile

    st.markdown(f'<div class="deed-tile-wrapper">{tiles_html}</div>', unsafe_allow_html=True)
