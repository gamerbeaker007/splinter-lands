import asyncio
import gc
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import pandas as pd

from src.api import spl
from src.api.db import resource_tracking, resource_metrics, active_metrics
from src.pages.player_overview.resource_player import prepare_summary
from src.static.static_values_enum import LEADERBOARD_RESOURCES, PRODUCING_RESOURCES
from src.utils.log_util import configure_logger
from src.utils.resource_util import get_price

log = configure_logger(__name__)

DATA_BASE_DIR = 'data'
DATA_PARTIAL_DIR = os.path.join(DATA_BASE_DIR, 'partial')
TIMESTAMP_PATH = os.path.join(DATA_BASE_DIR, 'last_updated.txt')
LOCK_FILE = os.path.join(DATA_BASE_DIR, 'refresh.lock')


def save_partial(category, df, suffix):
    os.makedirs(DATA_PARTIAL_DIR, exist_ok=True)
    filename = os.path.join(DATA_PARTIAL_DIR, f"{category}_{suffix}.parquet")
    df.to_parquet(filename, index=False)


def process_player(player, temp_df, unit_prices):
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


def create_dec_earning_df(df):
    log.info("Start Processing DEC...")

    metrics_df = spl.get_land_resources_pools()
    prices_df = spl.get_prices()

    # filter out inactive deeds
    log.info(f'unique land owners {len(df.player.unique().tolist())}')
    df = df.loc[df.total_harvest_pp > 0]
    log.info(f'unique active land owners {len(df.player.unique().tolist())}')

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

    grouped_df = grouped_df.merge(token_counts, on=["region_uid", 'token_symbol', 'player'], how='left')

    unit_prices = {
        key.lower(): get_price(metrics_df, prices_df, key, 1)
        for key in PRODUCING_RESOURCES
    }

    start_time = time.time()
    summary_rows = []
    log.info("Start Threads.....")

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for player, temp_df in grouped_df.groupby("player"):
            futures.append(executor.submit(process_player, player, temp_df, unit_prices))

        total = len(futures)
        for i, future in enumerate(futures, start=1):
            result = future.result()
            summary_rows.append(result)
            log.info(f"Progress: {i}/{total} players processed")

    end_time = time.time()
    elapsed_time = end_time - start_time
    log.info(f"Processing with Thread completed in {elapsed_time:.2f} seconds.")
    return pd.DataFrame(summary_rows)


def process_region(region_number):
    try:
        log.info(f'fetching data for region: {region_number}')
        deed, worksite_details, staked_details = spl.get_land_region_details(region_number)

        save_partial("deeds", deed, region_number)
        save_partial("worksite_details", worksite_details, region_number)
        save_partial("staking_details", staked_details, region_number)

        del deed, worksite_details, staked_details
        gc.collect()
    except Exception as e:
        log.error(f"Error processing region {region_number}: {e}")


def process_leaderboard_resource(resource):
    try:
        log.info(f'Fetching leaderboard data for resource: {resource}')
        leaderboard_df = spl.get_resource_leaderboard(resource)
        leaderboard_df['resource'] = resource

        save_partial("resource_leaderboard", leaderboard_df, resource)

        del leaderboard_df
        gc.collect()

        return f"Resource {resource} processed successfully"
    except Exception as e:
        log.error(f"Error processing resource {resource}: {e}")
        return f"Resource {resource} failed: {e}"


async def fetch_all_region_data():
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(process_region, region_number) for region_number in range(1, 151)]

        for future in as_completed(futures):
            future.result()  # Ensures exceptions are raised

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(process_leaderboard_resource, resource): resource for resource in LEADERBOARD_RESOURCES}

        for future in as_completed(futures):
            result = future.result()
            log.info(result)

    # Concatenate only for final merge/processing
    deeds_df = pd.concat(
        [pd.read_parquet(f"{DATA_PARTIAL_DIR}/deeds_{i}.parquet") for i in range(1, 151)]
    )
    worksite_df = pd.concat(
        [pd.read_parquet(f"{DATA_PARTIAL_DIR}/worksite_details_{i}.parquet") for i in range(1, 151)]
    )
    staking_df = pd.concat(
        [pd.read_parquet(f"{DATA_PARTIAL_DIR}/staking_details_{i}.parquet") for i in range(1, 151)]
    )
    resource_leaderboards = pd.concat(
        [pd.read_parquet(f"{DATA_PARTIAL_DIR}/resource_leaderboard_{res}.parquet") for res in LEADERBOARD_RESOURCES]
    )

    df = merge_with_details(deeds_df, worksite_df, staking_df)
    resource_tracking.upload_daily_resource_metrics(df, resource_leaderboards)
    resource_metrics.upload_land_resources_info()
    active_metrics.upload_daily_active_metrics(df)

    dec_df = create_dec_earning_df(df)

    data_dict = {
        'deeds': deeds_df,
        'worksite_details': worksite_df,
        'staking_details': staking_df,
        'resource_leaderboard': resource_leaderboards,
        'resource_net_dec': dec_df
    }

    save_data(data_dict)


def save_data(dict_of_data):
    os.makedirs(DATA_BASE_DIR, exist_ok=True)
    for name, df in dict_of_data.items():
        log.info(f'Writing {name}')
        df.to_parquet(os.path.join(DATA_BASE_DIR, f'{name}.parquet'))
    with open(TIMESTAMP_PATH, 'w') as f:
        f.write(datetime.now().isoformat())


def get_last_updated():
    if not os.path.exists(TIMESTAMP_PATH):
        return None
    with open(TIMESTAMP_PATH, 'r') as f:
        return datetime.fromisoformat(f.read().strip())


def is_data_stale():
    last_updated = get_last_updated()
    if not last_updated:
        return True
    return datetime.now().date() > last_updated.date()


def load_cached_data(name):
    if os.path.exists(DATA_BASE_DIR):
        filename = os.path.join(DATA_BASE_DIR, f'{name}.parquet')
        if os.path.exists(filename):
            return pd.read_parquet(filename)
        else:
            log.warning(f'file not found: {filename}')

    return pd.DataFrame()


def is_refreshing():
    return os.path.exists(LOCK_FILE)


def set_refresh_lock():
    os.makedirs(DATA_BASE_DIR, exist_ok=True)
    with open(LOCK_FILE, 'w') as f:
        f.write(datetime.now().isoformat())


def clear_refresh_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)


def safe_refresh_data():
    if is_refreshing():
        log.info('Refresh already in progress. Skipping.')
        return

    try:
        set_refresh_lock()
        asyncio.run(fetch_all_region_data())
    finally:
        clear_refresh_lock()


def merge_with_details(deeds, worksite_details, staking_details):
    df = pd.merge(
        deeds,
        worksite_details,
        how='left',
        on='deed_uid',
        suffixes=('', '_worksite_details')
    )
    df = pd.merge(
        df,
        staking_details,
        how='left',
        on='deed_uid',
        suffixes=('', '_staking_details')
    )

    matching_columns = df.columns[df.columns.str.endswith(('_worksite_details', '_staking_details'))].tolist()
    log.debug(f'Reminder watch these columns: {matching_columns}')

    return df.reindex(sorted(df.columns), axis=1)
