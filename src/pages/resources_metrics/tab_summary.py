import streamlit as st

from src.static.icons import SPL_WEB_URL, land_hammer_icon_url, land_grain_farm_icon_url, \
    land_logging_camp_icon_url, land_ore_mine_icon_url, land_quarry_icon_url, land_research_hut_icon_url, \
    land_shard_mine_icon_url, land_keep_icon_url, land_castle_icon_url


def print_deed_types(df):
    grouped = df.groupby('deed_type').size().reset_index(name='count')
    grouped = grouped.sort_values(by='deed_type', ascending=True)

    st.markdown("### Deed Type Overview")

    # Start flex container
    total_html = """
        <style>
        .deed-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
        }
        .deed-item {
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            min-width: 120px;
            max-width: 120px;
            min-height: 150px;
            flex-grow: 1;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        }
        .deed-item img {
            max-width: 80px;
            height: auto;
        }
        </style>
        <div class="deed-grid">
        """

    html_blocks = ""
    for _, row in grouped.iterrows():
        deed_type = row['deed_type']
        count = row['count']

        if deed_type == 'Unsurveyed Deed':
            image_html = '<div style="font-size: 24px;">❓</div>'
        else:
            image_url = f"{SPL_WEB_URL}assets/lands/deedAssets/img_geography-emblem_{deed_type.lower()}.svg"
            image_html = f'<img src="{image_url}" alt="{deed_type}">'

        html_blocks += f"""
        <div class="deed-item">
            {image_html}
            <div><strong>{deed_type}</strong></div>
            <div>Count: {count}</div>
        </div>
        """

    total_html += html_blocks
    total_html += '</div>'
    # Close container and render
    st.markdown(total_html, unsafe_allow_html=True)


def print_rarity(df):
    rarities = df['rarity'].value_counts().reset_index()

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
        if rarity == 'mythic':
            image_url = f"{SPL_WEB_URL}assets/lands/sideMenu/legendaryOff.svg"
        else:
            image_url = f"{SPL_WEB_URL}assets/lands/sideMenu/{rarity.lower()}Off.svg"

        html_blocks += f"""
        <div class="rarity-item">
            <img src="{image_url}" alt="{rarity}">
            <div><strong>{rarity.title()}</strong></div>
            <div>Count: {count}</div>
        </div>
        """

    total_html += """<div class="rarity-grid">"""
    total_html += html_blocks
    total_html += "</div>"
    st.markdown(total_html, unsafe_allow_html=True)


worksite_type_mapping = {
    'Grain Farm': land_grain_farm_icon_url,
    'Logging Camp': land_logging_camp_icon_url,
    'Ore Mine': land_ore_mine_icon_url,
    'Quarry': land_quarry_icon_url,
    'Research Hut': land_research_hut_icon_url,
    'Shard Mine': land_shard_mine_icon_url,
    'KEEP': land_keep_icon_url,
    'CASTLE': land_castle_icon_url,
    '': land_hammer_icon_url,
}


def print_worksite_types(df):
    worksite_types = df['worksite_type'].value_counts().reset_index()

    ordered_keys = list(worksite_type_mapping.keys())
    worksite_types = worksite_types[worksite_types['worksite_type'].isin(ordered_keys)]
    worksite_types['sort_order'] = worksite_types['worksite_type'].apply(lambda x: ordered_keys.index(x))
    worksite_types = worksite_types.sort_values('sort_order')

    st.markdown("### Worksite Type Overview")

    total_html = """
        <style>
        .worksite-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
        }
        .worksite-item {
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            min-width: 100px;
            max-width: 120px;
            flex-grow: 1;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        }
        .worksite-item img {
            max-width: 60px;
            height: auto;
        }
        </style>
        <div class="worksite-grid">
    """

    html_blocks = ""
    for _, row in worksite_types.iterrows():
        worksite_type = row['worksite_type']
        count = row['count']

        image_url = worksite_type_mapping.get(worksite_type)
        html_blocks += f"""
        <div class="worksite-item">
            <img src="{image_url}" alt="{worksite_type}">
            <div><strong>{worksite_type.replace('_', ' ').title()}</strong></div>
            <div>Count: {count}</div>
        </div>
        """

    total_html += html_blocks
    total_html += "</div>"

    st.markdown(total_html, unsafe_allow_html=True)


def print_player_info(df):
    unique_players = df.player.unique().size
    top_ten_holders = df['player'].value_counts().head(10)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Top 10 Holders")
        html = "<div style='line-height:1.6;'>"
        for i, (player, count) in enumerate(top_ten_holders.items(), start=1):
            html += f"<strong>{i}.</strong> {player} <span style='color:gray'>({count})</span><br>"
        html += "</div>"

        st.markdown(html, unsafe_allow_html=True)
    with col2:
        st.markdown("### Unique owners")
        st.markdown(f"{unique_players}")


def get_page(filtered_all_data):
    st.markdown("### Player Overview")

    print_player_info(filtered_all_data)
    print_rarity(filtered_all_data)
    print_deed_types(filtered_all_data)
    print_worksite_types(filtered_all_data)
