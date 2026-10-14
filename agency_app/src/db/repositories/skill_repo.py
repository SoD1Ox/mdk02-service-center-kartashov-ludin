from src.db.connection import get_connection, DB_PATH
from src.services.audit_service import log_action


def get_all(db_path=DB_PATH):
    with get_connection(db_path) as conn:
        rows = conn.execute("SELECT * FROM skills ORDER BY id").fetchall()
        return [dict(r) for r in rows]


def create(name, category, user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """INSERT INTO skills (name, category, created_by, updated_by, updated_at)
               VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (name, category, user_login, user_login),
        )
        sid = cur.lastrowid
    log_action(user_login, user_role, "CREATE", "skill", sid,
               f"Навык: {name}", db_path)
    return sid


def update(skill_id, name, category, user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute(
            """UPDATE skills
               SET name=?, category=?, updated_by=?, updated_at=CURRENT_TIMESTAMP
               WHERE id=?""",
            (name, category, user_login, skill_id),
        )
    log_action(user_login, user_role, "UPDATE", "skill", skill_id,
               f"Навык: {name}", db_path)


def delete(skill_id, user_login="system", user_role="system", db_path=DB_PATH):
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT name FROM skills WHERE id=?", (skill_id,)).fetchone()
        conn.execute("DELETE FROM skills WHERE id=?", (skill_id,))
    name = row["name"] if row else f"id={skill_id}"
    log_action(user_login, user_role, "DELETE", "skill", skill_id,
               f"Навык: {name}", db_path)
