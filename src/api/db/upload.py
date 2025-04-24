import sqlalchemy

from src.api.db.session import get_session
from src.utils.log_util import configure_logger

log = configure_logger(__name__)


def commit(df, table_name):
    Session = get_session()
    with Session() as session:
        try:
            # Check if table exists
            if not session.bind.dialect.has_table(session.bind.connect(), table_name):
                log.error(f"Table {table_name} does not exist. Did you forget to run Alembic migrations?")
                return

            # Upload using the session’s connection
            df.to_sql(
                name=table_name,
                con=session.connection(),
                if_exists="append",
                index=False,
                method="multi"
            )
            log.info(f"✅ Uploaded {len(df)} records to {table_name}")
        except sqlalchemy.exc.IntegrityError as e:
            log.warning("⚠️ Duplicate entry detected. Likely already inserted.")
            log.debug("Details:", exc_info=e)
        except sqlalchemy.exc.OperationalError as e:
            log.error("❌ Database operational error (e.g. table does not exist)", exc_info=e)
        except Exception as e:
            log.error("❌ Unexpected failure during database upload", exc_info=e)
