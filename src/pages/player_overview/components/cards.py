from src.static.icons import WEB_URL, land_hammer_icon_url
from src.static.static_values_enum import Edition


card_display_style = """
<style>
.card-wrapper {
    display: inline-block;
    text-align: center;
    width: 75px;
}

.card-img-container.gold {
    border-color: gold;
}

.card-img-container {
    width: 75px;
    height: 110px;
    border: 3px solid gray;
    border-radius: 10px;
    background-color: #f5f5f5;
    background-size: 200%;
    background-repeat: no-repeat;
    background-position: center -20px;
    display: block;
    line-height: 0;
    padding: 0;
    margin: 0;
}

.card-pp-info {
    margin-top: 1px;
    background-color: rgba(240, 240, 240, 0.85);
    color: #333;
    font-size: 10pt;
    font-family: monospace;
    padding: 4px 6px;
    border-radius: 6px;
}
.card-pp-info img {
    vertical-align: middle;
    height: 12px;
    margin-right: 1px;
}
</style>
"""


def get_card_img(card_name, edition, foil):
    card_name = card_name.split(' - ')[0]
    gold_suffix = "_gold" if foil else ""
    base_card_url = f'{WEB_URL}cards_by_level'
    edition_name = Edition(edition).name
    safe_card_name = str(card_name).replace(" ", "%20")
    return f'{base_card_url}/{edition_name}/{safe_card_name}_lv1{gold_suffix}.png'


def add_card(cards):
    html = ""
    for card in cards:
        if 'runi' in card['name'].lower():
            print("RUNI TODO")
            continue  # Skip or handle separately
        base_pp = float(card['base_pp_after_cap'])
        boosted_pp = float(card['total_harvest_pp'])
        img = get_card_img(card['name'], card['edition'], card['foil'])
        is_gold = "gold" if card['foil'] else ""
        html += f"""<div class="card-wrapper">
            <div class="card-img-container {is_gold}" style="background-image: url('{img}');"></div>
            <div class="card-pp-info">
                <img src="{land_hammer_icon_url}" alt="hammer"/> {base_pp:.0f}<br/>
                <img src="{land_hammer_icon_url}" alt="hammer"/> {boosted_pp:.0f}
            </div>
        </div>
        """
    return f"<div style='text-align:center'>{html}</div>"


def add_card_runi(cards):
    html = ""
    for card in cards:
        if 'runi' in card['name'].lower():
            base_pp = float(card['base_pp_after_cap'])
            boosted_pp = float(card['total_harvest_pp'])
            img = f'https://runi.splinterlands.com/cards/{card['uid']}.jpg'
            is_gold = "gold" if card['foil'] else ""
            html += f"""<div class="card-wrapper">
                <div class="card-img-container {is_gold}" style="background-image: url('{img}');"></div>
                <div class="card-pp-info">
                    <img src="{land_hammer_icon_url}" alt="hammer"/> {base_pp:.0f}<br/>
                    <img src="{land_hammer_icon_url}" alt="hammer"/> {boosted_pp:.0f}
                </div>
            </div>
            """
    return f"<div style='text-align:center'>{html}</div>"
