from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton,
)
from src.db.connection import get_connection, DB_PATH


class AnalyticsSection(QWidget):
    """Раздел «Аналитика» — статистика по статусам."""

    def __init__(self, role="director", login=""):
        super().__init__()
        self.role = role
        self.login = login
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Аналитика")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Отклики по статусам
        layout.addWidget(QLabel("Отклики по статусам:"))
        self.table_responses = QTableWidget()
        self.table_responses.setColumnCount(2)
        self.table_responses.setHorizontalHeaderLabels(["Статус", "Количество"])
        self.table_responses.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_responses.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table_responses)

        # Вакансии по статусам
        layout.addWidget(QLabel("Вакансии по статусам:"))
        self.table_vacancies = QTableWidget()
        self.table_vacancies.setColumnCount(2)
        self.table_vacancies.setHorizontalHeaderLabels(["Статус", "Количество"])
        self.table_vacancies.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_vacancies.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table_vacancies)

        # Средняя зарплата
        layout.addWidget(QLabel("Средняя зарплата по вакансиям:"))
        self.lbl_salary = QLabel("—")
        layout.addWidget(self.lbl_salary)

        # Средняя комиссия
        layout.addWidget(QLabel("Средняя комиссия по сделкам:"))
        self.lbl_commission = QLabel("—")
        layout.addWidget(self.lbl_commission)

        btn = QPushButton("Обновить")
        btn.clicked.connect(self.load_data)
        layout.addWidget(btn)

        self.setLayout(layout)

    def load_data(self):
        with get_connection(DB_PATH) as conn:
            # Отклики по статусам
            resp = conn.execute("""
                SELECT status, COUNT(*) FROM responses GROUP BY status
            """).fetchall()

            # Вакансии по статусам
            vac = conn.execute("""
                SELECT status, COUNT(*) FROM vacancies GROUP BY status
            """).fetchall()

            # Средняя зарплата
            avg_salary = conn.execute(
                "SELECT COALESCE(AVG(salary), 0) FROM vacancies"
            ).fetchone()[0]

            # Средняя комиссия
            avg_comm = conn.execute(
                "SELECT COALESCE(AVG(commission), 0) FROM deals"
            ).fetchone()[0]

        self._fill(self.table_responses, resp)
        self._fill(self.table_vacancies, vac)
        self.lbl_salary.setText(f"{avg_salary:.0f} ₽")
        self.lbl_commission.setText(f"{avg_comm:.0f} ₽")

    def _fill(self, table, rows):
        table.setRowCount(0)
        for name, count in rows:
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(str(name or "—")))
            table.setItem(row, 1, QTableWidgetItem(str(count)))