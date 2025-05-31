import importlib
import sys

import st_pages
import streamlit as st
from st_pages import get_nav_from_toml

from src.pages import (
    resource_metrics_page,
    region_metrics_page,
    region_dec_metrics_page,
    player_overview_page,
)
from src.utils import dev_mode, data_helper, data_loader_new
from src.utils.data_loader_new import safe_refresh_data
from src.utils.dev_mode import check_offline
from src.utils.log_util import configure_logger


# Optional: Reload modules during development
def reload_all():
    """Reload all src modules (for hot-reloading in development)."""
    for name in list(sys.modules):
        if name.startswith("src"):
            importlib.reload(sys.modules[name])


reload_all()  # Only needed during dev

# Configure logger
log = configure_logger(__name__)

# Page setup
st.set_page_config(page_title="SplinterLands", layout="wide")

check_offline()

# Load navigation
nav = get_nav_from_toml('.streamlit/pages.toml')
pg = st.navigation(nav)

# Dev mode tools
dev_mode.start_memory_measurements()
dev_mode.show_dev_warning()
mem_placeholder = st.empty()

# Page title
st_pages.add_page_title(pg)

# --- Refresh logic ---
if data_loader_new.is_data_stale() and not data_loader_new.is_refreshing():
    # Trigger background refresh
    safe_refresh_data()

# --- Sidebar Data Status ---
status_icon = ":large_green_circle:"
status_text = "Data Ready"

if data_loader_new.is_refreshing():
    status_icon = ":large_orange_circle:"
    status_text = "Data Refreshing..."
elif data_loader_new.is_data_stale():
    status_icon = ":large_orange_circle:"
    status_text = "Data Stale (will refresh in background)"

# --- Last updated logic ---
last_updated = data_helper.get_last_updated()
if not last_updated:
    st.warning("""
    **No data found yet.**

    The application may still be fetching new data. Please refresh in a few minutes.
    You can also check the sidebar for data status information.
    """)
    st.stop()
else:
    formatted_time = last_updated.strftime("%Y-%m-%d %H:%M:%S")

# --- Sidebar Summary ---
st.sidebar.markdown(f"""
**ℹ️ Data Info**

{status_icon} <b>{status_text}</b><br>
📦 Cached as of <code>{formatted_time}</code></br>
⚡ Player overview fetched on demand
""", unsafe_allow_html=True)
# Render selected page
with st.empty().container():
    if pg.title == "Resource Metrics":
        resource_metrics_page.get_page()
    elif pg.title == "Region Metrics":
        region_metrics_page.get_page()
    elif pg.title == "Region DEC Metrics":
        region_dec_metrics_page.get_page()
    elif pg.title == "Player Overview":
        player_overview_page.get_page()

# Memory usage display
dev_mode.show_memory_output(mem_placeholder)
