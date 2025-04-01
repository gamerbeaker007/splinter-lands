# run_migration.py
import os
from pathlib import Path

import toml
import subprocess


def load_database_url():
    secrets_path = Path(__file__).resolve().parent.parent / ".streamlit" / "secrets.toml"
    if not os.path.exists(secrets_path):
        raise FileNotFoundError("Missing .streamlit/secrets.toml")

    secrets = toml.load(secrets_path)
    return secrets["database"]["url"]


def run_alembic_upgrade():
    db_url = load_database_url()
    os.environ["DATABASE_URL"] = db_url
    print("Running Alembic ....")

    # Equivalent to: alembic upgrade head
    subprocess.run(["alembic", "upgrade", "head"], check=True)


if __name__ == "__main__":
    run_alembic_upgrade()
