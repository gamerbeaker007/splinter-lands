import asyncio
import os
from datetime import datetime

import pandas as pd

from src.api import spl
from src.api.db import resource_tracking, resource_metrics, active_metrics
from src.static.static_values_enum import RESOURCES_RANKINGS
from src.utils.log_util import configure_logger

log = configure_logger(__name__)

DATA_BASE_DIR = 'data'
TIMESTAMP_PATH = os.path.join(DATA_BASE_DIR, 'last_updated.txt')
LOCK_FILE = os.path.join(DATA_BASE_DIR, 'refresh.lock')


async def fetch_all_region_data():
    all_deeds = []
    all_worksite_details = []
    all_staking_details = []

    for region_number in range(1, 151):
        log.info(f'fetching data for region: {region_number}')
        deed, worksite_details, staked_details = spl.get_land_region_details(region_number)

        all_deeds.append(deed)
        all_worksite_details.append(worksite_details)
        all_staking_details.append(staked_details)

    all_resource_leaderboards = []
    for resource in RESOURCES_RANKINGS:
        log.info(f'fetching leaderboard data for resource: {resource}')
        leaderboard_df = spl.get_resource_leaderboard(resource)
        leaderboard_df['resource'] = resource  # add the resource type to each row
        all_resource_leaderboards.append(leaderboard_df)

    # Combine the individual DataFrames into one for each category
    deeds_df = pd.concat(all_deeds, ignore_index=True)
    worksite_df = pd.concat(all_worksite_details, ignore_index=True)
    staking_df = pd.concat(all_staking_details, ignore_index=True)
    resource_leaderboards = pd.concat(all_resource_leaderboards, ignore_index=True)

    data_dict = {
        'deeds': deeds_df,
        'worksite_details': worksite_df,
        'staking_details': staking_df,
        'resource_leaderboard': resource_leaderboards
    }

    # store pp tracking (resource on daily bases)
    df = merge_with_details(deeds_df, worksite_df, staking_df)
    resource_tracking.upload_daily_resource_metrics(df, resource_leaderboards)

    # store daily resource metrics
    resource_metrics.upload_land_resources_info()

    # store daily active metrics
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
