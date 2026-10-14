from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QFormLayout, QMessageBox, QHeaderView,
)
from src.db.repositories import deal_repo
from src.services.permissions import can


class DealsSection(QWidget):
    def __init__(self, role="manager", login=""):
        super().__init__()
        self.role = role
        self.login = login
        self.current_id = None
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(QLabel("Сделки"))

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск:"))
        self.search_input = QLineEdit()
        search_layout.addWidget(self.search_input)
        b = QPushButton("Найти"); b.clicked.connect(self.search); search_layout.addWidget(b)
        b = QPushButton("Сбросить"); b.clicked.connect(self.load_data); search_layout.addWidget(b)
        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["id", "ID отклика", "Комиссия", "Налог", "Дата"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.on_row_selected)
        layout.addWidget(self.table)

        form = QFormLayout()
        self.input_response = QLineEdit()
        self.input_commission = QLineEdit()
        self.input_tax = QLineEdit()
        form.addRow("ID отклика:", self.input_response)
        form.addRow("Комиссия:", self.input_commission)
        form.addRow("Налог:", self.input_tax)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        if can(self.role, "deals", "add"):
            b = QPushButton("Добавить"); b.clicked.connect(self.add_record); btn_layout.addWidget(b)
        if can(self.role, "deals", "edit"):
            b = QPushButton("Изменить"); b.clicked.connect(self.update_record); btn_layout.addWidget(b)
        if can(self.role, "deals", "delete"):
            b = QPushButton("Удалить"); b.clicked.connect(self.delete_record); btn_layout.addWidget(b)
        b = QPushButton("Очистить форму"); b.clicked.connect(self.clear_form); btn_layout.addWidget(b)
        layout.addLayout(btn_layout)

        if not can(self.role, "deals", "edit"):
            self.input_response.setReadOnly(True)
            self.input_commission.setReadOnly(True)
            self.input_tax.setReadOnly(True)

        self.setLayout(layout)

    def load_data(self):
        self._fill_table(deal_repo.get_all())

    def search(self):
        text = self.search_input.text().strip().lower()
        rows = [
            r for r in deal_repo.get_all()
            if text in str(r["response_id"]).lower()
            or text in str(r["commission"]).lower()
        ] if text else deal_repo.get_all()
        self._fill_table(rows)

    def _fill_table(self, rows):
        self.table.blockSignals(True)
        try:
            self.table.setRowCount(0)
            for r in rows:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(r["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(str(r["response_id"])))
                self.table.setItem(row, 2, QTableWidgetItem(f"{r['commission']} ₽"))
                self.table.setItem(row, 3, QTableWidgetItem(f"{r['tax']} ₽"))
                self.table.setItem(row, 4, QTableWidgetItem(str(r["closed_at"] or "")))
        finally:
            self.table.blockSignals(False)

    def on_row_selected(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        id_item = self.table.item(row, 0)
        if id_item is None:
            return
        rid = int(id_item.text())
        for r in deal_repo.get_all():
            if r["id"] == rid:
                self.current_id = rid
                self.input_response.setText(str(r["response_id"]))
                self.input_commission.setText(str(r["commission"]))
                self.input_tax.setText(str(r["tax"]))
                break

    def add_record(self):
        if not can(self.role, "deals", "add"):
            QMessageBox.warning(self, "Доступ запрещён", "Нет прав"); return
        try:
            deal_repo.create(
                int(self.input_response.text().strip()),
                int(self.input_commission.text().strip() or 0),
                int(self.input_tax.text().strip() or 0),
            )
            self.load_data(); self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def update_record(self):
        if not can(self.role, "deals", "edit"):
            QMessageBox.warning(self, "Доступ запрещён", "Нет прав"); return
        if self.current_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите строку"); return
        try:
            deal_repo.update(
                self.current_id,
                int(self.input_response.text().strip()),
                int(self.input_commission.text().strip() or 0),
                int(self.input_tax.text().strip() or 0),
            )
            self.load_data(); self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def delete_record(self):
        if not can(self.role, "deals", "delete"):
            QMessageBox.warning(self, "Доступ запрещён", "Нет прав"); return
        if self.current_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите строку"); return
        if QMessageBox.question(self, "Подтверждение", "Удалить запись?") != QMessageBox.Yes:
            return
        self.table.blockSignals(True)
        try:
            deal_repo.delete(self.current_id)
            self.current_id = None
            self.load_data(); self.clear_form()
        finally:
            self.table.blockSignals(False)

    def clear_form(self):
        self.current_id = None
        self.input_response.clear()
        self.input_commission.clear()
        self.input_tax.clear()
        self.table.blockSignals(True)
        try:
            self.table.clearSelection()
        finally:
            self.table.blockSignals(False)