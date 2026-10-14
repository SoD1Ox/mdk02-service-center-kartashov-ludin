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


def _migrate(conn):
    """
    Простая миграция «на лету»: добавляет отсутствующие столбцы
    created_by / updated_by / updated_at в бизнес-таблицы.
    Нужно, чтобы старые файлы agency.db работали с новой схемой.
    """
    tables = ["candidates", "resumes", "skills", "employers",
              "vacancies", "responses", "deals"]
    new_cols = ["created_by TEXT", "updated_by TEXT", "updated_at TIMESTAMP"]
    for t in tables:
        existing = {r["name"] for r in conn.execute(f"PRAGMA table_info({t})")}
        for col in new_cols:
            name = col.split()[0]
            if name not in existing:
                conn.execute(f"ALTER TABLE {t} ADD COLUMN {col}")


def init_db(db_path=DB_PATH, with_seed=True):
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = f.read()

    with get_connection(db_path) as conn:
        conn.executescript(schema)
        _migrate(conn)
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    if with_seed and count == 0:
        from src.db.seed import seed_data
        seed_data(db_path)