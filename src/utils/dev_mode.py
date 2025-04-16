import os

import streamlit as st
from alembic import command
from alembic.config import Config

from src.utils.log_util import configure_logger

db_url = st.secrets["database"]["url"]
log = configure_logger(__name__)


def run_migrations():
    alembic_cfg = Config("alembic.ini")
    os.environ["DATABASE_URL"] = db_url
    os.environ["DISABLE_ALEMBIC_LOGGING"] = "1"

    log.info("Running Alembic ....")
    command.upgrade(alembic_cfg, "head")


def show_dev_warning():
    if db_url == "sqlite:///app.db":
        run_migrations()
        st.warning("""
        You're visiting a development version of the site.

        Historical data will be reset on each reboot, and test data may be present.

        Feel free to explore here, but for accurate and persistent data,
        visit the main page: https://splinter-lands.streamlit.app/
        """)
