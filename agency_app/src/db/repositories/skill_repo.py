from src.db.connection import get_connection, DB_PATH


from src.db.connection import get_connection, DB_PATH


def get_all(db_path=DB_PATH):
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM skills").fetchall()
        return [dict(r) for r in rows]


def create(name, category, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO skills (name, category) VALUES (?, ?)",
            (name, category),
        )
        return cur.lastrowid


def update(skill_id, name, category, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE skills SET name=?, category=? WHERE id=?",
            (name, category, skill_id),
        )


def delete(skill_id, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM skills WHERE id=?", (skill_id,))
        