import logging

import pandas as pd

import asyncio
import os
from datetime import datetime

from src.api import spl

log = logging.getLogger('Data Loader')

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

    # Combine the individual DataFrames into one for each category
    deeds_df = pd.concat(all_deeds, ignore_index=True)
    worksite_df = pd.concat(all_worksite_details, ignore_index=True)
    staking_df = pd.concat(all_staking_details, ignore_index=True)
    data_dict = {
        'deeds': deeds_df,
        'worksite_details': worksite_df,
        'staking_details': staking_df,

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
    return (datetime.now() - last_updated).days >= 1


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
