"""Главное окно: тёмный сайдбар с навигацией + контейнер разделов."""
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QLabel,
    QPushButton, QFrame,
)

from src.services.permissions import can
from src.ui.theme import COLORS, ROLE_COLORS, ROLE_LABELS
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


SECTION_CLASSES = {
    "Соискатели":   CandidatesSection,
    "Резюме":       ResumesSection,
    "Навыки":       SkillsSection,
    "Работодатели": EmployersSection,
    "Вакансии":     VacanciesSection,
    "Мои вакансии": VacanciesSection,
    "Моё резюме":   ResumesSection,
    "Отклики":      ResponsesSection,
    "Мои отклики":  ResponsesSection,
    "Сделки":       DealsSection,
    "Отчёты":       ReportsSection,
    "Аналитика":    AnalyticsSection,
    "Журнал":       AuditSection,   # только для admin
}

# Разделы по ролям; «Журнал» есть только у администратора
ROLE_SECTIONS = {
    "admin": [
        "Соискатели", "Резюме", "Навыки", "Работодатели",
        "Вакансии", "Отклики", "Сделки", "Журнал",
    ],
    "manager": [
        "Соискатели", "Резюме", "Навыки", "Работодатели",
        "Вакансии", "Отклики", "Сделки",
    ],
    "director": [
        "Отчёты", "Аналитика", "Сделки", "Соискатели", "Вакансии",
    ],
    "employer": [
        "Мои вакансии", "Отклики",
    ],
    "candidate": [
        "Моё резюме", "Вакансии", "Мои отклики",
    ],
}

SECTION_ICONS = {
    "Соискатели": "👤", "Моё резюме": "📄", "Резюме": "📄",
    "Навыки": "🧩", "Работодатели": "🏢", "Вакансии": "💼",
    "Мои вакансии": "💼", "Отклики": "✉️", "Мои отклики": "✉️",
    "Сделки": "🤝", "Отчёты": "📊", "Аналитика": "📈", "Журнал": "🛡️",
}


class MainWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.role = user.get("role", "candidate")
        self.current_section = None

        self.setWindowTitle(f"ИС «Кадровое агентство» — {user['login']}")
        self.resize(1100, 680)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---------------- Сайдбар ----------------
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        side_lay = QVBoxLayout(sidebar)
        side_lay.setContentsMargins(14, 18, 14, 14)
        side_lay.setSpacing(4)

        logo = QLabel("◆ Кадровое агентство")
        logo.setObjectName("SidebarTitle")
        side_lay.addWidget(logo)

        name = QLabel(user["login"])
        name.setObjectName("SidebarUser")
        side_lay.addWidget(name)

        role_lbl = QLabel(ROLE_LABELS.get(self.role, self.role))
        role_lbl.setObjectName("SidebarRole")
        _rc = ROLE_COLORS.get(self.role, COLORS["primary"])
        role_lbl.setStyleSheet(
            "color: " + COLORS["sidebar_text"] + "; font-weight: bold;"
            " border-left: 3px solid " + _rc + ";"
            " padding-left: 6px;"
        )
        side_lay.addWidget(role_lbl)

        sec_lbl = QLabel("РАЗДЕЛЫ")
        sec_lbl.setObjectName("Section")
        side_lay.addWidget(sec_lbl)

        self.sections = list(ROLE_SECTIONS.get(self.role, ["Вакансии"]))
        self.menu = QListWidget()
        self.menu.setObjectName("Nav")
        for s in self.sections:
            self.menu.addItem(f"{SECTION_ICONS.get(s, '•')}  {s}")
        self.menu.setFixedWidth(220)
        self.menu.currentRowChanged.connect(self.on_menu_changed)
        side_lay.addWidget(self.menu, 1)

        btn_logout = QPushButton("⎋  Выйти")
        btn_logout.setObjectName("Logout")
        btn_logout.clicked.connect(self.logout)
        side_lay.addWidget(btn_logout)

        root.addWidget(sidebar)

        # ---------------- Контент ----------------
        self.container = QVBoxLayout()
        self.container.setContentsMargins(0, 0, 0, 0)
        root.addLayout(self.container, 1)

        if self.sections:
            QTimer.singleShot(0, lambda: (self.menu.setCurrentRow(0),
                                          self.open_section(self.sections[0])))

    # ---------------- Разделы ----------------
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
        self.open_section(self.sections[index])

    def logout(self):
        from src.ui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
