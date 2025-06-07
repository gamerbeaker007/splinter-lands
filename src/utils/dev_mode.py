import os
import tracemalloc
from pathlib import Path

import pandas as pd
import streamlit as st

from src.utils.log_util import configure_logger

db_url = st.secrets["database"]["url"]
log = configure_logger(__name__)
project_root = Path.cwd()


def show_dev_warning():
    if st.secrets.get("settings", {}).get("dev_mode", False):
        st.warning("""
        **You're viewing a development version of the site.**

        This environment is used for experimenting and testing new features.

        Feel free to explore, but please note that things may be unstable or change frequently.
        For the stable experience, visit the main site:
        [https://land.spl-stats.com/](https://land.spl-stats.com/)
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


def check_offline():
    if st.secrets.get("settings", {}).get("offline", False):
        st.warning("""
        **⚠️ This page is offline...**

        But don’t worry — we’re just moving to a better home (with fewer *Oh No!* screens 🤞😄).

        👉 Visit the new site here: [https://land.spl-stats.com/](https://land.spl-stats.com/)
        """)

        st.markdown(
            """
            <div style="text-align: center;">
                <img width="100px" src="https://media.tenor.com/YCM_QtL_MV8AAAAi/14.gif" alt="Don't be sad" width="300">
            </div>
            """,
            unsafe_allow_html=True
        )

        st.stop()


def get_version():
    if os.getenv('APP_VERSION'):
        version = os.getenv('APP_VERSION')
    else:
        version = "SNAPSHOT"
    return version
