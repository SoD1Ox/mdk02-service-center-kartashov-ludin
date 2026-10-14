from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton,
)
from src.db.connection import get_connection, DB_PATH


class ReportsSection(QWidget):
    """Раздел «Отчёты» — сводка по системе."""

    def __init__(self, role="director", login=""):
        super().__init__()
        self.role = role
        self.login = login
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Отчёты")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Таблица отчёта
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Показатель", "Значение"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        # Кнопка обновления
        btn = QPushButton("Обновить")
        btn.clicked.connect(self.load_data)
        layout.addWidget(btn)

        self.setLayout(layout)

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