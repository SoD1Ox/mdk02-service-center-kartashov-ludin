import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.environ.get("AGENCY_DB", "agency.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


@contextmanager
def get_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path=DB_PATH, with_seed=True):
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = f.read()

    with get_connection(db_path) as conn:
        conn.executescript(schema)
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    if with_seed and count == 0:
        from src.db.seed import seed_data
        seed_data(db_path)