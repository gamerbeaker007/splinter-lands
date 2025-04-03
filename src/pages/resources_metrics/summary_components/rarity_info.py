import pandas as pd
import streamlit as st

from src.static.icons import SPL_WEB_URL

rarity_order = ['common', 'rare', 'epic', 'legendary', 'mythic']


def print_rarity(df):
    rarities = df['rarity'].value_counts().reset_index()
    rarities['rarity_cat'] = pd.Categorical(rarities['rarity'], categories=rarity_order, ordered=True)
    rarities = rarities.sort_values('rarity_cat')

    st.markdown("### Rarity Overview")
    total_html = """
        <style>
        .rarity-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
        }
        .rarity-item {
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            min-width: 100px;
            max-width: 120px;
            flex-grow: 1;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        }
        .rarity-item img {
            max-width: 60px;
            height: auto;
        }
        </style>
        """

    html_blocks = ""
    for _, row in rarities.iterrows():
        rarity = row['rarity']
        count = row['count']

        path = "assets/lands/sideMenu/"
        extra_style = """style="width: 50px; min-height: 50px" """

        if rarity == 'Unknown':
            image_html = '<div style="font-size: 30px;">❓</div>'
        elif rarity == 'mythic':
            image_html = f"""<img src="{SPL_WEB_URL}{path}legendaryOff.svg" alt="{rarity}" {extra_style}>"""
        else:
            image_html = f"""<img src="{SPL_WEB_URL}{path}{rarity.lower()}Off.svg" alt="{rarity}" {extra_style}>"""

        html_blocks += f"""
        <div class="rarity-item">
            {image_html}
            <div><strong>{rarity.title()}</strong></div>
            <div>Count: {count}</div>
        </div>
        """

    total_html += """<div class="rarity-grid">"""
    total_html += html_blocks
    total_html += "</div>"
    st.markdown(total_html, unsafe_allow_html=True)
