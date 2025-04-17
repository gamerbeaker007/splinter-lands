from typing import Dict, Any, Optional

import pandas as pd
import requests
import streamlit as st
from requests.adapters import HTTPAdapter

from src.api.logRetry import LogRetry
from src.utils.log_util import configure_logger

# API URLs
API_URLS = {
    "base": "https://api2.splinterlands.com/",
    "land": "https://vapi.splinterlands.com/",
    "prices": "https://prices.splinterlands.com/",
}

log = configure_logger(__name__)


# Retry Strategy
def configure_http_session() -> requests.Session:
    retry_strategy = LogRetry(
        total=11,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=2,
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        logger_name="SPL Retry"
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.headers.update({
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "User-Agent": "BeeBalanced/1.0"
    })
    return session


http = configure_http_session()


def fetch_api_data(address: str, params: Optional[Dict[str, Any]] = None,
                   data_key: Optional[str] = None) -> pd.DataFrame:
    """
    Generic function to fetch data from the Splinterlands API.

    :param address: API endpoint URL.
    :param params: Query parameters for the request.
    :param data_key: Key to extract data from JSON response (optional).
    :return: DataFrame with requested data or empty DataFrame on failure.
    """
    try:
        response = http.get(address, params=params, timeout=10)
        response.raise_for_status()

        response_json = response.json()

        # Handle API errors
        if isinstance(response_json, dict) and "error" in response_json:
            log.error(f"API error from {address}: {response_json['error']}")
            return None

        if data_key and isinstance(response_json, dict):
            response_json = get_nested_value(response_json, data_key)

        return response_json

    except requests.exceptions.RequestException as e:
        log.error(f"Error fetching {address}: {e}")
        return pd.DataFrame()


def get_nested_value(response_dict: dict, key_path: str) -> Any:
    """
    Retrieve a nested value from a dictionary using dot-separated keys.
    """
    keys = key_path.split(".")
    for key in keys:
        if isinstance(response_dict, dict) and key in response_dict:
            response_dict = response_dict[key]
        else:
            log.error(f"Invalid key requested {key_path}.. Fix api call or check response changed {response_dict}")
            return {}  # Return empty if any key is missing
    return response_dict


def get_land_region_details(region):
    result = fetch_api_data(f'{API_URLS['land']}land/deeds', params={"region_number": region}, data_key='data')

    if result:
        worksite_details = pd.DataFrame(result["worksite_details"])
        staking_details = pd.DataFrame(result["staking_details"])
        deeds = pd.DataFrame(result["deeds"])
        return deeds, worksite_details, staking_details
    return pd.DataFrame()


@st.cache_data(ttl="1h")
def get_land_resources_pools():
    result = fetch_api_data(f'{API_URLS['land']}land/liquidity/landpools', data_key='data')
    if result:
        return pd.DataFrame(result)
    return pd.DataFrame()


@st.cache_data(ttl="1h")
def get_prices():
    result = fetch_api_data(f'{API_URLS['prices']}prices')
    if result:
        return pd.DataFrame(result, index=[0])
    return pd.DataFrame()


@st.cache_data(ttl="1h")
def get_land_deeds_uid(plot_id):
    result = fetch_api_data(f'{API_URLS['land']}land/deeds/{plot_id}', data_key='data')
    if result:
        return pd.DataFrame(result, index=[0])
    return pd.DataFrame()


@st.cache_data(ttl="1h")
def get_land_stake_deed_details(deed_uid):
    result = fetch_api_data(f'{API_URLS['land']}land/stake/deed/details/{deed_uid}', data_key='data')
    if result:
        return pd.DataFrame(result, index=[0])
    return pd.DataFrame()


@st.cache_data(ttl="1h")
def get_land_region_details_player(player):
    result = fetch_api_data(f'{API_URLS['land']}land/deeds', params={"player": player}, data_key='data')

    if result:
        worksite_details = pd.DataFrame(result["worksite_details"])
        staking_details = pd.DataFrame(result["staking_details"])
        deeds = pd.DataFrame(result["deeds"])
        return deeds, worksite_details, staking_details
    return pd.DataFrame()


def get_staked_assets(deed_uid):
    result = fetch_api_data(f'{API_URLS['land']}land/stake/deeds/{deed_uid}/assets', data_key='data')
    if result:
        return result
    return None
