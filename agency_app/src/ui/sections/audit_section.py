from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QLineEdit,
)
from src.services.audit_service import get_all, get_for_roles, get_for_user


class AuditSection(QWidget):
    """Журнал действий пользователей (аудит)."""

    def __init__(self, role="admin", login=""):
        super().__init__()
        self.role = role
        self.login = login
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(QLabel(f"Журнал действий — {self.role}"))

        # Поиск
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск:"))
        self.search_input = QLineEdit()
        search_layout.addWidget(self.search_input)
        b = QPushButton("Найти"); b.clicked.connect(self.search); search_layout.addWidget(b)
        b = QPushButton("Обновить"); b.clicked.connect(self.load_data); search_layout.addWidget(b)
        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["id", "Пользователь", "Роль", "Действие", "Объект", "ID объекта", "Дата"]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def _fetch_data(self):
        """Что показывать в зависимости от роли."""
        if self.role == "admin":
            return get_all()
        if self.role == "manager":
            # менеджер видит действия директора и менеджеров
            return get_for_roles(["director", "manager"])
        # director / employer / candidate — только свои
        return get_for_user(self.login)

    def load_data(self):
        rows = self._fetch_data()
        self._fill(rows)

    def search(self):
        text = self.search_input.text().strip().lower()
        rows = self._fetch_data()
        if text:
            rows = [
                r for r in rows
                if text in (r["user_login"] or "").lower()
                or text in (r["action"] or "").lower()
                or text in (r["entity_type"] or "").lower()
            ]
        self._fill(rows)

    def _fill(self, rows):
        self.table.blockSignals(True)
        try:
            self.table.setRowCount(0)
            for r in rows:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(r["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(r["user_login"] or ""))
                self.table.setItem(row, 2, QTableWidgetItem(r["user_role"] or ""))
                self.table.setItem(row, 3, QTableWidgetItem(r["action"] or ""))
                self.table.setItem(row, 4, QTableWidgetItem(r["entity_type"] or ""))
                self.table.setItem(row, 5, QTableWidgetItem(str(r["entity_id"] or "")))
                self.table.setItem(row, 6, QTableWidgetItem(str(r["created_at"] or "")))
        finally:
            self.table.blockSignals(False)