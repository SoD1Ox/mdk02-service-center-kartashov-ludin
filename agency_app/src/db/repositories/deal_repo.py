from src.db.connection import get_connection, DB_PATH
from src.services.audit_service import log_action


def get_all(db_path=DB_PATH):
    with get_connection(db_path) as conn:
        rows = conn.execute("""
            SELECT d.id, d.response_id, d.commission, d.tax, d.closed_at,
                   d.created_by, d.updated_by, d.updated_at,
                   c.full_name AS candidate_name, v.title AS vacancy_title,
                   e.name AS employer_name
            FROM deals d
            LEFT JOIN responses r ON r.id = d.response_id
            LEFT JOIN candidates c ON c.id = r.candidate_id
            LEFT JOIN vacancies v ON v.id = r.vacancy_id
            LEFT JOIN employers e ON e.id = v.employer_id
            ORDER BY d.id
        """).fetchall()
        return [dict(r) for r in rows]


def create(response_id, commission, tax,
           user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """INSERT INTO deals
                   (response_id, commission, tax, created_by, updated_by, updated_at)
               VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (response_id, commission, tax, user_login, user_login),
        )
        did = cur.lastrowid
    log_action(user_login, user_role, "CREATE", "deal", did,
               f"Комиссия: {commission} ₽ по отклику #{response_id}", db_path)
    return did


def update(deal_id, response_id, commission, tax,
           user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute(
            """UPDATE deals
               SET response_id=?, commission=?, tax=?,
                   updated_by=?, updated_at=CURRENT_TIMESTAMP
               WHERE id=?""",
            (response_id, commission, tax, user_login, deal_id),
        )
    log_action(user_login, user_role, "UPDATE", "deal", deal_id,
               f"Комиссия: {commission} ₽", db_path)


def delete(deal_id, user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM deals WHERE id=?", (deal_id,))
    log_action(user_login, user_role, "DELETE", "deal", deal_id,
               None, db_path)
