from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import streamlit as st

from src.api import spl
from src.pages.player_overview.resource_player import prepare_summary
from src.static.static_values_enum import PRODUCING_RESOURCES
from src.utils.resource_util import get_price


@st.cache_data(show_spinner="Processing data...")
def prepare_data(df):
    grouped_df = df.groupby(["region_uid", 'token_symbol', 'player']).agg(
        {'total_harvest_pp': 'sum',
         'total_base_pp_after_cap': 'sum',
         'rewards_per_hour': 'sum'}
    ).reset_index()

    token_counts = (
        df.groupby(['region_uid', 'token_symbol', 'player'])
        .agg(count=('token_symbol', 'count'))
        .reset_index()
    )

    return grouped_df.merge(token_counts, on=["region_uid", 'token_symbol', 'player'], how='left')


def process_player(player, temp_df, unit_prices):
    print(f'Processing player {player}')
    summary_df = prepare_summary(temp_df, True, True)

    dec_net = {}
    total_dec = 0
    for key in PRODUCING_RESOURCES:
        k = key.lower()
        amount = summary_df[f"adj_net_{k}"].sum()
        dec_value = unit_prices[k] * amount
        dec_net[f"dec_{k}"] = dec_value
        total_dec += dec_value

    harvest_sum = temp_df['total_harvest_pp'].sum()
    base_sum = temp_df['total_base_pp_after_cap'].sum()
    count_sum = temp_df['count'].sum()

    return {
        'player': player,
        'total_harvest_pp': harvest_sum,
        'total_base_pp_after_cap': base_sum,
        'count': count_sum,
        'total_dec': total_dec,
        **dec_net
    }


def get_page(df):
    return
    metrics_df = spl.get_land_resources_pools()
    prices_df = spl.get_prices()

    st.title("WIP")
    st.write(f'unique land owners {len(df.player.unique().tolist())}')
    df = prepare_data(df)

    unit_prices = {
        key.lower(): get_price(metrics_df, prices_df, key, 1)
        for key in PRODUCING_RESOURCES
    }

    # Multithreaded processing
    summary_rows = []
    with ThreadPoolExecutor() as executor:
        futures = []
        for player, temp_df in df.groupby("player"):
            futures.append(executor.submit(process_player, player, temp_df, unit_prices))
        for future in futures:
            summary_rows.append(future.result())

    total_df = pd.DataFrame(summary_rows)
    st.dataframe(total_df)
