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

    По правилам проекта полный журнал доступен ТОЛЬКО администратору.
    Остальные роли не получают ничего (свои изменения они видят
    прямо под записью — см. get_history / «История изменений»).
    """
    if role == "admin":
        return get_all(limit, db_path)
    return []


def get_history(entity_type, entity_id, db_path=DB_PATH):
    """История изменений КОНКРЕТНОЙ записи (для блока под строкой таблицы)."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT * FROM audit_log
            WHERE entity_type = ? AND entity_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (entity_type, entity_id),
        ).fetchall()
        return [dict(r) for r in rows]


def format_row(row):
    """Человекочитаемая строка вида: 12.10 14:30 • Иванов • Изменение • Резюме №3."""
    from src.ui.theme import ACTION_LABELS, ENTITY_LABELS

    ts = str(row.get("created_at") or "")[:16]
    try:
        date_part, time_part = ts.split(" ")
        dd, mm, yyyy = date_part.split("-")
        ts = f"{dd}.{mm} {time_part}"
    except ValueError:
        pass
    action = ACTION_LABELS.get(row.get("action"), row.get("action") or "")
    entity = ENTITY_LABELS.get(row.get("entity_type"), row.get("entity_type") or "")
    text = f"{ts} • {row.get('user_login', '')} ({row.get('user_role', '')}) • {action} • {entity}"
    if row.get("entity_id") is not None:
        text += f" №{row['entity_id']}"
    if row.get("details"):
        text += f" — {row['details']}"
    return text