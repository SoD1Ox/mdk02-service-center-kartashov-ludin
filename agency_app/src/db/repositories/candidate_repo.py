from src.db.connection import get_connection, DB_PATH
from src.services.audit_service import log_action


def get_all(db_path=DB_PATH):
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM candidates ORDER BY id").fetchall()
        return [dict(r) for r in rows]


def create(full_name, phone, email, user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """INSERT INTO candidates (full_name, phone, email, created_by, updated_by, updated_at)
               VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (full_name, phone, email, user_login, user_login),
        )
        cid = cur.lastrowid
    log_action(user_login, user_role, "CREATE", "candidate", cid,
               f"ФИО: {full_name}", db_path)
    return cid


def update(candidate_id, full_name, phone, email,
           user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute(
            """UPDATE candidates
               SET full_name=?, phone=?, email=?, updated_by=?, updated_at=CURRENT_TIMESTAMP
               WHERE id=?""",
            (full_name, phone, email, user_login, candidate_id),
        )
    log_action(user_login, user_role, "UPDATE", "candidate", candidate_id,
               f"ФИО: {full_name}", db_path)


def delete(candidate_id, user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT full_name FROM candidates WHERE id=?", (candidate_id,)
        ).fetchone()
        conn.execute("DELETE FROM candidates WHERE id=?", (candidate_id,))
    name = row["full_name"] if row else f"id={candidate_id}"
    log_action(user_login, user_role, "DELETE", "candidate", candidate_id,
               f"ФИО: {name}", db_path)
