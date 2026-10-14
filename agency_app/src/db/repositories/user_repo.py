from src.db.connection import get_connection, DB_PATH


def find_by_credentials(login, password, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT id, login, role FROM users WHERE login=? AND password_hash=?",
            (login, password),
        ).fetchone()
        return dict(row) if row else None