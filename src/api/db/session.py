import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@st.cache_resource
def get_engine():
    # Same URL as in alembic.ini
    db_url = st.secrets["database"]["url"]
    return create_engine(db_url)


@st.cache_resource
def get_session():
    engine = get_engine()
    return sessionmaker(bind=engine)
