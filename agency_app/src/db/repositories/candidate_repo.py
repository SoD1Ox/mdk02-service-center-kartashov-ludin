from src.db.connection import get_connection, DB_PATH
from src.services.audit_service import log_action


def get_all(db_path=DB_PATH):
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM candidates").fetchall()
        return [dict(r) for r in rows]


def create(full_name, phone, email, user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO candidates (full_name, phone, email) VALUES (?, ?, ?)",
            (full_name, phone, email),
        )
        cid = cur.lastrowid
    log_action(user_login, user_role, "CREATE", "candidate", cid,
               f"ФИО: {full_name}", db_path)
    return cid


def update(candidate_id, full_name, phone, email,
           user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE candidates SET full_name=?, phone=?, email=? WHERE id=?",
            (full_name, phone, email, candidate_id),
        )
    log_action(user_login, user_role, "UPDATE", "candidate", candidate_id,
               f"ФИО: {full_name}", db_path)


def delete(candidate_id, user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM candidates WHERE id=?", (candidate_id,))
    log_action(user_login, user_role, "DELETE", "candidate", candidate_id,
               None, db_path)