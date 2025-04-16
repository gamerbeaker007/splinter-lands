import sqlalchemy
import streamlit as st
from sqlalchemy import create_engine

from src.utils.log_util import configure_logger

# Same URL as in alembic.ini
db_url = st.secrets["database"]["url"]
engine = create_engine(db_url)

log = configure_logger(__name__)


def commit(df, table_name):
    if not engine.dialect.has_table(engine.connect(), table_name):
        log.error(f"Table {table_name} does not exist. Did you forget to run Alembic migrations?")
        return

    try:
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="append",  # append rows to existing table
            index=False,
            method="multi"  # batch insert for performance
        )
        log.info(f"✅ Uploaded {len(df)} records to {table_name}")
    except sqlalchemy.exc.IntegrityError as e:
        # This usually happens when a UNIQUE constraint is violated
        log.warning("⚠️ Duplicate entry detected. Likely already inserted.")
        log.debug("Details:", exc_info=e)
    except sqlalchemy.exc.OperationalError as e:
        log.error("❌ Database operational error (e.g. table does not exist)", exc_info=e)
    except Exception as e:
        log.error("❌ Unexpected failure during database upload", exc_info=e)
