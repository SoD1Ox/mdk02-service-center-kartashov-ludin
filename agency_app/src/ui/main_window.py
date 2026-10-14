from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QLabel,
    QPushButton,
)
from PyQt5.QtCore import Qt, QTimer

from src.ui.sections.candidates_section import CandidatesSection
from src.ui.sections.resumes_section import ResumesSection
from src.ui.sections.skills_section import SkillsSection
from src.ui.sections.employers_section import EmployersSection
from src.ui.sections.vacancies_section import VacanciesSection
from src.ui.sections.responses_section import ResponsesSection
from src.ui.sections.deals_section import DealsSection
from src.ui.sections.reports_section import ReportsSection
from src.ui.sections.analytics_section import AnalyticsSection
from src.ui.sections.audit_section import AuditSection


ROLE_SECTIONS = {
    "admin": [
        "Соискатели", "Резюме", "Навыки", "Работодатели",
        "Вакансии", "Отклики", "Сделки", "Журнал",
    ],
    "manager": [
        "Соискатели", "Резюме", "Навыки", "Работодатели",
        "Вакансии", "Отклики", "Сделки", "Журнал",
    ],
    "director": [
        "Отчёты", "Аналитика", "Сделки", "Журнал",
    ],
    "employer": [
        "Мои вакансии", "Отклики", "Журнал",
    ],
    "candidate": [
        "Моё резюме", "Вакансии", "Мои отклики", "Журнал",
    ],
}


SECTION_CLASSES = {
    "Соискатели": CandidatesSection,
    "Резюме": ResumesSection,
    "Навыки": SkillsSection,
    "Работодатели": EmployersSection,
    "Вакансии": VacanciesSection,
    "Отклики": ResponsesSection,
    "Сделки": DealsSection,
    "Отчёты": ReportsSection,
    "Аналитика": AnalyticsSection,
    "Журнал": AuditSection,                  # ← новый раздел
    "Мои вакансии": VacanciesSection,
    "Моё резюме": ResumesSection,
    "Мои отклики": ResponsesSection,
}


class MainWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.role = user.get("role", "candidate")
        self.current_section = None

        self.setWindowTitle(f"ИС «Кадровое агентство» — {user['login']} ({self.role})")
        self.resize(1000, 600)

        root = QHBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        menu_layout = QVBoxLayout()
        menu_layout.setContentsMargins(10, 10, 10, 10)

        user_label = QLabel(f"{user['login']}\n({self.role})")
        user_label.setStyleSheet("font-weight: bold; padding: 5px;")
        menu_layout.addWidget(user_label)

        menu_layout.addWidget(QLabel("Разделы:"))

        self.menu = QListWidget()
        self.sections = ROLE_SECTIONS.get(self.role, ["Вакансии"])
        self.menu.addItems(self.sections)
        self.menu.setFixedWidth(200)
        self.menu.currentRowChanged.connect(self.on_menu_changed)
        menu_layout.addWidget(self.menu)

        btn_logout = QPushButton("Выйти")
        btn_logout.clicked.connect(self.logout)
        menu_layout.addWidget(btn_logout)

        root.addLayout(menu_layout)

        self.container = QVBoxLayout()
        self.container.setContentsMargins(0, 0, 0, 0)
        root.addLayout(self.container)

        self.setLayout(root)

        if self.sections:
            QTimer.singleShot(0, lambda: self.open_section(self.sections[0]))

    def open_section(self, name):
        if self.current_section is not None:
            self.container.removeWidget(self.current_section)
            self.current_section.deleteLater()
            self.current_section = None

        cls = SECTION_CLASSES.get(name)
        if cls is None:
            w = QWidget()
            lay = QVBoxLayout()
            lbl = QLabel(f"Раздел «{name}» — в разработке")
            lbl.setAlignment(Qt.AlignCenter)
            lay.addWidget(lbl)
            w.setLayout(lay)
            self.current_section = w
        else:
            try:
                self.current_section = cls(role=self.role, login=self.user["login"])
            except Exception as e:
                print(f"[Ошибка раздела {name}]:", e)
                w = QWidget()
                lay = QVBoxLayout()
                lbl = QLabel(f"Ошибка раздела «{name}»: {e}")
                lbl.setAlignment(Qt.AlignCenter)
                lay.addWidget(lbl)
                w.setLayout(lay)
                self.current_section = w

        self.container.addWidget(self.current_section)

    def on_menu_changed(self, index):
        if index < 0:
            return
        name = self.sections[index]
        self.open_section(name)

    def logout(self):
        from src.ui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()