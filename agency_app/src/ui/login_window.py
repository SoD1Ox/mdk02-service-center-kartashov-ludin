import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.services.auth_service import AuthService
from src.db.connection import init_db
from src.ui.main_window import MainWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.auth = AuthService()
        self.setWindowTitle("Кадровое агентство")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)

        title = QLabel("ИС «Кадровое агентство»")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addWidget(QLabel("Логин:"))
        self.login = QLineEdit()
        self.login.setPlaceholderText("Введите логин")
        layout.addWidget(self.login)

        layout.addWidget(QLabel("Пароль:"))
        self.password = QLineEdit()
        self.password.setPlaceholderText("Введите пароль")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        btn = QPushButton("Войти")
        btn.clicked.connect(self.on_login)
        layout.addWidget(btn)

        self.attempts = QLabel(f"Осталось попыток: {self.auth.attempts_left}")
        self.attempts.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.attempts)

        self.setLayout(layout)

    def on_login(self):
        ok, result, left = self.auth.login(
            self.login.text().strip(),
            self.password.text().strip(),
        )
        self.attempts.setText(f"Осталось попыток: {left}")

        if ok:
            QMessageBox.information(self, "Успех", f"Добро пожаловать, {result['login']}!")
            self.open_main_window(result)
        elif left <= 0:
            QMessageBox.critical(self, "Блокировка", result)
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", result)

    def open_main_window(self, user):
        from src.services.audit_service import log_action
        log_action(user["login"], user["role"], "LOGIN", "user", user["id"],
                   "Вход в систему")
        self.main_window = MainWindow(user)
        self.main_window.show()
        self.close()


def run():
    init_db()
    app = QApplication(sys.argv)
    w = LoginWindow()
    w.show()
    sys.exit(app.exec_())