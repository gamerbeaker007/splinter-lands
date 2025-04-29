import pandas as pd

from src.static.static_values_enum import consume_rates, CONSUMING_GRAIN_ONLY_RESOURCES, MULTIPLE_CONSUMING_RESOURCE, \
    NATURAL_RESOURCE


def calc_costs(row):
    resource = row["token_symbol"]
    base = row["total_base_pp_after_cap"]
    costs = {f'cost_per_h_{res.lower()}': 0 for res in NATURAL_RESOURCE}

    if resource in CONSUMING_GRAIN_ONLY_RESOURCES:
        costs['cost_per_h_grain'] = base * consume_rates["GRAIN"]
    elif resource in MULTIPLE_CONSUMING_RESOURCE:
        for dep in NATURAL_RESOURCE:
            key = f'cost_per_h_{dep.lower()}'
            costs[key] = base * consume_rates[dep]
    return pd.Series(costs)
