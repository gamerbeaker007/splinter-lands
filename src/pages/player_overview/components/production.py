from src.static.icons import land_hammer_icon_url
from src.static.static_values_enum import worksite_type_mapping, resource_icon_map
from src.utils.resource_util import calc_costs

production_card_style = """
<style>
.production-card {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 8px;
    border-radius: 10px;
    border: 1px solid #ccc;
    font-size: 10pt;
    width: 400px
}

.production-main {
    display: flex;
    flex-direction: row;
    gap: 10px;
}

.production-progress {
    padding: 4px 2px 0 2px;
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

.progress-bar-container {
    position: relative;
    width: 100%;
    background-color: #eee;
    border: 2px solid #ccc;
    border-radius: 6px;
    overflow: hidden;
    height: 18px;
    margin-top: 6px;
}

.progress-bar-fill {
    height: 100%;
    transition: width 0.4s ease-in-out;
    z-index: 1;
}

.progress-bar-text {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: bold;
    color: black;
    z-index: 2;
    pointer-events: none;  /* makes sure clicks go through to underlying div if needed */
}

.tooltip-wrapper {
    position: relative;
    display: inline-block;
    margin-left: 6px;
    cursor: pointer;
    font-style: normal;
    font-weight: bold;
    color: #555;
}

.tooltip-box {
    visibility: hidden;
    width: 250px;
    background-color: #333;
    color: #fff;
    text-align: left;
    border-radius: 6px;
    padding: 8px;
    position: absolute;
    z-index: 1;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    opacity: 0;
    transition: opacity 0.3s;
    white-space: normal;
}

.tooltip-wrapper:hover .tooltip-box {
    visibility: visible;
    opacity: 1;
}


</style>
"""


def calculate_taxes(tax_fee, amount):
    if tax_fee:
        amount = amount * 0.90  # there is a 10% tax fee
        extra_txt = "<span style='color:gray'>(incl. tax)</span><br>"
    else:
        extra_txt = "<br>"
    return extra_txt, amount


def get_tooltip_html(row):
    tooltip = row['progress_tooltip']
    if tooltip:
        return f"""<span class="tooltip-wrapper">
            <span>ℹ️</span>
            <div class="tooltip-box">{tooltip}</div>
        </span>"""
    else:
        return "<span/>"


def add_production(row, include_tax):
    worksite_type = row.get('worksite_type', '') or 'Undeveloped'
    base_pp = row.get('total_base_pp', 0)
    boosted_pp = row.get('total_harvest_pp', 0)
    production_per_hour = row.get('rewards_per_hour', 0)
    extra_txt, production_per_hour = calculate_taxes(include_tax, production_per_hour)
    resource = row.get('resource_symbol', '')

    image_url = worksite_type_mapping.get(worksite_type)
    cost = calc_costs(row)

    hammer_icon = f'<img src="{land_hammer_icon_url}" alt="hammer" />'
    prod_icon = f'<img src="{resource_icon_map.get(resource, land_hammer_icon_url)}" alt="{resource}" />'

    progress_html = get_progres_html(row)
    tooltip_html = get_tooltip_html(row)

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
        {prod_icon} {production_per_hour:.1f}/h {extra_txt}
    </div>"""

    html = f"""<div class="production-card">
        <div class="production-main">
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
                <div class='line'><strong>Cost:</strong></div> {cost_html}
            </div>
        </div>
        <div class="production-progress">
            <div class="line"><strong>Progress:</strong>
            {tooltip_html}
            </div>
            {progress_html}
        </div>
    </div>"""

    return html


def get_progres_html(row):
    percentage_done = row['percentage_done']
    info_str = row['info_str']

    if row['resource_symbol'] == "TAX":
        progress_fill_style = "width: 0%; background-color: green;"
        progress_html = f"""<div class="progress-bar-container">
            <div class="progress-bar-fill" style="{progress_fill_style}"></div>
            <div class="progress-bar-text">N/A</div>
        </div>"""
    else:
        progress_color = "red" if percentage_done >= 75 else "orange" if percentage_done >= 40 else "green"
        progress_fill_style = f"width: {percentage_done}%; background-color: {progress_color};"

        progress_html = f"""<div class="progress-bar-container">
            <div class="progress-bar-fill" style="{progress_fill_style}"></div>
            <div class="progress-bar-text">{info_str}</div>
        </div>"""
    return progress_html
