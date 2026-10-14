from src.db.connection import get_connection, DB_PATH


def log(login, success, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO attempts (login, success) VALUES (?, ?)",
            (login, 1 if success else 0),
        )


def count_failed(login, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM attempts WHERE login=? AND success=0",
            (login,),
        ).fetchone()
        return row[0]