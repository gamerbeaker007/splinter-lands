from src.static.icons import SPL_WEB_URL, land_region_icon_url, land_plot_icon_url, land_tract_icon_url

BASE_URL = "https://next.splinterlands.com/assets/lands/deedsSurveyed"

# Add custom CSS styling
deed_type_style = """
<style>
.deed-type-card {
    position: relative;
    display: flex;
    aspect-ratio: 1 / 2;
    height: 210px;
    width: 400px;
    background-size: cover;
    background-position: center;
    margin: 20px auto;
    overflow: hidden;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: white;
    text-align: center;
}

.deed-overlay {
    position: relative;
    z-index: 2;
    padding: 10px;
    text-shadow: 0 0 6px black;
}

.location {
    background-color: rgba(240, 240, 240, 0.85);
    color: #333;
    border-radius: 8px;
    padding: 5px 10px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    margin-top: 8px;
}
</style>
"""


def add_deed_type(row):
    magical_type = row['magic_type']
    deed_type = row['deed_type']
    plot_status = row['plot_status'].lower()
    rarity = row['rarity'].lower()
    region_number = row['region_number']
    tract_number = row['tract_number']
    plot_number = row['plot_number']
    territory_name = row['territory']
    region_name = row['region_name']

    if magical_type:
        card_img = f'{BASE_URL}/{deed_type.lower()}_{plot_status}_{magical_type}_{rarity}.jpg'
    else:
        card_img = f'{BASE_URL}/{deed_type.lower()}_{plot_status}_{rarity}.jpg'

    path = "assets/lands/deedAssets/"
    if deed_type == 'Unsurveyed Deed':
        image_html = '<div style="font-size: 30px;">❓</div>'
    else:
        image_url = f"{SPL_WEB_URL}{path}img_geography-emblem_{deed_type.lower()}.svg"
        extra_style = 'style="width: 50px; min-height: 50px"'
        image_html = f'<img class="deed-type" src="{image_url}" alt="{deed_type}" {extra_style}>'

    icon_style = 'style="width: 20px; min-height: 20px;"'
    region_img = f'<img src="{land_region_icon_url}" alt="region" {icon_style}>'
    tract_img = f'<img src="{land_tract_icon_url}" alt="tract" {icon_style}>'
    plot_img = f'<img src="{land_plot_icon_url}" alt="plot" {icon_style}>'

    # Inject dynamic background URL via inline style
    return f"""<div class="deed-type-card" style="background-image: url('{card_img}');">
        <div class="deed-overlay">
            {image_html}
            <div><strong>{deed_type}</strong></div>
            <div>{territory_name} | {region_name}</div>
            <div class="location">
                {region_img} {region_number}
                {tract_img} {tract_number}
                {plot_img} {plot_number}
            </div>
        </div>
    </div>"""
