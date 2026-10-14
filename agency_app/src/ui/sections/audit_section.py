"""
Раздел «Журнал действий» — доступен только администратору.

Остальные роли свои изменения видят прямо под выбранной записью
в таблицах разделов (блок «История изменений» в CrudSection).
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QLineEdit,
    QHeaderView, QFrame,
)

from src.services.audit_service import visible_rows
from src.services.permissions import can
from src.ui.theme import COLORS, ACTION_LABELS, ROLE_LABELS


ACTION_COLORS = {
    "CREATE": COLORS["success"],
    "UPDATE": COLORS["primary"],
    "DELETE": COLORS["danger"],
    "LOGIN": COLORS["warning"],
}


class AuditSection(QWidget):
    """Полный журнал действий (только admin)."""

    def __init__(self, role="admin", login=""):
        super().__init__()
        self.role = role
        self.login = login
        self._all_rows = []
        self._build_ui()
        if can(self.role, "audit", "view"):
            self.load_data()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        from src.ui.icons import icon as _icon
        head_row = QHBoxLayout()
        head_row.setSpacing(10)
        lbl_icon = QLabel()
        lbl_icon.setPixmap(_icon("shield", color=COLORS["primary"], size=30).pixmap(30, 30))
        head_row.addWidget(lbl_icon)
        ttl_box = QVBoxLayout()
        ttl_box.setSpacing(0)
        title = QLabel("Журнал действий")
        title.setObjectName("PageTitle")
        ttl_box.addWidget(title)
        head_row.addLayout(ttl_box)
        head_row.addStretch()
        root.addLayout(head_row)

        sub = QLabel("Полный журнал виден только администратору. "
                     "Остальные пользователи видят историю изменений прямо под записью в разделе.")
        sub.setObjectName("Subtitle")
        root.addWidget(sub)

        if not can(self.role, "audit", "view"):
            lock = QFrame()
            lock.setObjectName("Card")
            lay = QVBoxLayout(lock)
            lay.setContentsMargins(20, 30, 20, 30)
            lock_row = QHBoxLayout()
            lock_row.addStretch()
            lk_icon = QLabel()
            lk_icon.setPixmap(_icon("lock", color=COLORS["muted"], size=40).pixmap(40, 40))
            lock_row.addWidget(lk_icon)
            lbl = QLabel("Доступ к журналу запрещён")
            lock_row.addWidget(lbl)
            lock_row.addStretch()
            lay.addLayout(lock_row)
            lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['danger']};")
            lay.addWidget(lbl)
            root.addWidget(lock)
            root.addStretch()
            return

        # Панель фильтров
        row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по пользователю, действию или объекту…")
        self.search_input.textChanged.connect(self.apply_filter)
        self.search_input.returnPressed.connect(self.apply_filter)
        row.addWidget(self.search_input, 1)

        btn_refresh = QPushButton("Обновить")
        btn_refresh.setObjectName("Primary")
        btn_refresh.setIcon(_icon("refresh", color=COLORS["on_primary"]))
        btn_refresh.clicked.connect(self.load_data)
        row.addWidget(btn_refresh)
        root.addLayout(row)

        # Таблица журнала
        card = QFrame()
        card.setObjectName("Card")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(8, 8, 8, 8)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Дата и время", "Пользователь", "Роль", "Действие", "Объект", "Подробности"]
        )
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.Stretch)
        hh.setSectionResizeMode(5, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        card_lay.addWidget(self.table)
        root.addWidget(card, 1)

        self.counter = QLabel("")
        self.counter.setObjectName("Subtitle")
        root.addWidget(self.counter)

    # ---------------- Данные ----------------
    def load_data(self):
        self._all_rows = visible_rows(self.role, self.login)
        self.apply_filter()

    def apply_filter(self):
        text = self.search_input.text().strip().lower()
        rows = self._all_rows
        if text:
            rows = [
                r for r in rows
                if text in (r["user_login"] or "").lower()
                or text in ACTION_LABELS.get(r["action"], r["action"] or "").lower()
                or text in (r["entity_type"] or "").lower()
                or text in (r["details"] or "").lower()
            ]
        self._fill(rows)

    def _fill(self, rows):
        self.table.blockSignals(True)
        try:
            self.table.setRowCount(0)
            for r in rows:
                i = self.table.rowCount()
                self.table.insertRow(i)
                values = [
                    str(r.get("created_at") or ""),
                    r.get("user_login") or "",
                    ROLE_LABELS.get(r.get("user_role"), r.get("user_role") or ""),
                    ACTION_LABELS.get(r.get("action"), r.get("action") or ""),
                    f"{(r.get('entity_type') or '')}" + (f" №{r['entity_id']}" if r.get("entity_id") is not None else ""),
                    r.get("details") or "",
                ]
                for j, v in enumerate(values):
                    item = QTableWidgetItem(v)
                    if j == 3:  # раскраска действия
                        color = ACTION_COLORS.get(r.get("action"), COLORS["text"])
                        item.setForeground(QBrush(QColor(color)))
                        f = QFont(); f.setBold(True)
                        item.setFont(f)
                    self.table.setItem(i, j, item)
        finally:
            self.table.blockSignals(False)
        self.counter.setText(f"Записей: {len(rows)}")
