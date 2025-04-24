import importlib
import sys

import streamlit as st
from st_pages import get_nav_from_toml, add_page_title

from src.pages import resource_metrics_page, region_metrics_page, player_overview_page
from src.utils import dev_mode
from src.utils.data_loader import is_data_stale, is_refreshing, safe_refresh_data
from src.utils.log_util import configure_logger


def reload_all():
    """Reload all imported modules. workaround for streamlit to load also changed modules"""
    for module_name in list(sys.modules.keys()):
        # Reload only modules that are not built-in and not part of the standard library
        if module_name.startswith("src"):
            importlib.reload(sys.modules[module_name])


reload_all()

log = configure_logger(__name__)

st.set_page_config(page_title="SplinterLands", layout="wide")

nav = get_nav_from_toml('.streamlit/pages.toml')
pg = st.navigation(nav)

dev_mode.start_memory_measurements()
dev_mode.show_dev_warning()
mem_placeholder = st.empty()

add_page_title(pg)

# Check if we need to refresh
if is_data_stale() and not is_refreshing():
    st.sidebar.markdown(":large_orange_circle: Refreshing data in background...")
    safe_refresh_data()

# Sidebar status
if is_refreshing():
    st.sidebar.markdown(":large_orange_circle: Data Refreshing...")
elif is_data_stale():
    st.sidebar.markdown(":large_orange_circle: Data Stale")
else:
    st.sidebar.markdown(":large_green_circle: Data Ready")


placeholder = st.empty()

# Dynamically call the page-specific function based on the selected page
if pg.title == "Resource Metrics":
    with placeholder.container():
        resource_metrics_page.get_page()
if pg.title == "Region Metrics":
    with placeholder.container():
        region_metrics_page.get_page()
if pg.title == "Player Overview":
    with placeholder.container():
        player_overview_page.get_page()


dev_mode.show_memory_output(mem_placeholder)