from src.static.icons import WEB_URL

item_boost_style = """
<style>
.item-wrapper {
    display: inline-block;
    text-align: center;
    margin: 6px;
    width: 75px;
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
    font-size: 8pt;
    font-weight: bold;
    font-family: monospace;
    margin-top: 4px;
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
            label = name
            normalized = name[4:].lower() if name.lower().startswith('the ') else name.lower()
            image_name = normalized.replace(" ", "%20")
            img_url = f'{WEB_URL}website/icons/icon_active_{image_name}.svg'

        elif stake_type == 'STK-LND-TOT':
            label = name
            totem_map = {
                'Common Totem': '1_common',
                'Rare Totem': '1_rare',
                'Epic Totem': '1_epic',
                'Legendary Totem': '1_legendary'
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
