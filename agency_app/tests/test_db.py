import os
import tempfile
import sqlite3
import pytest

from src.db.connection import init_db, get_connection
from src.db.seed import seed_data


@pytest.fixture
def tmp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path, with_seed=True)
    yield path
    os.remove(path)


# --- ОГРАНИЧЕНИЯ ---

def test_unique_login(tmp_db):
    with pytest.raises(sqlite3.IntegrityError):
        with get_connection(tmp_db) as conn:
            conn.execute(
                "INSERT INTO users (login, password_hash) VALUES ('admin', 'x')"
            )


def test_unique_email(tmp_db):
    with pytest.raises(sqlite3.IntegrityError):
        with get_connection(tmp_db) as conn:
            conn.execute(
                "INSERT INTO candidates (full_name, email) VALUES ('Тест', 'ivanov@example.com')"
            )


def test_check_role(tmp_db):
    with pytest.raises(sqlite3.IntegrityError):
        with get_connection(tmp_db) as conn:
            conn.execute(
                "INSERT INTO users (login, password_hash, role) VALUES ('x', 'y', 'superadmin')"
            )


def test_check_salary_negative(tmp_db):
    with pytest.raises(sqlite3.IntegrityError):
        with get_connection(tmp_db) as conn:
            conn.execute(
                "INSERT INTO vacancies (employer_id, title, salary) VALUES (1, 'X', -100)"
            )


def test_check_status_vacancy(tmp_db):
    with pytest.raises(sqlite3.IntegrityError):
        with get_connection(tmp_db) as conn:
            conn.execute(
                "INSERT INTO vacancies (employer_id, title, status) VALUES (1, 'X', 'Неверный')"
            )


def test_not_null_full_name(tmp_db):
    with pytest.raises(sqlite3.IntegrityError):
        with get_connection(tmp_db) as conn:
            conn.execute("INSERT INTO candidates (phone) VALUES ('+7')")


# --- СВЯЗИ ---

def test_fk_resume_candidate(tmp_db):
    with pytest.raises(sqlite3.IntegrityError):
        with get_connection(tmp_db) as conn:
            conn.execute(
                "INSERT INTO resumes (candidate_id, title) VALUES (9999, 'X')"
            )


def test_fk_vacancy_employer(tmp_db):
    with pytest.raises(sqlite3.IntegrityError):
        with get_connection(tmp_db) as conn:
            conn.execute(
                "INSERT INTO vacancies (employer_id, title) VALUES (9999, 'X')"
            )


def test_fk_response_candidate(tmp_db):
    with pytest.raises(sqlite3.IntegrityError):
        with get_connection(tmp_db) as conn:
            conn.execute(
                "INSERT INTO responses (candidate_id, vacancy_id) VALUES (9999, 1)"
            )


def test_cascade_delete_resume(tmp_db):
    with get_connection(tmp_db) as conn:
        conn.execute("DELETE FROM candidates WHERE id=1")
        rows = conn.execute("SELECT COUNT(*) FROM resumes WHERE candidate_id=1").fetchone()
        assert rows[0] == 0


def test_unique_response(tmp_db):
    with get_connection(tmp_db) as conn:
        conn.execute("INSERT INTO responses (candidate_id, vacancy_id) VALUES (1, 3)")
    with pytest.raises(sqlite3.IntegrityError):
        with get_connection(tmp_db) as conn:
            conn.execute("INSERT INTO responses (candidate_id, vacancy_id) VALUES (1, 3)")


# --- ДАННЫЕ ---

def test_seed_users(tmp_db):
    with get_connection(tmp_db) as conn:
        rows = conn.execute("SELECT COUNT(*) FROM users").fetchone()
        assert rows[0] >= 2


def test_seed_skills(tmp_db):
    with get_connection(tmp_db) as conn:
        rows = conn.execute("SELECT COUNT(*) FROM skills").fetchone()
        assert rows[0] >= 5


def test_seed_candidates(tmp_db):
    with get_connection(tmp_db) as conn:
        rows = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()
        assert rows[0] >= 3