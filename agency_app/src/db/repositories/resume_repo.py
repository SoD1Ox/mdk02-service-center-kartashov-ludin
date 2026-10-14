from src.db.connection import get_connection, DB_PATH


def get_all(db_path=DB_PATH):
    with get_connection(db_path) as conn:
        rows = conn.execute("""
            SELECT r.id, r.candidate_id, c.full_name AS candidate_name,
                   r.title, r.experience, r.education
            FROM resumes r
            JOIN candidates c ON c.id = r.candidate_id
        """).fetchall()
        return [dict(r) for r in rows]


def create(candidate_id, title, experience, education, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO resumes (candidate_id, title, experience, education) VALUES (?, ?, ?, ?)",
            (candidate_id, title, experience, education),
        )
        return cur.lastrowid


def update(resume_id, candidate_id, title, experience, education, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE resumes SET candidate_id=?, title=?, experience=?, education=? WHERE id=?",
            (candidate_id, title, experience, education, resume_id),
        )


def delete(resume_id, db_path=DB_PATH):
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM resumes WHERE id=?", (resume_id,))