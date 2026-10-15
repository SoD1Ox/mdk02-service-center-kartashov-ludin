from src.db.connection import get_connection, DB_PATH


def find_by_credentials(login, password, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT id, login, role FROM users WHERE login=? AND password_hash=?",
            (login, password),
        ).fetchone()
        return dict(row) if row else None

def get_candidate_id_by_login(login, db_path=DB_PATH):
    """Логическая связь: учётная запись соискателя -> его карточка кандидата."""
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT id FROM candidates WHERE email LIKE ? || '@%'", (login,)
        ).fetchone()
        return row[0] if row else None


def get_employer_id_by_name(login, db_path=DB_PATH):
    """Логическая связь: работодатель привязан к компании через email
    контактного лица вида login@company (например employer@romashka.ru)."""
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT id FROM employers WHERE contact_person LIKE ? || '@%'",
            (login,),
        ).fetchone()
        return row[0] if row else None
