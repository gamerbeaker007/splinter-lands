import pandas as pd
import streamlit as st

from src.api import spl
from src.static.static_values_enum import worksite_type_mapping, biome_mapper

BASE_URL = "https://next.splinterlands.com/assets/lands/deedsSurveyed"


def create_plot_tile(row):
    # st.write(row)
    deed_type = row['deed_type'].lower()
    plot_status = row['plot_status'].lower()
    rarity = row['rarity'].lower()
    worksite_type = row['worksite_type']
    if worksite_type == '':
        worksite_type = 'Undeveloped'

    if row['red_biome_modifier'] > 0:
        url = biome_mapper.get('red')
        st.image(url)
    if row['blue_biome_modifier'] > 0:
        url = biome_mapper.get('blue')
        st.image(url)
    if row['white_biome_modifier'] > 0:
        url = biome_mapper.get('white')
        st.image(url)
    if row['black_biome_modifier'] > 0:
        url = biome_mapper.get('black')
        st.image(url)
    if row['green_biome_modifier'] > 0:
        url = biome_mapper.get('green')
        st.image(url)
    if row['gold_biome_modifier'] > 0:
        url = biome_mapper.get('gold')
        st.image(url)

    image_url = worksite_type_mapping.get(worksite_type)
    st.write(worksite_type)
    st.image(image_url)
    st.image(f'{BASE_URL}/{deed_type}_{plot_status}_{rarity}.jpg')

    deed_uid = row['deed_uid']
    asset_info = spl.get_staked_assets(deed_uid)
    if asset_info:
        for card in asset_info['cards']:
            st.write(card['name'])
    # st.write(asset_info)


def get_page(df: pd.DataFrame):
    st.markdown("## Deed Overview")
    # st.dataframe(df)
    # st.write(df.columns.tolist())
    # filtered_df = df.filter(regex='_y_', axis=1)
    # st.write(filtered_df.columns.tolist())

    cols = st.columns(3)
    for idx, (_, row) in enumerate(df.iterrows()):
        with cols[idx % 3]:
            create_plot_tile(row)
