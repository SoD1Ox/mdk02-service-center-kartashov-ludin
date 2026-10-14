import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox, QFrame,
)

from src.services.auth_service import AuthService
from src.db.connection import init_db
from src.ui.main_window import MainWindow
from src.ui.theme import login_qss


DEMO_HINT = ("Демо-доступы: admin/admin123, manager/manager123, "
             "director/director123, employer/employer123, candidate/candidate123")


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.auth = AuthService()
        self.setWindowTitle("Кадровое агентство — вход")
        self.setFixedSize(460, 420)
        self.setStyleSheet(login_qss())

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)

        card = QFrame()
        card.setObjectName("LoginCard")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(34, 28, 34, 24)
        lay.setSpacing(10)

        title = QLabel("ИС «Кадровое агентство»")
        title.setObjectName("LoginTitle")
        title.setAlignment(Qt.AlignCenter)
        lay.addWidget(title)

        sub = QLabel("Вход в систему учёта кандидатов и вакансий")
        sub.setObjectName("LoginSub")
        sub.setAlignment(Qt.AlignCenter)
        lay.addWidget(sub)

        lay.addSpacing(8)
        lay.addWidget(QLabel("Логин"))
        self.login = QLineEdit()
        self.login.setPlaceholderText("Введите логин")
        lay.addWidget(self.login)

        lay.addWidget(QLabel("Пароль"))
        self.password = QLineEdit()
        self.password.setPlaceholderText("Введите пароль")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.returnPressed.connect(self.on_login)
        lay.addWidget(self.password)

        lay.addSpacing(6)
        btn = QPushButton("Войти")
        btn.setObjectName("LoginBtn")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.on_login)
        lay.addWidget(btn)

        self.attempts = QLabel(f"Осталось попыток: {self.auth.attempts_left}")
        self.attempts.setObjectName("Hint")
        self.attempts.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.attempts)

        hint = QLabel(DEMO_HINT)
        hint.setObjectName("Hint")
        hint.setAlignment(Qt.AlignCenter)
        hint.setWordWrap(True)
        lay.addWidget(hint)

        outer.addWidget(card)

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
        from src.ui.theme import main_qss
        QApplication.instance().setStyleSheet(main_qss())
        self.main_window = MainWindow(user)
        self.main_window.show()
        self.close()


def run():
    init_db()
    app = QApplication(sys.argv)
    app.setStyleSheet(login_qss())
    w = LoginWindow()
    w.show()
    sys.exit(app.exec_())
