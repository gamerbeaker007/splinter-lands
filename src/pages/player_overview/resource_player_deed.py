import pandas as pd
import streamlit as st

from src.api import spl
from src.static.icons import WEB_URL
from src.static.static_values_enum import worksite_type_mapping, biome_mapper, Edition

BASE_URL = "https://next.splinterlands.com/assets/lands/deedsSurveyed"


def get_card_img(card_name, edition, card_set, foil):
    if foil == 0:
        gold_suffix = "_gold"
    else:
        gold_suffix = ""

    extension = "jpg"
    if (card_set == Edition.untamed.name.lower() or
            card_set == Edition.beta.name.lower() or
            card_set == Edition.alpha.name.lower()):
        extension = 'png'

    if edition == Edition.reward.value and (
            card_set == "alpha" or
            card_set == "beta" or
            card_set == "untamed" or
            card_set == "chaos"):
        edition_name = "beta"
    else:
        edition_name = Edition(edition).name

    card_name = card_name.split(" - ")[0]
    card_name = str(card_name).replace(" ", "%20")
    return f'{WEB_URL}cards_{edition_name}/{card_name}{gold_suffix}.{extension}'


def create_plot_tile(row):
    with st.container(border=True):

        # st.write(row)
        deed_type = row['deed_type'].lower()
        plot_status = row['plot_status'].lower()
        rarity = row['rarity'].lower()
        worksite_type = row['worksite_type']
        if worksite_type == '':
            worksite_type = 'Undeveloped'

        magical_type = row['magic_type']
        total_base_pp = row['total_base_pp']
        total_boosted_pp = row['total_harvest_pp']

        add_biome(row)

        image_url = worksite_type_mapping.get(worksite_type)
        st.write(worksite_type)
        st.image(image_url)

        if magical_type:
            st.image(f'{BASE_URL}/{deed_type}_{plot_status}_{magical_type}_{rarity}.jpg')
        else:
            st.image(f'{BASE_URL}/{deed_type}_{plot_status}_{rarity}.jpg')

        deed_uid = row['deed_uid']
        add_staked_assets(deed_uid, total_base_pp, total_boosted_pp)


def add_staked_assets(deed_uid, total_base_pp, total_boosted_pp):
    asset_info = spl.get_staked_assets(deed_uid)
    if asset_info:
        cards = asset_info['cards']
        add_card_item(cards, total_base_pp, total_boosted_pp)

        items = asset_info['items']
        add_items(items)


def add_card_item(cards, total_base_pp, total_boosted_pp):
    if len(cards) > 0:
        cols = st.columns(len(cards))
        for i, card in enumerate(cards):
            with cols[i]:
                if 'runi' in card['name'].lower():
                    st.write("TODO RUNI")
                else:
                    img = get_card_img(
                        card['name'],
                        card['edition'],
                        card['card_set'],
                        card['foil']
                    )
                    # st.write(row)
                    st.markdown(
                        f"""
                                        <div style="width: 75px; height: 75px;
                                         overflow: hidden;
                                          display: flex;
                                           justify-content: center;
                                            align-items: flex-start;">
                                            <img src="{img}" style="height: auto; width: auto; max-height: none;" />
                                        </div>
                                        <div>
                                            {total_base_pp}/{total_boosted_pp}
                                        </div>
                                        """,
                        unsafe_allow_html=True
                    )


def add_items(items):
    for item in items:
        boost = float(item['boost']) * 100
        if item['stake_type_uid'] == 'STK-LND-TTL':
            st.write(f'{item['name']}')
            name = item['name']
            name = name[4:].lower() if name.lower().startswith('the ') else name.lower()
            name = str(name).replace(" ", "%20")
            img = f'{WEB_URL}website/icons/icon_active_{name}.svg'
            st.markdown(
                f"""
                        <div style="width: 75px;
                        height: 75px;
                         overflow: hidden;
                          display: flex;
                           justify-content: center;
                            align-items: flex-start;">
                            <img src="{img}" style="height: auto; width: auto; max-height: none;" />
                        </div>
                        <div>
                        {boost}
                        </div>
                        """,
                unsafe_allow_html=True
            )

        elif item['stake_type_uid'] == 'STK-LND-TOT':
            st.write(f'{item['name']}')
            name = item['name']
            if name == 'Common Totem':
                name = '1_common'
            elif name == 'Rare Totem':
                name = '1_rare'
            elif name == 'Epic Totem':
                name = '1_epic'
            elif name == 'Legendary Totem':
                name = '1_legendary'
            img = f'{WEB_URL}website/icons/icon_totem_{name.lower()}_300.png'
            st.markdown(
                f"""
                        <div style="width: 75px;
                         height: 75px;
                          overflow: hidden;
                           display: flex;
                            justify-content: center;
                             align-items: flex-start;">
                            <img src="{img}" style="height: auto; width: auto; max-height: none;" />
                        </div>
                        <div>
                        {boost}
                        </div>
                        """,
                unsafe_allow_html=True
            )


def add_biome(row):
    if row['red_biome_modifier'] > 0:
        url = biome_mapper.get('red')
        st.image(url)
        st.write(f'{row['red_biome_modifier'] * 100:0.2f}%')
    if row['blue_biome_modifier'] > 0:
        url = biome_mapper.get('blue')
        st.image(url)
        st.write(f'{row['blue_biome_modifier'] * 100:0.2f}%')
    if row['white_biome_modifier'] > 0:
        url = biome_mapper.get('white')
        st.image(url)
        st.write(f'{row['white_biome_modifier'] * 100:0.2f}%')
    if row['black_biome_modifier'] > 0:
        url = biome_mapper.get('black')
        st.image(url)
        st.write(f'{row['black_biome_modifier'] * 100:0.2f}%')
    if row['green_biome_modifier'] > 0:
        url = biome_mapper.get('green')
        st.image(url)
        st.write(f'{row['green_biome_modifier'] * 100:0.2f}%')
    if row['gold_biome_modifier'] > 0:
        url = biome_mapper.get('gold')
        st.image(url)
        st.write(f'{row['gold_biome_modifier'] * 100:0.2f}%')


def get_page(df: pd.DataFrame):
    st.markdown("## Deed Overview")
    if df.index.size > 100:
        st.warning("To many deeds displaying the first 100 (please use filters)")
        df = df.head(100)

    # st.dataframe(df)
    # st.write(df.columns.tolist())
    # filtered_df = df.filter(regex='_y_', axis=1)
    # st.write(filtered_df.columns.tolist())

    cols = st.columns(3)
    for idx, (_, row) in enumerate(df.iterrows()):
        with cols[idx % 3]:
            create_plot_tile(row)
