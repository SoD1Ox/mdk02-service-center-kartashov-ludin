from src.db.connection import get_connection, DB_PATH
from src.services.audit_service import log_action


def get_all(db_path=DB_PATH):
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM employers ORDER BY id").fetchall()
        return [dict(r) for r in rows]


def create(name, inn, contact_person, phone,
           user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """INSERT INTO employers
                   (name, inn, contact_person, phone, created_by, updated_by, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (name, inn, contact_person, phone, user_login, user_login),
        )
        eid = cur.lastrowid
    log_action(user_login, user_role, "CREATE", "employer", eid,
               f"Компания: {name}", db_path)
    return eid


def update(employer_id, name, inn, contact_person, phone,
           user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute(
            """UPDATE employers
               SET name=?, inn=?, contact_person=?, phone=?,
                   updated_by=?, updated_at=CURRENT_TIMESTAMP
               WHERE id=?""",
            (name, inn, contact_person, phone, user_login, employer_id),
        )
    log_action(user_login, user_role, "UPDATE", "employer", employer_id,
               f"Компания: {name}", db_path)


def delete(employer_id, user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT name FROM employers WHERE id=?", (employer_id,)).fetchone()
        conn.execute("DELETE FROM employers WHERE id=?", (employer_id,))
    name = row["name"] if row else f"id={employer_id}"
    log_action(user_login, user_role, "DELETE", "employer", employer_id,
               f"Компания: {name}", db_path)
