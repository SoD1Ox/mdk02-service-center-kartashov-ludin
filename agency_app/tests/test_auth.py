import os
import tempfile
import pytest

from src.db.connection import init_db
from src.services.auth_service import AuthService, MAX_ATTEMPTS


@pytest.fixture
def tmp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    yield path
    os.remove(path)


def test_success(tmp_db):
    svc = AuthService(tmp_db)
    ok, user, left = svc.login("admin", "admin123")
    assert ok is True
    assert user["login"] == "admin"
    assert user["role"] == "admin"


def test_fail_decreases(tmp_db):
    svc = AuthService(tmp_db)
    ok, msg, left = svc.login("admin", "wrong")
    assert ok is False
    assert left == MAX_ATTEMPTS - 1


def test_three_fails_block(tmp_db):
    svc = AuthService(tmp_db)
    for _ in range(MAX_ATTEMPTS):
        ok, msg, left = svc.login("admin", "wrong")
    assert left == 0