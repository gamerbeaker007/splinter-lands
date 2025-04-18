from src.static.icons import land_hammer_icon_url
from src.static.static_values_enum import worksite_type_mapping, resource_icon_map
from src.utils.resource_util import calc_costs

production_card_style = """
<style>
.production-card {
    display: flex;
    flex-direction: row;
    gap: 10px;
    padding: 8px;
    border-radius: 10px;
    border: 1px solid #ccc;
    font-size: 10pt;
}

.production-info {
    flex-grow: 1;
    font-family: monospace;
}

.production-info .line {
    margin-bottom: 4px;
}

.production-info img {
    vertical-align: middle;
    height: 20px;
    margin-right: 4px;
}

.production-info {
    font-weight: bold;
    margin-top: 6px;
    margin-bottom: 2px;
    display: block;
}

.production-left {
    text-align: center;
    flex-shrink: 0;
}

.production-img-container {
    width: 150px;
    height: 150px;
    border-radius: 10px;
    background-size: 90%;
    background-repeat: no-repeat;
    background-position: center center;
    border: 2px solid #ccc;
    margin-bottom: 4px;
}

.production-pp {
    font-size: 10pt;
    font-family: monospace;
    padding: 4px 6px;
    border-radius: 6px;
    background-color: rgba(240, 240, 240, 0.85);
    color: #333;
    margin-top: 2px;
}
.production-pp img {
    vertical-align: middle;
    height: 12px;
    margin-right: 3px;
}
</style>
"""


def add_production(row):
    worksite_type = row.get('worksite_type', '') or 'Undeveloped'
    base_pp = row.get('total_base_pp', 0)
    boosted_pp = row.get('total_harvest_pp', 0)
    production_per_hour = row.get('rewards_per_hour', 0)
    resource = row.get('resource_symbol', '')
    image_url = worksite_type_mapping.get(worksite_type)
    cost = calc_costs(row)

    hammer_icon = f'<img src="{land_hammer_icon_url}" alt="hammer" />'
    prod_icon = f'<img src="{resource_icon_map.get(resource, land_hammer_icon_url)}" alt="{resource}" />'

    # Generate cost lines (skip zero)
    cost_html = ""
    for key, value in cost.items():
        if value and value > 0:
            res_name = key.split('_')[-1].upper()
            icon = resource_icon_map.get(res_name)
            if icon:
                cost_html += f"""<div class="line">
                    <img src="{icon}" alt="{res_name}" /> {value:.1f}/h
                </div>"""

    production_html = f"""<div class="line">
        {prod_icon} {production_per_hour:.1f}/h
    </div>"""

    html = f"""<div class="production-card">
        <div class="production-left">
            <div class="production-img-container" style="background-image: url('{image_url}');"></div>
            <div class="production-pp">
                {hammer_icon} {base_pp:.0f} </br>
                {hammer_icon} {boosted_pp:.0f}
            </div>
        </div>
        <div class="production-info">
            <div class="line"><strong>Worksite:</strong> {worksite_type}</div>
            <div class="line"><strong>Production:</strong></div> {production_html}
            <div class='line'><string>Cost:</strong></div> {cost_html}
        </div>
    </div>"""

    return html
