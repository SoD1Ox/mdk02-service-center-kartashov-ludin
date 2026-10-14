from src.db.connection import get_connection, DB_PATH


def get_all(db_path=DB_PATH):
    with get_connection(db_path) as conn:
        rows = conn.execute("""
            SELECT id, response_id, commission, tax, closed_at
            FROM deals
        """).fetchall()
        return [dict(r) for r in rows]


def create(response_id, commission, tax, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO deals (response_id, commission, tax) VALUES (?, ?, ?)",
            (response_id, commission, tax),
        )
        return cur.lastrowid


def update(deal_id, response_id, commission, tax, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE deals SET response_id=?, commission=?, tax=? WHERE id=?",
            (response_id, commission, tax, deal_id),
        )


def delete(deal_id, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM deals WHERE id=?", (deal_id,))