import streamlit as st

from src.static.icons import land_grain_farm_icon_url, land_logging_camp_icon_url, land_ore_mine_icon_url, \
    land_quarry_icon_url, land_research_hut_icon_url, land_shard_mine_icon_url, land_keep_icon_url, \
    land_castle_icon_url, land_hammer_icon_url

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
