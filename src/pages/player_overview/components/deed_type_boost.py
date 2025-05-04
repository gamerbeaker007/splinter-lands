from src.static.icons import SPL_WEB_URL


def add_deed_type_boost(row):
    plot_status = row['plot_status']
    boost = float(row['deed_status_token_boost']) * 100

    if plot_status not in ['magical', 'occupied'] or boost == 0:
        return "<div></div>"

    img_url = f'{SPL_WEB_URL}assets/lands/sideMenu/{plot_status.lower()}Off.svg'
    label = plot_status
    html = f"""<div class="item-wrapper">
        <div class="item-boost">{boost:.0f}%</div>
        <div class="item-img-container">
            <img src="{img_url}" alt="{label}" style="width: 50px; min-height: 50px" />
        </div>
    </div>"""

    return f"<div style='text-align: center;'>{html}</div>"
