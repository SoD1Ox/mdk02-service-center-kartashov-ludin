from src.db.connection import get_connection, DB_PATH
from src.services.audit_service import log_action
from src.services.status_service import log_status_change


def get_all(db_path=DB_PATH):
    with get_connection(db_path) as conn:
        rows = conn.execute("""
            SELECT v.id, v.employer_id, e.name AS employer_name,
                   v.title, v.requirements, v.salary, v.status
            FROM vacancies v
            LEFT JOIN employers e ON e.id = v.employer_id
        """).fetchall()
        return [dict(r) for r in rows]


def create(employer_id, title, requirements, salary,
           user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO vacancies (employer_id, title, requirements, salary) VALUES (?, ?, ?, ?)",
            (employer_id, title, requirements, salary),
        )
        vid = cur.lastrowid
    log_action(user_login, user_role, "CREATE", "vacancy", vid,
               f"Должность: {title}", db_path)
    log_status_change("vacancy", vid, None, "Открыта", user_login, db_path)
    return vid


def update(vacancy_id, employer_id, title, requirements, salary, status,
           user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT status FROM vacancies WHERE id=?", (vacancy_id,)
        ).fetchone()
        old_status = row["status"] if row else None

        conn.execute(
            "UPDATE vacancies SET employer_id=?, title=?, requirements=?, salary=?, status=? WHERE id=?",
            (employer_id, title, requirements, salary, status, vacancy_id),
        )
    log_action(user_login, user_role, "UPDATE", "vacancy", vacancy_id,
               f"Должность: {title}, статус: {status}", db_path)
    if old_status != status:
        log_status_change("vacancy", vacancy_id, old_status, status,
                          user_login, db_path)


def delete(vacancy_id, user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM vacancies WHERE id=?", (vacancy_id,))
    log_action(user_login, user_role, "DELETE", "vacancy", vacancy_id,
               None, db_path)