import pandas as pd

from src.utils.time_util import valid_date, time_until, calculate_progress


def production_percentage(hours_since_last_op):
    max_hours = 7 * 24  # 7 days = 168 hours
    percent = (hours_since_last_op / max_hours) * 100
    return min(round(percent, 2), 100.0)  # cap at 100%


def get_progress_info(hours_since_last_op, projected_created_date, projected_end_date, boosted_pp):
    if valid_date(projected_end_date):
        info_str = f'Finished in: {time_until(projected_end_date)}'
        percentage_done = calculate_progress(projected_created_date, projected_end_date)
        tooltip = "Show the amount of time until building is finished. When finished a negative time can be shown."
    elif boosted_pp <= 0:
        percentage_done = 0
        info_str = "No workers assigned"
        tooltip = None
    elif pd.notna(hours_since_last_op):
        percentage_done = production_percentage(hours_since_last_op)
        info_str = f'{percentage_done}% Capacity'
        tooltip = ("How close this plot is to full. "
                   "Once capacity reached 100%,"
                   " resources no longer accumulate until they are harvested")
    else:
        percentage_done = 0
        info_str = "Undeveloped"
        tooltip = None

    return pd.Series({'percentage_done': percentage_done, 'info_str': info_str, 'progress_tooltip': tooltip})
