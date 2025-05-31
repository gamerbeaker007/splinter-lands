import streamlit as st
import asyncio
import os
import time
from datetime import datetime

import pandas as pd

from src.api.db import fetch_data
from src.utils.log_util import configure_logger

log = configure_logger(__name__)

DATA_BASE_DIR = 'data'
TIMESTAMP_PATH = os.path.join(DATA_BASE_DIR, 'last_updated.txt')
LOCK_FILE = os.path.join(DATA_BASE_DIR, 'refresh.lock')


def is_data_stale() -> bool:
    last_updated = load_cached_last_updated()
    try:
        remote = fetch_data.get_last_update()
    except Exception as e:
        log.warning(f"Unable to check DB timestamp: {e}")
        return False  # fail safe: assume not stale

    if remote is None:
        log.error("Major issue: remote DB did not return a valid last_update timestamp")
        return False

    if last_updated is None:
        return True  # no local cache, treat as stale

    return remote > last_updated


def is_refreshing():
    return os.path.exists(LOCK_FILE)


def set_refresh_lock():
    os.makedirs(DATA_BASE_DIR, exist_ok=True)
    with open(LOCK_FILE, 'w') as f:
        f.write(datetime.now().isoformat())


def clear_refresh_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)


async def fetch_all():
    active = fetch_data.get_active()
    deed = fetch_data.get_deed()
    staking_detail = fetch_data.get_staking_detail()
    worksite_detail = fetch_data.get_worksite_detail()
    player_production_summary = fetch_data.get_player_production_summary()
    resource_hub_metrics = fetch_data.get_resource_hub_metrics()
    resource_supply = fetch_data.get_resource_supply()
    resource_tracking = fetch_data.get_resource_tracking()
    last_updated = fetch_data.get_last_update()

    data_dict = {
        'active': active,
        'deed': deed,
        'staking_detail': staking_detail,
        'worksite_detail': worksite_detail,
        'player_production_summary': player_production_summary,
        'resource_hub_metrics': resource_hub_metrics,
        'resource_supply': resource_supply,
        'resource_tracking': resource_tracking,
    }

    save_data(data_dict, last_updated)


def safe_refresh_data(force=False):
    if is_refreshing():
        log.info('Refresh in progress. Skipping.')
        return
    if not force and not is_data_stale():
        log.info('Data is fresh. Skipping refresh.')
        return

    try:
        start_time = time.time()
        log.info("Start reload of data.....")

        st.warning("""
        **⚠️ You're the first to trigger the reload process for today — the community thanks you! 🙌**

        The latest data is being refreshed and should be ready in a few minutes.

        You have two options:
        - ⏳ **Wait** a bit and you'll automatically see the freshest data.
        - 🔄 **Refresh the page (F5)** to load yesterday's data — the update will continue running in the background.

        Thanks for your patience, and sorry for the inconvenience!
        """)

        set_refresh_lock()
        asyncio.run(fetch_all())

        end_time = time.time()
        elapsed_time = end_time - start_time
        log.info(f"Processing data completed in {elapsed_time:.2f} seconds.")

    finally:
        clear_refresh_lock()


def save_data(dict_of_data, last_updated):
    os.makedirs(DATA_BASE_DIR, exist_ok=True)
    for name, df in dict_of_data.items():
        log.info(f'Writing {name}')
        df.to_parquet(os.path.join(DATA_BASE_DIR, f'{name}.parquet'))
    if last_updated:
        with open(TIMESTAMP_PATH, 'w') as f:
            f.write(last_updated.isoformat())
    else:
        log.error("Tried to write None as last_updated... skipping")


def load_cached_last_updated() -> datetime | None:
    if os.path.exists(TIMESTAMP_PATH):
        with open(TIMESTAMP_PATH, 'r') as f:
            value = f.readline().strip()
            try:
                return datetime.fromisoformat(value)
            except Exception as e:
                log.error(f"Invalid timestamp format in {TIMESTAMP_PATH}: {e}")
                return None
    return None


@st.cache_data(ttl='1h')
def load_cached_data(name):
    path = os.path.join(DATA_BASE_DIR, f'{name}.parquet')
    if os.path.exists(path):
        return pd.read_parquet(path)
    log.warning(f'Missing cache: {path}')
    return pd.DataFrame()
