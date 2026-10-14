from src.db.repositories import user_repo, attempt_repo
from src.db.connection import DB_PATH

MAX_ATTEMPTS = 3


class AuthService:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.attempts_left = MAX_ATTEMPTS

    def login(self, login, password):
        if not login or not password:
            return False, "Заполните поля", self.attempts_left

        user = user_repo.find_by_credentials(login, password, self.db_path)
        if user:
            attempt_repo.log(login, True, self.db_path)
            self.attempts_left = MAX_ATTEMPTS
            return True, user, self.attempts_left      # ← возвращаем dict

        attempt_repo.log(login, False, self.db_path)
        self.attempts_left -= 1
        if self.attempts_left <= 0:
            return False, "Попытки исчерпаны", 0
        return False, "Неверный логин или пароль", self.attempts_left