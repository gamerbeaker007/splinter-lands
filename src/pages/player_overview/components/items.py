from src.static.icons import WEB_URL, land_hammer_icon_url
from src.static.static_values_enum import title_icon_map

item_boost_style = """
<style>
.item-wrapper {
    display: inline-block;
    text-align: center;
}
.item-img-container {
    width: 50px;
    height: 50px;
    overflow: hidden;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #gray;
}
.item-img-container img {
    max-width: 100%;
    max-height: 100%;
    padding: 2px;
}
.item-boost {
    font-size: 10pt;
    font-weight: bold;
    font-family: monospace;
    margin-top: 1px;
}
</style>
"""


def add_items(items):
    html = ""
    for item in items:
        boost = float(item['boost']) * 100
        stake_type = item['stake_type_uid']
        name = item['name']

        if stake_type == 'STK-LND-TTL':
            img_url, label = find_title_icon(name)

        elif stake_type == 'STK-LND-TOT':
            label = name
            totem_map = {
                'Common Totem': '1_common',
                'Rare Totem': '2_rare',
                'Epic Totem': '3_epic',
                'Legendary Totem': '4_legendary'
            }
            image_name = totem_map.get(name, name.lower().replace(" ", "_"))
            img_url = f'{WEB_URL}website/icons/icon_totem_{image_name}_300.png'
        else:
            continue  # Skip unknown types

        html += f"""<div class="item-wrapper">
            <div class="item-img-container">
                <img src="{img_url}" alt="{label}" />
            </div>
            <div class="item-boost">{boost:.0f}%</div>
        </div>"""

    return f"<div style='text-align: center;'>{html}</div>"


def find_title_icon(name):
    label = name
    normalized = name[4:].lower() if name.lower().startswith('the ') else name.lower()
    image_name = normalized.replace(" ", "_")
    img_url = title_icon_map.get(image_name, land_hammer_icon_url)
    return img_url, label
