import pandas as pd

from src.static.icons import land_hammer_icon_url
from src.static.static_values_enum import worksite_type_mapping, resource_icon_map
from src.utils.resource_util import calc_costs
from src.utils.time_util import time_until, calculate_progress, valid_date

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

</style>
"""


def production_percentage(hours_since_last_op):
    max_hours = 7 * 24  # 7 days = 168 hours
    percent = (hours_since_last_op / max_hours) * 100
    return min(round(percent, 2), 100.0)  # cap at 100%


def add_production(row):
    worksite_type = row.get('worksite_type', '') or 'Undeveloped'
    base_pp = row.get('total_base_pp', 0)
    boosted_pp = row.get('total_harvest_pp', 0)
    production_per_hour = row.get('rewards_per_hour', 0)
    resource = row.get('resource_symbol', '')
    projected_end_date = row.get('projected_end', None)
    projected_created_date = row.get('project_created_date', None)
    hours_since_last_op = row.get('hours_since_last_op', 0)

    image_url = worksite_type_mapping.get(worksite_type)
    cost = calc_costs(row)

    hammer_icon = f'<img src="{land_hammer_icon_url}" alt="hammer" />'
    prod_icon = f'<img src="{resource_icon_map.get(resource, land_hammer_icon_url)}" alt="{resource}" />'

    progress_html = get_progres_html(
        hours_since_last_op,
        projected_created_date,
        projected_end_date,
        boosted_pp
    )

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
            <div class="line"><strong>Progress:</strong> </div>
            {progress_html}
        </div>
    </div>"""

    return html


def get_progres_html(hours_since_last_op, projected_created_date, projected_end_date, boosted_pp):
    if valid_date(projected_end_date):
        info_str = f'Finished in: {time_until(projected_end_date)}'
        percentage_done = calculate_progress(projected_created_date, projected_end_date)
    elif boosted_pp <= 0:
        percentage_done = 0
        info_str = "No workers assigned"
    elif pd.notna(hours_since_last_op):
        percentage_done = production_percentage(hours_since_last_op)
        info_str = f'{percentage_done}% Full'
    else:
        percentage_done = 0
        info_str = "Undeveloped"

    progress_color = "red" if percentage_done >= 75 else "orange" if percentage_done >= 40 else "green"
    progress_fill_style = f"width: {percentage_done}%; background-color: {progress_color};"

    progress_html = f"""<div class="progress-bar-container">
        <div class="progress-bar-fill" style="{progress_fill_style}"></div>
        <div class="progress-bar-text">{info_str}</div>
    </div>"""
    return progress_html
