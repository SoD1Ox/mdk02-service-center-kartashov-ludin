from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton,
)
from src.db.connection import get_connection, DB_PATH
from src.ui.theme import COLORS
from src.ui.widgets import StatCard


class ReportsSection(QWidget):
    """Раздел «Отчёты» — сводка по системе."""

    def __init__(self, role="director", login=""):
        super().__init__()
        self.role = role
        self.login = login
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("Отчёты")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        sub = QLabel("Сводные показатели работы кадрового агентства")
        sub.setObjectName("Subtitle")
        layout.addWidget(sub)

        # Карточки ключевых показателей
        row1 = QHBoxLayout()
        self.card_deals = StatCard("Сделок", "—", accent=COLORS["primary"])
        self.card_commission = StatCard("Комиссии", "—", accent=COLORS["success"])
        self.card_tax = StatCard("Налоги", "—", accent=COLORS["warning"])
        self.card_vacancies = StatCard("Вакансий", "—", accent=COLORS["info"])
        for w in (self.card_deals, self.card_commission, self.card_tax, self.card_vacancies):
            row1.addWidget(w)
        layout.addLayout(row1)

        # Таблица отчёта
        card = QFrame()
        card.setObjectName("Card")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(8, 8, 8, 8)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Показатель", "Значение"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        card_lay.addWidget(self.table)
        layout.addWidget(card, 1)

        # Кнопка обновления
        btn_row = QHBoxLayout()
        btn = QPushButton("⟳  Обновить")
        btn.setObjectName("Primary")
        btn.clicked.connect(self.load_data)
        btn_row.addWidget(btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def load_data(self):
        with get_connection(DB_PATH) as conn:
            users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            candidates = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
            resumes = conn.execute("SELECT COUNT(*) FROM resumes").fetchone()[0]
            employers = conn.execute("SELECT COUNT(*) FROM employers").fetchone()[0]
            vacancies = conn.execute("SELECT COUNT(*) FROM vacancies").fetchone()[0]
            responses = conn.execute("SELECT COUNT(*) FROM responses").fetchone()[0]
            deals = conn.execute("SELECT COUNT(*) FROM deals").fetchone()[0]

            total_commission = conn.execute(
                "SELECT COALESCE(SUM(commission), 0) FROM deals"
            ).fetchone()[0]
            total_tax = conn.execute(
                "SELECT COALESCE(SUM(tax), 0) FROM deals"
            ).fetchone()[0]

        rows = [
            ("Пользователей", users),
            ("Соискателей", candidates),
            ("Резюме", resumes),
            ("Работодателей", employers),
            ("Вакансий", vacancies),
            ("Откликов", responses),
            ("Сделок", deals),
            ("Сумма комиссий", f"{total_commission} ₽"),
            ("Сумма налогов", f"{total_tax} ₽"),
        ]

        self.table.setRowCount(0)
        for name, value in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(name)))
            self.table.setItem(row, 1, QTableWidgetItem(str(value)))

        self.card_deals.set_value(deals)
        self.card_commission.set_value(f"{total_commission} ₽")
        self.card_tax.set_value(f"{total_tax} ₽")
        self.card_vacancies.set_value(vacancies)