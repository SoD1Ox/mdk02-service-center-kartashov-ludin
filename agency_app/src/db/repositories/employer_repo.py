from src.db.connection import get_connection, DB_PATH


def get_all(db_path=DB_PATH):
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM employers").fetchall()
        return [dict(r) for r in rows]


def create(name, inn, contact_person, phone, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO employers (name, inn, contact_person, phone) VALUES (?, ?, ?, ?)",
            (name, inn, contact_person, phone),
        )
        return cur.lastrowid


def update(employer_id, name, inn, contact_person, phone, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE employers SET name=?, inn=?, contact_person=?, phone=? WHERE id=?",
            (name, inn, contact_person, phone, employer_id),
        )


def delete(employer_id, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM employers WHERE id=?", (employer_id,))