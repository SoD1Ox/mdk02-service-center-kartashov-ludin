"""Аудит действий пользователей."""
from src.db.connection import get_connection, DB_PATH


def log_action(user_login, user_role, action, entity_type, entity_id=None,
               details=None, db_path=DB_PATH):
    """
    action: CREATE / UPDATE / DELETE / LOGIN
    entity_type: 'candidate' / 'vacancy' / 'response' / 'deal' / 'user' и т.д.
    """
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO audit_log
                (user_login, user_role, action, entity_type, entity_id, details)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_login, user_role, action, entity_type, entity_id, details),
        )


def get_all(limit=500, db_path=DB_PATH):
    """Всё — для admin."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT * FROM audit_log
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_for_roles(roles, limit=500, db_path=DB_PATH):
    """Фильтр по ролям — для manager (видит director + manager)."""
    placeholders = ",".join("?" * len(roles))
    with get_connection(db_path) as conn:
        rows = conn.execute(
            f"""
            SELECT * FROM audit_log
            WHERE user_role IN ({placeholders})
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (*roles, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def get_for_user(user_login, limit=500, db_path=DB_PATH):
    """Только действия конкретного пользователя."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT * FROM audit_log
            WHERE user_login = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (user_login, limit),
        ).fetchall()
        return [dict(r) for r in rows]