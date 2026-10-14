"""
Сервис истории статусов.

BR-02: каждое изменение статуса отклика или вакансии
фиксируется в таблице status_history.
"""
from src.db.connection import get_connection, DB_PATH


def log_status_change(
    entity_type: str,
    entity_id: int,
    old_status: str,
    new_status: str,
    changed_by: str = "system",
    db_path=DB_PATH,
):
    """
    entity_type: 'response' или 'vacancy'
    """
    with get_connection(db_path) as conn:
        conn.execute(
            """
            INSERT INTO status_history
                (entity_type, entity_id, old_status, new_status, changed_by)
            VALUES (?, ?, ?, ?, ?)
            """,
            (entity_type, entity_id, old_status, new_status, changed_by),
        )


def get_history(entity_type: str, entity_id: int, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """
            SELECT old_status, new_status, changed_by, changed_at
            FROM status_history
            WHERE entity_type=? AND entity_id=?
            ORDER BY changed_at
            """,
            (entity_type, entity_id),
        ).fetchall()
        return [dict(r) for r in rows]