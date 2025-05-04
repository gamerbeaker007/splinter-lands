from src.static.icons import SPL_WEB_URL


def add_rarity_boost(row):
    rarity = row['rarity']
    if rarity in ['mythic', 'common']:
        return "<div></div>"

    boost = float(row['deed_rarity_boost']) * 100
    img_url = f'{SPL_WEB_URL}assets/lands/sideMenu/{rarity.lower()}Off.svg'
    label = rarity
    html = f"""<div class="item-wrapper">
        <div class="item-boost">{boost:.0f}%</div>
        <div class="item-img-container">
            <img src="{img_url}" alt="{label}" style="width: 50px; min-height: 50px" />
        </div>
    </div>"""

    return f"<div style='text-align: center;'>{html}</div>"
