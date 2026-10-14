from src.db.connection import get_connection, DB_PATH
from src.services.audit_service import log_action
from src.services.status_service import log_status_change


def get_all(db_path=DB_PATH):
    with get_connection(db_path) as conn:
        rows = conn.execute("""
            SELECT r.id, r.candidate_id, c.full_name AS candidate_name,
                   r.vacancy_id, v.title AS vacancy_title, r.status
            FROM responses r
            LEFT JOIN candidates c ON c.id = r.candidate_id
            LEFT JOIN vacancies v ON v.id = r.vacancy_id
        """).fetchall()
        return [dict(r) for r in rows]


def create(candidate_id, vacancy_id, status="На рассмотрении",
           user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO responses (candidate_id, vacancy_id, status) VALUES (?, ?, ?)",
            (candidate_id, vacancy_id, status),
        )
        rid = cur.lastrowid
    log_action(user_login, user_role, "CREATE", "response", rid, None, db_path)
    log_status_change("response", rid, None, status, user_login, db_path)
    return rid


def update(response_id, candidate_id, vacancy_id, status,
           user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT status FROM responses WHERE id=?", (response_id,)
        ).fetchone()
        old_status = row["status"] if row else None

        conn.execute(
            "UPDATE responses SET candidate_id=?, vacancy_id=?, status=? WHERE id=?",
            (candidate_id, vacancy_id, status, response_id),
        )
    log_action(user_login, user_role, "UPDATE", "response", response_id,
               f"Статус: {status}", db_path)
    if old_status != status:
        log_status_change("response", response_id, old_status, status,
                          user_login, db_path)


def delete(response_id, user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM responses WHERE id=?", (response_id,))
    log_action(user_login, user_role, "DELETE", "response", response_id,
               None, db_path)