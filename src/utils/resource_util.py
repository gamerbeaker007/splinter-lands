import pandas as pd

from src.static.static_values_enum import consume_rates


def calc_costs(row):
    resource = row["token_symbol"]
    base = row["total_base_pp_after_cap"]
    costs = {f'cost_per_h_{res.lower()}': 0 for res in ['GRAIN', 'WOOD', 'STONE', 'IRON']}

    if resource in {"GRAIN", "WOOD", "STONE", "IRON"}:
        costs['cost_per_h_grain'] = base * consume_rates["GRAIN"]
    elif resource in ["RESEARCH", "SPS"]:
        for dep in ["GRAIN", "WOOD", "STONE", "IRON"]:
            key = f'cost_per_h_{dep.lower()}'
            costs[key] = base * consume_rates[dep]
    return pd.Series(costs)
