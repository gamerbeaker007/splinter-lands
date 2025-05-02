import asyncio
import gc
import os
from datetime import datetime

import pandas as pd

from src.api import spl
from src.api.db import resource_tracking, resource_metrics, active_metrics
from src.static.static_values_enum import LEADERBOARD_RESOURCES
from src.utils.log_util import configure_logger

log = configure_logger(__name__)

DATA_BASE_DIR = 'data'
DATA_PARTIAL_DIR = os.path.join(DATA_BASE_DIR, 'partial')
TIMESTAMP_PATH = os.path.join(DATA_BASE_DIR, 'last_updated.txt')
LOCK_FILE = os.path.join(DATA_BASE_DIR, 'refresh.lock')


def save_partial(category, df, suffix):
    os.makedirs(DATA_PARTIAL_DIR, exist_ok=True)
    filename = os.path.join(DATA_PARTIAL_DIR, f"{category}_{suffix}.parquet")
    df.to_parquet(filename, index=False)


async def fetch_all_region_data():
    for region_number in range(1, 151):
        log.info(f'fetching data for region: {region_number}')
        deed, worksite_details, staked_details = spl.get_land_region_details(region_number)

        save_partial("deeds", deed, region_number)
        save_partial("worksite_details", worksite_details, region_number)
        save_partial("staking_details", staked_details, region_number)

        del deed, worksite_details, staked_details
        gc.collect()

    for resource in LEADERBOARD_RESOURCES:
        log.info(f'fetching leaderboard data for resource: {resource}')
        leaderboard_df = spl.get_resource_leaderboard(resource)
        leaderboard_df['resource'] = resource
        save_partial("resource_leaderboard", leaderboard_df, resource)
        del leaderboard_df
        gc.collect()

    # Concatenate only for final merge/processing
    deeds_df = pd.concat([pd.read_parquet(f"{DATA_PARTIAL_DIR}/deeds_{i}.parquet") for i in range(1, 151)])
    worksite_df = pd.concat([pd.read_parquet(f"{DATA_PARTIAL_DIR}/worksite_details_{i}.parquet") for i in range(1, 151)])
    staking_df = pd.concat([pd.read_parquet(f"{DATA_PARTIAL_DIR}/staking_details_{i}.parquet") for i in range(1, 151)])
    resource_leaderboards = pd.concat([
        pd.read_parquet(f"{DATA_PARTIAL_DIR}/resource_leaderboard_{res}.parquet") for res in LEADERBOARD_RESOURCES
    ])

    data_dict = {
        'deeds': deeds_df,
        'worksite_details': worksite_df,
        'staking_details': staking_df,
        'resource_leaderboard': resource_leaderboards
    }

    df = merge_with_details(deeds_df, worksite_df, staking_df)
    resource_tracking.upload_daily_resource_metrics(df, resource_leaderboards)
    resource_metrics.upload_land_resources_info()
    active_metrics.upload_daily_active_metrics(df)

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
