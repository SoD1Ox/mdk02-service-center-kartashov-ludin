from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QFormLayout, QMessageBox, QHeaderView,
)
from src.db.repositories import candidate_repo
from src.services.permissions import can


class CandidatesSection(QWidget):
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

        layout.addWidget(QLabel("Соискатели"))

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск:"))
        self.search_input = QLineEdit()
        search_layout.addWidget(self.search_input)
        b = QPushButton("Найти"); b.clicked.connect(self.search); search_layout.addWidget(b)
        b = QPushButton("Сбросить"); b.clicked.connect(self.load_data); search_layout.addWidget(b)
        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["id", "ФИО", "Телефон", "Email"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.on_row_selected)
        layout.addWidget(self.table)

        form = QFormLayout()
        self.input_name = QLineEdit()
        self.input_phone = QLineEdit()
        self.input_email = QLineEdit()
        form.addRow("ФИО:", self.input_name)
        form.addRow("Телефон:", self.input_phone)
        form.addRow("Email:", self.input_email)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        if can(self.role, "candidates", "add"):
            b = QPushButton("Добавить"); b.clicked.connect(self.add_record); btn_layout.addWidget(b)
        if can(self.role, "candidates", "edit"):
            b = QPushButton("Изменить"); b.clicked.connect(self.update_record); btn_layout.addWidget(b)
        if can(self.role, "candidates", "delete"):
            b = QPushButton("Удалить"); b.clicked.connect(self.delete_record); btn_layout.addWidget(b)
        b = QPushButton("Очистить форму"); b.clicked.connect(self.clear_form); btn_layout.addWidget(b)
        layout.addLayout(btn_layout)

        if not can(self.role, "candidates", "edit"):
            self.input_name.setReadOnly(True)
            self.input_phone.setReadOnly(True)
            self.input_email.setReadOnly(True)

        self.setLayout(layout)

    def load_data(self):
        self._fill_table(candidate_repo.get_all())

    def search(self):
        text = self.search_input.text().strip().lower()
        rows = [
            r for r in candidate_repo.get_all()
            if text in (r["full_name"] or "").lower()
            or text in (r["email"] or "").lower()
        ] if text else candidate_repo.get_all()
        self._fill_table(rows)

    def _fill_table(self, rows):
        self.table.blockSignals(True)
        try:
            self.table.setRowCount(0)
            for r in rows:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(r["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(r["full_name"] or ""))
                self.table.setItem(row, 2, QTableWidgetItem(r["phone"] or ""))
                self.table.setItem(row, 3, QTableWidgetItem(r["email"] or ""))
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
        self.current_id = int(id_item.text())
        self.input_name.setText(self.table.item(row, 1).text() if self.table.item(row, 1) else "")
        self.input_phone.setText(self.table.item(row, 2).text() if self.table.item(row, 2) else "")
        self.input_email.setText(self.table.item(row, 3).text() if self.table.item(row, 3) else "")

    def add_record(self):
        if not can(self.role, "candidates", "add"):
            QMessageBox.warning(self, "Доступ запрещён", "Нет прав"); return
        try:
            candidate_repo.create(
                name,
                self.input_phone.text().strip(),
                self.input_email.text().strip(),
                user_login=self.login,
                user_role=self.role,
            )
            self.load_data(); self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def update_record(self):
        if not can(self.role, "candidates", "edit"):
            QMessageBox.warning(self, "Доступ запрещён", "Нет прав"); return
        if self.current_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите строку"); return
        try:
            candidate_repo.update(
                self.current_id,
                self.input_name.text().strip(),
                self.input_phone.text().strip(),
                self.input_email.text().strip(),
                user_login=self.login,
                user_role=self.role,
            )
            self.load_data(); self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def delete_record(self):
        if not can(self.role, "candidates", "delete"):
            QMessageBox.warning(self, "Доступ запрещён", "Нет прав"); return
        if self.current_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите строку"); return
        if QMessageBox.question(self, "Подтверждение", "Удалить запись?") != QMessageBox.Yes:
            return
        self.table.blockSignals(True)
        try:
            candidate_repo.delete(
                self.current_id,
                user_login=self.login,
                user_role=self.role,
            )
        finally:
            self.table.blockSignals(False)

    def clear_form(self):
        self.current_id = None
        self.input_name.clear()
        self.input_phone.clear()
        self.input_email.clear()
        self.table.blockSignals(True)
        try:
            self.table.clearSelection()
        finally:
            self.table.blockSignals(False)