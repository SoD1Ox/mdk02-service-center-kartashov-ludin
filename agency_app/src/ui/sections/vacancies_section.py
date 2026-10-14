from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QFormLayout, QMessageBox,
)
from src.db.repositories import vacancy_repo
from src.services.permissions import can


class VacanciesSection(QWidget):
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

        layout.addWidget(QLabel("Вакансии"))

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["id", "Работодатель", "Должность", "Требования", "Зарплата", "Статус"]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.on_row_selected)
        layout.addWidget(self.table)

        form = QFormLayout()
        self.input_employer = QLineEdit()
        self.input_title = QLineEdit()
        self.input_requirements = QLineEdit()
        self.input_salary = QLineEdit()
        self.input_status = QLineEdit()
        form.addRow("ID работодателя:", self.input_employer)
        form.addRow("Должность:", self.input_title)
        form.addRow("Требования:", self.input_requirements)
        form.addRow("Зарплата:", self.input_salary)
        form.addRow("Статус:", self.input_status)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        if can(self.role, "vacancies", "add"):
            b = QPushButton("Добавить"); b.clicked.connect(self.add_record); btn_layout.addWidget(b)
        if can(self.role, "vacancies", "edit"):
            b = QPushButton("Изменить"); b.clicked.connect(self.update_record); btn_layout.addWidget(b)
        if can(self.role, "vacancies", "delete"):
            b = QPushButton("Удалить"); b.clicked.connect(self.delete_record); btn_layout.addWidget(b)
        b = QPushButton("Очистить"); b.clicked.connect(self.clear_form); btn_layout.addWidget(b)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_data(self):
        self._fill_table(vacancy_repo.get_all())

    def _fill_table(self, rows):
        self.table.blockSignals(True)
        try:
            self.table.setRowCount(0)
            for r in rows:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(r["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(r["employer_name"] or ""))
                self.table.setItem(row, 2, QTableWidgetItem(r["title"] or ""))
                self.table.setItem(row, 3, QTableWidgetItem(r["requirements"] or ""))
                self.table.setItem(row, 4, QTableWidgetItem(str(r["salary"] or 0)))
                self.table.setItem(row, 5, QTableWidgetItem(r["status"] or ""))
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
        for r in vacancy_repo.get_all():
            if r["id"] == rid:
                self.current_id = rid
                self.input_employer.setText(str(r["employer_id"]))
                self.input_title.setText(r["title"] or "")
                self.input_requirements.setText(r["requirements"] or "")
                self.input_salary.setText(str(r["salary"] or 0))
                self.input_status.setText(r["status"] or "")
                break

    def add_record(self):
        try:
            vacancy_repo.create(
                int(self.input_employer.text().strip()),
                self.input_title.text().strip(),
                self.input_requirements.text().strip(),
                int(self.input_salary.text().strip() or 0),
            )
            self.load_data(); self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def update_record(self):
        if self.current_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите строку"); return
        try:
            vacancy_repo.update(
                self.current_id,
                int(self.input_employer.text().strip()),
                self.input_title.text().strip(),
                self.input_requirements.text().strip(),
                int(self.input_salary.text().strip() or 0),
                self.input_status.text().strip() or "Открыта",
            )
            self.load_data(); self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def delete_record(self):
        if self.current_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите строку"); return
        if QMessageBox.question(self, "Подтверждение", "Удалить запись?") != QMessageBox.Yes:
            return
        self.table.blockSignals(True)
        try:
            vacancy_repo.delete(self.current_id)
            self.current_id = None
            self.load_data(); self.clear_form()
        finally:
            self.table.blockSignals(False)

    def clear_form(self):
        self.current_id = None
        self.input_employer.clear()
        self.input_title.clear()
        self.input_requirements.clear()
        self.input_salary.clear()
        self.input_status.clear()
        self.table.blockSignals(True)
        try:
            self.table.clearSelection()
        finally:
            self.table.blockSignals(False)