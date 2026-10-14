from src.db.connection import get_connection, DB_PATH
from src.services.audit_service import log_action


def get_all(db_path=DB_PATH):
    with get_connection(db_path) as conn:
        rows = conn.execute("""
            SELECT r.id, r.candidate_id, c.full_name AS candidate_name,
                   r.title, r.experience, r.education,
                   r.created_by, r.updated_by, r.updated_at
            FROM resumes r
            JOIN candidates c ON c.id = r.candidate_id
            ORDER BY r.id
        """).fetchall()
        return [dict(r) for r in rows]


def create(candidate_id, title, experience, education,
           user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """INSERT INTO resumes
                   (candidate_id, title, experience, education,
                    created_by, updated_by, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (candidate_id, title, experience, education, user_login, user_login),
        )
        rid = cur.lastrowid
    log_action(user_login, user_role, "CREATE", "resume", rid,
               f"Должность: {title}", db_path)
    return rid


def update(resume_id, candidate_id, title, experience, education,
           user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute(
            """UPDATE resumes
               SET candidate_id=?, title=?, experience=?, education=?,
                   updated_by=?, updated_at=CURRENT_TIMESTAMP
               WHERE id=?""",
            (candidate_id, title, experience, education, user_login, resume_id),
        )
    log_action(user_login, user_role, "UPDATE", "resume", resume_id,
               f"Должность: {title}", db_path)


def delete(resume_id, user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT title FROM resumes WHERE id=?", (resume_id,)
        ).fetchone()
        conn.execute("DELETE FROM resumes WHERE id=?", (resume_id,))
    title = row["title"] if row else f"id={resume_id}"
    log_action(user_login, user_role, "DELETE", "resume", resume_id,
               f"Должность: {title}", db_path)
