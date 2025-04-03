import streamlit as st

from src.static.icons import (
    totem_common_icon_url, totem_rare_icon_url, totem_epic_icon_url, totem_legendary_icon_url,
    title_legendary_icon_url, title_epic_icon_url, title_rare_icon_url,
    deed_rarity_rare_icon_url, deed_rarity_epic_icon_url, deed_rarity_legendary_icon_url
)

RUNI_IMAGE_URL = (
    "https://files.peakd.com/file/peakd-hive/"
    "beaker007/AJiyscF5BsZYHGkTSYAPvbcZjoP1UpBSwuoCD3E9mcrPuAafRgPxNtaq32sETQE.png"
)

default_style = """
<style>
.boost-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
}
.boost-item {
    border: 1px solid #ccc;
    border-radius: 8px;
    padding: 10px;
    text-align: center;
    min-width: 130px;
    max-width: 130px;
    min-height: 150px;
    flex-grow: 1;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
}
.boost-item img {
    max-width: 80px;
    height: auto;
}
</style>
"""

TITLE_BOOST_MAP = {
    10.0: ("Rare", title_rare_icon_url),
    25.0: ("Epic", title_epic_icon_url),
    50.0: ("Legendary", title_legendary_icon_url),
}

TOTEM_BOOST_MAP = {
    10.0: ("Common", totem_common_icon_url),
    25.0: ("Rare", totem_rare_icon_url),
    50.0: ("Epic", totem_epic_icon_url),
    100.0: ("Legendary", totem_legendary_icon_url),
}


DEED_BOOST_MAP = {
    10.0: ("Rare", deed_rarity_rare_icon_url),
    40.0: ("Epic", deed_rarity_epic_icon_url),
    100.0: ("Legendary", deed_rarity_legendary_icon_url),
}


def create_boost_html(image_url, label, boost_pct, count):
    if 'Off' in image_url:
        extra_style = 'style="width: 120px;"'
    else:
        extra_style = ''

    if image_url:
        image_html = f'<img src="{image_url}" alt="{label}" {extra_style}>'
    else:
        image_html = '<div style="font-size: 24px;">❓</div>'

    return f"""
<div class="boost-item">
    {image_html}
    <div><strong>{label}</strong></div>
    <div><strong>Boost: {boost_pct}%</strong></div>
    <div>Count: {count}</div>
</div>
    """


def process_boost_column(df, col_name, boost_map, label_prefix):
    boost_df = df.loc[df[col_name] > 0.0]
    boost_df = boost_df.groupby(col_name).size().reset_index(name='count')

    html_blocks = ""
    for _, row in boost_df.iterrows():
        boost_pct = row[col_name] * 100
        count = row['count']
        text, image_url = boost_map.get(boost_pct, ("?", None))
        label = f"{label_prefix} {text}" if text != "?" else text
        html_blocks += create_boost_html(image_url, label, boost_pct, count)
    return html_blocks


def get_runi_boosts(df):
    runi_boost = df.loc[df.total_runi_boost > 0]
    if runi_boost.empty:
        return ""

    count = len(runi_boost)
    return create_boost_html(RUNI_IMAGE_URL, "Runi", 100, count)


def print_boost(df):
    st.markdown("### Boost Overview")

    total_html = default_style
    total_html += """<div class="boost-grid">"""

    html_blocks = ""
    html_blocks += get_runi_boosts(df)
    html_blocks += process_boost_column(df, 'totem_boost', TOTEM_BOOST_MAP, 'Totem')
    html_blocks += process_boost_column(df, 'title_boost', TITLE_BOOST_MAP, 'Title')
    html_blocks += process_boost_column(df, 'deed_rarity_boost', DEED_BOOST_MAP, 'Deed')

    total_html += html_blocks
    total_html += "</div>"

    st.markdown(total_html, unsafe_allow_html=True)
