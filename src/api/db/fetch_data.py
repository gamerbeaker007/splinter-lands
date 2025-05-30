import pandas as pd
import streamlit as st

from src.api.db.session import get_session
from src.utils.log_util import configure_logger

# Define table names as constants (in case your DB uses snake_case or mapped names)
DEED_TABLE = "deed"
STAKING_DETAIL_TABLE = "staking_detail"
WORKSITE_DETAIL_TABLE = "worksite_detail"
ACTIVE_TABLE = "active"
LAST_UPDATE_TABLE = "last_update"
PLAYER_PRODUCTION_TABLE = "player_production_summary"
RESOURCE_HUB_TABLE = "resource_hub_metrics"
RESOURCE_SUPPLY_TABLE = "resource_supply"
RESOURCE_TRACKING_TABLE = "resource_tracking"

log = configure_logger(__name__)


@st.cache_data(ttl='1h')
def get_last_update() :
    log.info('Fetch fresh data -  get_last_update')
    Session = get_session()
    with Session() as session:
        query = f"SELECT * FROM {LAST_UPDATE_TABLE}"
        df = pd.read_sql(query, con=session.bind)
        if df.empty:
            return
        return df.updatedAt.iloc[0]


def get_active() -> pd.DataFrame:
    log.info('Fetch fresh data -  get_active')
    Session = get_session()
    with Session() as session:
        query = f"SELECT * FROM {ACTIVE_TABLE}"
        return pd.read_sql(query, con=session.bind)


def get_deed() -> pd.DataFrame:
    log.info('Fetch fresh data -  get_deed')
    Session = get_session()
    with Session() as session:
        query = f"SELECT * FROM {DEED_TABLE}"
        return pd.read_sql(query, con=session.bind)


def get_staking_detail() -> pd.DataFrame:
    log.info('Fetch fresh data -  get_staking_detail')
    Session = get_session()
    with Session() as session:
        query = f"SELECT * FROM {STAKING_DETAIL_TABLE}"
        return pd.read_sql(query, con=session.bind)


def get_worksite_detail() -> pd.DataFrame:
    log.info('Fetch fresh data -  get_worksite_detail')
    Session = get_session()
    with Session() as session:
        query = f"SELECT * FROM {WORKSITE_DETAIL_TABLE}"
        return pd.read_sql(query, con=session.bind)


def get_player_production_summary() -> pd.DataFrame:
    log.info('Fetch fresh data -  get_player_production_summary')
    Session = get_session()
    with Session() as session:
        query = f"SELECT * FROM {PLAYER_PRODUCTION_TABLE}"
        return pd.read_sql(query, con=session.bind)


def get_resource_hub_metrics() -> pd.DataFrame:
    log.info('Fetch fresh data -  get_resource_hub_metrics')
    Session = get_session()
    with Session() as session:
        query = f"SELECT * FROM {RESOURCE_HUB_TABLE}"
        return pd.read_sql(query, con=session.bind)


def get_resource_supply() -> pd.DataFrame:
    log.info('Fetch fresh data -  get_resource_supply')
    Session = get_session()
    with Session() as session:
        query = f"SELECT * FROM {RESOURCE_SUPPLY_TABLE}"
        return pd.read_sql(query, con=session.bind)


def get_resource_tracking() -> pd.DataFrame:
    log.info('Fetch fresh data -  get_resource_tracking')
    Session = get_session()
    with Session() as session:
        query = f"SELECT * FROM {RESOURCE_TRACKING_TABLE}"
        return pd.read_sql(query, con=session.bind)
