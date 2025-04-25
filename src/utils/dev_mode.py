import os
import tracemalloc
from pathlib import Path

import pandas as pd
import streamlit as st
from alembic import command
from alembic.config import Config

from src.utils.log_util import configure_logger

db_url = st.secrets["database"]["url"]
log = configure_logger(__name__)
project_root = Path.cwd()


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


def show_memory_output(placeholder):
    if st.secrets.get("settings", {}).get("debug_memory", False):
        with st.sidebar.expander("🧠 Memory Debug Mode: ON", expanded=True):
            current, peak = tracemalloc.get_traced_memory()
            st.write(f"Current memory usage: {current / 1024 / 1024:.2f} MB")
            st.write(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")

        with placeholder.container():
            if st.button("🔍 Debug Memory"):
                snapshot = tracemalloc.take_snapshot()
                stats = snapshot.statistics("lineno")[:10]
                data = []
                for stat in stats:
                    full_path = Path(stat.traceback[0].filename)
                    try:
                        # Try to make the path relative to your project root
                        short_path = full_path.relative_to(project_root)
                    except ValueError:
                        # If it's not inside the project folder, just use the file name
                        short_path = full_path.name
                    data.append({
                        "File": f"{short_path}:{stat.traceback[0].lineno}",
                        "Size (MiB)": f"{stat.size / 1024 / 1024:.2f}",
                        "Count": stat.count,
                        "Average (KiB)": f"{stat.size / stat.count / 1024:.2f}" if stat.count > 0 else "-"
                    })

                df = pd.DataFrame(data)

                # Show it in a nice Streamlit table
                st.markdown("### 🔍 Top Memory Usage")
                st.dataframe(df, use_container_width=True)


def start_memory_measurements():
    if st.secrets.get("settings", {}).get("debug_memory", False):
        tracemalloc.start()
