import streamlit as st

from src.static.icons import totem_common_icon_url, totem_rare_icon_url, totem_epic_icon_url, \
    totem_legendary_icon_url, title_legendary_icon_url, title_epic_icon_url, title_rare_icon_url, \
    deed_rarity_rare_icon_url, deed_rarity_epic_icon_url, deed_rarity_legendary_icon_url

RUNI_IMAGE_URL = ("https://files.peakd.com/file/peakd-hive/"
                  "beaker007/AJiyscF5BsZYHGkTSYAPvbcZjoP1UpBSwuoCD3E9mcrPuAafRgPxNtaq32sETQE.png")

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


def print_boost(df):
    st.markdown("### Boost Overview")

    total_html = default_style
    total_html += """<div class="boost-grid">"""

    html_blocks = get_runi_boosts(df)
    html_blocks += get_totem_boosts(df)
    html_blocks += get_title_boosts(df)
    html_blocks += get_deed_rarity_boosts(df)

    total_html += html_blocks
    total_html += "</div>"

    st.markdown(total_html, unsafe_allow_html=True)


def get_runi_boosts(df):
    runi_boost = df.loc[df.total_runi_boost > 0]
    runi_boost = runi_boost.groupby('total_runi_boost').size().reset_index(name='count')
    image_html = f'<img src="{RUNI_IMAGE_URL}" alt="Runi">'
    html_blocks = ""
    html_blocks += f"""
    <div class="boost-item">
        {image_html}
        <div><strong>Runi</strong></div>
        <div><strong>Boost: 100%</strong></div>
        <div>Count: {runi_boost['count'].iloc[0]}</div>
    </div>
    """
    return html_blocks


def get_title_boosts(df):
    title_boost = df.loc[df.title_boost > 0]
    title_boost = title_boost.groupby('title_boost').size().reset_index(name='count')
    html_blocks = ""
    for _, row in title_boost.iterrows():
        title_boost_pct = row['title_boost'] * 100
        count = row['count']

        image_url = None
        if title_boost_pct == 10.0:
            text = "Rare"
            image_url = title_rare_icon_url
        elif title_boost_pct == 25.0:
            text = "Epic"
            image_url = title_epic_icon_url
        elif title_boost_pct == 50.0:
            text = "Legendary"
            image_url = title_legendary_icon_url
        else:
            text = "?"
            image_html = '<div style="font-size: 24px;">❓</div>'

        if image_url:
            image_html = f'<img src="{image_url}" alt="{title_boost_pct}">'

        html_blocks += f"""
<div class="boost-item">
    {image_html}
    <div><strong>{text}</strong></div>
    <div><strong>Boost: {title_boost_pct}%</strong></div>
    <div>Count: {count}</div>
</div>
"""
    return html_blocks


def get_totem_boosts(df):
    # df['total_title_boost'] = pd.to_numeric(df['total_title_boost'], errors='coerce')
    totem_boosts = df.loc[df['totem_boost'] > 0.0]
    totem_boosts = totem_boosts.groupby('totem_boost').size().reset_index(name='count')
    html_blocks = ""
    for _, row in totem_boosts.iterrows():
        totem_boost_pct = row['totem_boost'] * 100
        count = row['count']

        image_url = None
        if totem_boost_pct == 10.0:
            text = "Common"
            image_url = totem_common_icon_url
        elif totem_boost_pct == 25.0:
            text = "Rare"
            image_url = totem_rare_icon_url
        elif totem_boost_pct == 50.0:
            text = "Epic"
            image_url = totem_epic_icon_url
        elif totem_boost_pct == 100.0:
            text = "Legendary"
            image_url = totem_legendary_icon_url
        else:
            text = "?"
            image_html = '<div style="font-size: 24px;">❓</div>'

        if image_url:
            image_html = f'<img src="{image_url}" alt="{totem_boost_pct}">'

        html_blocks += f"""
<div class="boost-item">
    {image_html}
    <div><strong>{text}</strong></div>
    <div><strong>Boost: {totem_boost_pct}%</strong></div>
    <div>Count: {count}</div>
</div>
"""

    return html_blocks


def get_deed_rarity_boosts(df):
    # df['total_title_boost'] = pd.to_numeric(df['total_title_boost'], errors='coerce')
    deed_rarity_boosts = df.loc[df['deed_rarity_boost'] > 0.0]
    deed_rarity_boosts = deed_rarity_boosts.groupby('deed_rarity_boost').size().reset_index(name='count')
    html_blocks = ""
    for _, row in deed_rarity_boosts.iterrows():
        deed_rarity_boost_pct = row['deed_rarity_boost'] * 100
        count = row['count']

        image_url = None
        if deed_rarity_boost_pct == 10.0:
            text = "Rare"
            image_url = deed_rarity_rare_icon_url
        elif deed_rarity_boost_pct == 40.0:
            text = "Epic"
            image_url = deed_rarity_epic_icon_url
        elif deed_rarity_boost_pct == 100.0:
            text = "Legendary"
            image_url = deed_rarity_legendary_icon_url
        else:
            text = "?"
            image_html = '<div style="font-size: 24px;">❓</div>'

        if image_url:
            image_html = f'<img src="{image_url}" alt="{deed_rarity_boost_pct}" style="width: 100px; min-height:90px">'

        html_blocks += f"""
<div class="boost-item">
    {image_html}
    <div><strong>{text}</strong></div>
    <div><strong>Boost: {deed_rarity_boost_pct}%</strong></div>
    <div>Count: {count}</div>
</div>
"""

    return html_blocks
