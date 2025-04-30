import pandas as pd

from src.api import spl
from src.static.static_values_enum import consume_rates, CONSUMING_GRAIN_ONLY_RESOURCES, MULTIPLE_CONSUMING_RESOURCE, \
    NATURAL_RESOURCE, DEFAULT_ORDER_RESOURCES


def get_price(metrics_df, prices_df, token, amount) -> float:
    if token == 'RESEARCH':
        return 0
    if token == "SPS":
        usd_value = amount * prices_df['sps'].values[0]
        dec_total = usd_value / prices_df['dec'].values[0]
        return dec_total
    if token == "AURA":
        usd_price = spl.get_item_price('MIDNIGHTPOT')
        if usd_price:
            dec_total = usd_price / prices_df['dec'].values[0]
            return dec_total / 40  # 40 aura is needed to make one midnight potion
        else:
            return 0
    return amount / metrics_df[metrics_df['token_symbol'] == token]['dec_price'].values[0]


def reorder_column(df, column="token_symbol"):
    filtered_df = df[df[column].isin(DEFAULT_ORDER_RESOURCES)]
    filtered_resources = [r for r in DEFAULT_ORDER_RESOURCES if r in filtered_df[column].values]
    ordered_df = filtered_df.set_index(column).loc[filtered_resources].reset_index()
    return ordered_df


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
