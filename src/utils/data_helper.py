import pandas as pd

from src.utils.data_loader_new import load_cached_data, load_cached_last_updated
from src.utils.log_util import configure_logger

log = configure_logger(__name__)


def merge_land_deed_with_details(deeds, worksite_details, staking_details):
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


def get_historical_resource_hub_data():
    return load_cached_data('resource_hub_metrics')


def get_historical_resource_tracking_data():
    return load_cached_data('resource_tracking')


def get_latest_resource_tracking_data():
    df = load_cached_data('resource_tracking')
    if df.empty or 'date' not in df.columns:
        return pd.DataFrame()

    df['date'] = pd.to_datetime(df['date'])  # ensure datetime
    latest_date = df['date'].max()
    return df[df['date'] == latest_date]


def get_historical_resource_supply_data():
    return load_cached_data('resource_supply')


def get_latest_resource_total_supply():
    df = load_cached_data('resource_supply')
    if df.empty or 'date' not in df.columns:
        return pd.DataFrame()

    df['date'] = pd.to_datetime(df['date'])  # ensure datetime
    latest_date = df['date'].max()
    return df[df['date'] == latest_date]


def get_land_data_merged():
    deeds = load_cached_data('deed')
    worksite_details = load_cached_data('worksite_detail')
    staking_details = load_cached_data('staking_detail')
    df = merge_land_deed_with_details(deeds, worksite_details, staking_details)
    return df


def get_last_updated():
    return load_cached_last_updated()


def get_historical_active_data():
    return load_cached_data('active')


def get_latest_active_data():
    df = load_cached_data('active')
    if df.empty or 'date' not in df.columns:
        return pd.DataFrame()

    df['date'] = pd.to_datetime(df['date'])  # ensure datetime
    latest_date = df['date'].max()
    return df[df['date'] == latest_date]


def get_player_summary_data():
    return load_cached_data('player_production_summary')
