# create_revision.py
import os
import sys
from pathlib import Path

import toml
import subprocess


def load_database_url():
    secrets_path = Path(__file__).resolve().parent.parent / ".streamlit" / "secrets.toml"
    if not os.path.exists(secrets_path):
        raise FileNotFoundError("Missing .streamlit/secrets.toml")

    secrets = toml.load(secrets_path)
    return secrets["database"]["url"]


def create_alembic_revision(message: str):
    db_url = load_database_url()
    os.environ["DATABASE_URL"] = db_url
    print(f"Creating Alembic revision with message: '{message}'")
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", message], check=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_revision.py 'your message here'")
        sys.exit(1)

    revision_message = " ".join(sys.argv[1:])
    create_alembic_revision(revision_message)
