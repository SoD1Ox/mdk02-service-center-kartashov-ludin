"""Аудит действий пользователей."""
from src.db.connection import get_connection, DB_PATH

# Роли, которые видит менеджер в журнале (чужие действия выше по иерархии — тоже)
MANAGER_VISIBLE_ROLES = ("admin", "manager", "director")


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
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_for_roles(roles, limit=500, db_path=DB_PATH):
    """Фильтр по ролям — для manager (видит admin, director, manager)."""
    placeholders = ",".join("?" * len(roles))
    with get_connection(db_path) as conn:
        rows = conn.execute(
            f"""
            SELECT * FROM audit_log
            WHERE user_role IN ({placeholders})
            ORDER BY created_at DESC, id DESC
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
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (user_login, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def visible_rows(role, login, limit=500, db_path=DB_PATH):
    """
    Единая точка: какие записи журнала видит пользователь.

    admin     — все действия всех пользователей;
    manager   — действия администратора, директора, менеджеров и свои;
    director  — только свои действия;
    остальные — только свои.
    """
    if role == "admin":
        return get_all(limit, db_path)
    if role == "manager":
        return get_for_roles(MANAGER_VISIBLE_ROLES, limit, db_path)
    return get_for_user(login, limit, db_path)