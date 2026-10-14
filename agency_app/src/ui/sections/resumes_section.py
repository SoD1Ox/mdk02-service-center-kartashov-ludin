from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QFormLayout, QMessageBox, QHeaderView,
)
from src.db.repositories import resume_repo
from src.services.permissions import can


class ResumesSection(QWidget):
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

        layout.addWidget(QLabel("Резюме"))

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск:"))
        self.search_input = QLineEdit()
        search_layout.addWidget(self.search_input)
        b = QPushButton("Найти"); b.clicked.connect(self.search); search_layout.addWidget(b)
        b = QPushButton("Сбросить"); b.clicked.connect(self.load_data); search_layout.addWidget(b)
        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["id", "Соискатель", "Должность", "Опыт", "Образование"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.on_row_selected)
        layout.addWidget(self.table)

        form = QFormLayout()
        self.input_candidate = QLineEdit()
        self.input_title = QLineEdit()
        self.input_experience = QLineEdit()
        self.input_education = QLineEdit()
        form.addRow("ID соискателя:", self.input_candidate)
        form.addRow("Должность:", self.input_title)
        form.addRow("Опыт:", self.input_experience)
        form.addRow("Образование:", self.input_education)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        if can(self.role, "resumes", "add"):
            b = QPushButton("Добавить"); b.clicked.connect(self.add_record); btn_layout.addWidget(b)
        if can(self.role, "resumes", "edit"):
            b = QPushButton("Изменить"); b.clicked.connect(self.update_record); btn_layout.addWidget(b)
        if can(self.role, "resumes", "delete"):
            b = QPushButton("Удалить"); b.clicked.connect(self.delete_record); btn_layout.addWidget(b)
        b = QPushButton("Очистить форму"); b.clicked.connect(self.clear_form); btn_layout.addWidget(b)
        layout.addLayout(btn_layout)

        if not can(self.role, "resumes", "edit"):
            for w in [self.input_candidate, self.input_title,
                      self.input_experience, self.input_education]:
                w.setReadOnly(True)

        self.setLayout(layout)

    def load_data(self):
        self._fill_table(resume_repo.get_all())

    def search(self):
        text = self.search_input.text().strip().lower()
        rows = [
            r for r in resume_repo.get_all()
            if text in (r["title"] or "").lower()
            or text in (r["candidate_name"] or "").lower()
        ] if text else resume_repo.get_all()
        self._fill_table(rows)

    def _fill_table(self, rows):
        self.table.blockSignals(True)
        try:
            self.table.setRowCount(0)
            for r in rows:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(r["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(r["candidate_name"] or ""))
                self.table.setItem(row, 2, QTableWidgetItem(r["title"] or ""))
                self.table.setItem(row, 3, QTableWidgetItem(str(r["experience"])))
                self.table.setItem(row, 4, QTableWidgetItem(r["education"] or ""))
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
        for r in resume_repo.get_all():
            if r["id"] == rid:
                self.current_id = rid
                self.input_candidate.setText(str(r["candidate_id"]))
                self.input_title.setText(r["title"] or "")
                self.input_experience.setText(str(r["experience"]))
                self.input_education.setText(r["education"] or "")
                break

    def add_record(self):
        if not can(self.role, "resumes", "add"):
            QMessageBox.warning(self, "Доступ запрещён", "Нет прав"); return
        try:
            resume_repo.create(
                int(self.input_candidate.text().strip()),
                self.input_title.text().strip(),
                int(self.input_experience.text().strip() or 0),
                self.input_education.text().strip(),
            )
            self.load_data(); self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def update_record(self):
        if not can(self.role, "resumes", "edit"):
            QMessageBox.warning(self, "Доступ запрещён", "Нет прав"); return
        if self.current_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите строку"); return
        try:
            resume_repo.update(
                self.current_id,
                int(self.input_candidate.text().strip()),
                self.input_title.text().strip(),
                int(self.input_experience.text().strip() or 0),
                self.input_education.text().strip(),
            )
            self.load_data(); self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def delete_record(self):
        if not can(self.role, "resumes", "delete"):
            QMessageBox.warning(self, "Доступ запрещён", "Нет прав"); return
        if self.current_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите строку"); return
        if QMessageBox.question(self, "Подтверждение", "Удалить запись?") != QMessageBox.Yes:
            return
        self.table.blockSignals(True)
        try:
            resume_repo.delete(self.current_id)
            self.current_id = None
            self.load_data(); self.clear_form()
        finally:
            self.table.blockSignals(False)

    def clear_form(self):
        self.current_id = None
        self.input_candidate.clear()
        self.input_title.clear()
        self.input_experience.clear()
        self.input_education.clear()
        self.table.blockSignals(True)
        try:
            self.table.clearSelection()
        finally:
            self.table.blockSignals(False)