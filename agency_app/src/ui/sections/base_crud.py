"""
Базовый класс CRUD-раздела.

Инкапсулирует типовой набор: заголовок, поиск, таблица, форма,
кнопки «Добавить / Изменить / Удалить / Очистить». Права берутся
из services/permissions по роли пользователя.

Наследнику достаточно описать:
    section_key  — ключ раздела в PERMISSIONS;
    columns      — заголовки столбцов таблицы;
    fields       — список (имя_поля, метка) для формы;
    fetch()      — загрузка строк (list[dict]);
    to_row()     — dict -> список ячеек таблицы;
    do_create/do_update/do_delete — вызовы репозитория.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QLineEdit,
    QMessageBox, QHeaderView, QFrame,
)

from src.services.permissions import can


class CrudSection(QWidget):
    section_key = ""            # ключ в PERMISSIONS ("candidates", ...)
    title = "Раздел"
    subtitle = ""
    columns = []                # заголовки столбцов
    fields = []                 # [(атрибут модели, метка), ...]
    searchable = True           # показывать ли строку поиска
    readonly_message = "Просмотр: изменений нет в ваших правах"

    def __init__(self, role="manager", login="", parent=None):
        super().__init__(parent)
        self.role = role
        self.login = login
        self.current_id = None
        self._inputs = {}
        self._build_ui()
        self.load_data()

    # ---------------- Права ----------------
    def perm(self, action):
        return can(self.role, self.section_key, action)

    # ---------------- Построение интерфейса ----------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        # Заголовок страницы
        lbl_title = QLabel(self.title)
        lbl_title.setObjectName("PageTitle")
        root.addWidget(lbl_title)
        if self.subtitle:
            lbl_sub = QLabel(self.subtitle)
            lbl_sub.setObjectName("Subtitle")
            root.addWidget(lbl_sub)

        # Поиск
        if self.searchable:
            row = QHBoxLayout()
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Поиск по таблице…")
            self.search_input.returnPressed.connect(self.search)
            row.addWidget(self.search_input, 1)

            btn_find = QPushButton("Найти")
            btn_find.setObjectName("Primary")
            btn_find.clicked.connect(self.search)
            row.addWidget(btn_find)

            btn_reset = QPushButton("Сбросить")
            btn_reset.clicked.connect(self.load_data)
            row.addWidget(btn_reset)
            root.addLayout(row)

        # Таблица
        card = QFrame()
        card.setObjectName("Card")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(8, 8, 8, 8)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.itemSelectionChanged.connect(self.on_row_selected)
        card_lay.addWidget(self.table)
        root.addWidget(card, 1)

        # Форма
        form_card = QFrame()
        form_card.setObjectName("Card")
        form_lay = QVBoxLayout(form_card)
        form_lay.setContentsMargins(14, 10, 14, 12)

        lbl_form = QLabel("Карточка записи")
        lbl_form.setObjectName("GroupBox")
        form_lay.addWidget(lbl_form)

        grid = QHBoxLayout()
        for name, label in self.fields:
            col = QVBoxLayout()
            col.addWidget(QLabel(label))
            inp = QLineEdit()
            self._inputs[name] = inp
            col.addWidget(inp)
            grid.addLayout(col)
        form_lay.addLayout(grid)
        root.addWidget(form_card)

        # Кнопки
        btns = QHBoxLayout()
        self.btn_add = QPushButton("＋ Добавить")
        self.btn_add.setObjectName("Primary")
        self.btn_add.clicked.connect(self.add_record)

        self.btn_edit = QPushButton("✎ Изменить")
        self.btn_edit.clicked.connect(self.update_record)

        self.btn_del = QPushButton("✕ Удалить")
        self.btn_del.setObjectName("Danger")
        self.btn_del.clicked.connect(self.delete_record)

        self.btn_clear = QPushButton("Очистить форму")
        self.btn_clear.clicked.connect(self.clear_form)

        for b, p in [(self.btn_add, "add"), (self.btn_edit, "edit"),
                     (self.btn_del, "delete")]:
            if self.perm(p):
                btns.addWidget(b)
            else:
                b.setEnabled(False)
                b.setToolTip(f"Нет права «{p}» для роли «{self.role}»")
        btns.addWidget(self.btn_clear)
        btns.addStretch()
        root.addLayout(btns)

        if not any([self.perm("add"), self.perm("edit"), self.perm("delete")]):
            note = QLabel(self.readonly_message)
            note.setObjectName("Subtitle")
            root.addWidget(note)

    # ---------------- Данные ----------------
    def value(self, name):
        """Значение поля формы по имени."""
        return self._inputs[name].text().strip()

    def set_values(self, mapping):
        for k, v in mapping.items():
            if k in self._inputs:
                self._inputs[k].setText("" if v is None else str(v))

    def fetch(self):
        """Возвращает list[dict] — переопределить у наследника."""
        return []

    def to_row(self, record):
        """dict -> список ячеек таблицы (по числу columns)."""
        raise NotImplementedError

    def search(self):
        text = self.search_input.text().strip().lower()
        rows = self.fetch()
        if text:
            rows = [r for r in rows
                    if any(text in str(v).lower() for v in r.values())]
        self._fill(rows)

    def load_data(self):
        self._fill(self.fetch())

    def _fill(self, rows):
        self.table.blockSignals(True)
        try:
            self.table.setRowCount(0)
            for r in rows:
                i = self.table.rowCount()
                self.table.insertRow(i)
                for j, cell in enumerate(self.to_row(r)):
                    item = QTableWidgetItem(str(cell if cell is not None else ""))
                    self.table.setItem(i, j, item)
        finally:
            self.table.blockSignals(False)

    def on_row_selected(self):
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            return
        self.fill_form_from_row(sel[0].row())

    def fill_form_from_row(self, row):
        """Заполнить форму из выбранной строки; id -> self.current_id."""
        first = self.table.item(row, 0)
        if first is not None and first.text().isdigit():
            self.current_id = int(first.text())

    # ---------------- CRUD ----------------
    def add_record(self):
        if not self.perm("add"):
            QMessageBox.warning(self, "Доступ запрещён", "Нет прав на добавление")
            return
        try:
            self.do_create()
            self.load_data()
            self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def update_record(self):
        if not self.perm("edit"):
            QMessageBox.warning(self, "Доступ запрещён", "Нет прав на изменение")
            return
        if self.current_id is None:
            QMessageBox.warning(self, "Выбор не сделан", "Сначала выберите строку в таблице")
            return
        try:
            self.do_update()
            self.load_data()
            self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def delete_record(self):
        if not self.perm("delete"):
            QMessageBox.warning(self, "Доступ запрещён", "Нет прав на удаление")
            return
        if self.current_id is None:
            QMessageBox.warning(self, "Выбор не сделан", "Сначала выберите строку в таблице")
            return
        if QMessageBox.question(self, "Подтверждение",
                                "Удалить выбранную запись?") != QMessageBox.Yes:
            return
        try:
            self.do_delete()
            self.load_data()
            self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def do_create(self):
        raise NotImplementedError

    def do_update(self):
        raise NotImplementedError

    def do_delete(self):
        raise NotImplementedError

    def clear_form(self):
        self.current_id = None
        for inp in self._inputs.values():
            inp.clear()
        self.table.blockSignals(True)
        try:
            self.table.clearSelection()
        finally:
            self.table.blockSignals(False)
