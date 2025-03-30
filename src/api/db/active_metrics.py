import logging
from datetime import date

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

from src.api.db import upload
from src.models.models import ACTIVE_TABLE_NAME

# Same URL as in alembic.ini
db_url = st.secrets["database"]["url"]
engine = create_engine(db_url)

log = logging.getLogger("DB - Active metrics")


def upload_daily_active_metrics(df):
    active_amount = df.loc[df.total_harvest_pp > 0].index.size
    in_use_amount = df.loc[df.in_use].index.size

    result_df = pd.DataFrame([{
        "date": date.today(),
        "active_based_on_pp": active_amount,
        "active_based_on_in_use": in_use_amount,
    }])
    upload.commit(result_df, ACTIVE_TABLE_NAME)


@st.cache_data(ttl="1h")
def get_historical_data() -> pd.DataFrame:
    query = f"SELECT * FROM {ACTIVE_TABLE_NAME}"
    return pd.read_sql(query, engine)


@st.cache_data(ttl="1h")
def get_latest_active() -> pd.DataFrame:
    query = f"""
        SELECT *
        FROM {ACTIVE_TABLE_NAME}
        WHERE date = (SELECT MAX(date) FROM {ACTIVE_TABLE_NAME})
    """
    return pd.read_sql(query, engine)
