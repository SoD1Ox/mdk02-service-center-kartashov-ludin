from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton,
)
from src.db.connection import get_connection, DB_PATH
from src.ui.theme import COLORS
from src.ui.widgets import StatCard


class AnalyticsSection(QWidget):
    """Раздел «Аналитика» — статистика по статусам."""

    def __init__(self, role="director", login=""):
        super().__init__()
        self.role = role
        self.login = login
        self._build_ui()
        self.load_data()

    def _table(self, headers):
        card = QFrame()
        card.setObjectName("Card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(8, 8, 8, 8)
        t = QTableWidget()
        t.setColumnCount(len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        t.setEditTriggers(QTableWidget.NoEditTriggers)
        t.verticalHeader().setVisible(False)
        t.setAlternatingRowColors(True)
        lay.addWidget(t)
        return card, t

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("Аналитика")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        sub = QLabel("Статистика по статусам и средние показатели")
        sub.setObjectName("Subtitle")
        layout.addWidget(sub)

        # Карточки средних значений
        row1 = QHBoxLayout()
        self.card_salary = StatCard("Средняя зарплата", "—", accent=COLORS["primary"])
        self.card_commission = StatCard("Средняя комиссия", "—", accent=COLORS["success"])
        row1.addWidget(self.card_salary)
        row1.addWidget(self.card_commission)
        layout.addLayout(row1)

        # Два таблицы рядом
        tables_row = QHBoxLayout()

        col_resp = QVBoxLayout()
        lbl_resp = QLabel("Отклики по статусам")
        lbl_resp.setObjectName("GroupBox")
        col_resp.addWidget(lbl_resp)
        card_resp, self.table_responses = self._table(["Статус", "Количество"])
        col_resp.addWidget(card_resp)
        tables_row.addLayout(col_resp)

        col_vac = QVBoxLayout()
        lbl_vac = QLabel("Вакансии по статусам")
        lbl_vac.setObjectName("GroupBox")
        col_vac.addWidget(lbl_vac)
        card_vac, self.table_vacancies = self._table(["Статус", "Количество"])
        col_vac.addWidget(card_vac)
        tables_row.addLayout(col_vac)

        layout.addLayout(tables_row, 1)

        btn_row = QHBoxLayout()
        btn = QPushButton("⟳  Обновить")
        btn.setObjectName("Primary")
        btn.clicked.connect(self.load_data)
        btn_row.addWidget(btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

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
        self.card_salary.set_value(f"{avg_salary:.0f} ₽")
        self.card_commission.set_value(f"{avg_comm:.0f} ₽")

    def _fill(self, table, rows):
        table.setRowCount(0)
        for name, count in rows:
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(str(name or "—")))
            table.setItem(row, 1, QTableWidgetItem(str(count)))