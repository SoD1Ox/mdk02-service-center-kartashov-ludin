"""
Базовый класс CRUD-раздела.

Инкапсулирует типовой набор: заголовок, поиск, таблица, форма,
кнопки «Добавить / Изменить / Удалить / Очистить». Права берутся
из services/permissions по роли пользователя.

Дополнительно: под таблицей показывается блок «История изменений»
выбранной записи — чтобы пользователю не открывать общий журнал
(он виден только администратору).

Наследнику достаточно описать:
    section_key  — ключ раздела в PERMISSIONS;
    entity_type  — тип объекта в audit_log ('candidate', 'vacancy', ...);
    columns      — заголовки столбцов таблицы;
    fields       — список (имя_поля, метка) для формы;
    fetch()      — загрузка строк (list[dict]);
    to_row()     — dict -> список ячеек таблицы;
    do_create/do_update/do_delete — вызовы репозитория.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QLineEdit,
    QMessageBox, QHeaderView, QFrame, QComboBox,
)

from src.services.permissions import can
from src.ui.theme import COLORS
from src.ui.widgets import history_card, EmptyHint


def _make_field(kind, options=None):
    """Создать виджет поля формы: комбобокс со списком вариантов или строку ввода."""
    if kind == "combo":
        cb = QComboBox()
        cb.setEditable(True)  # можно и выбрать из списка, и ввести своё
        if options:
            cb.addItems([str(o) for o in options])
        return cb
    return QLineEdit()


class CrudSection(QWidget):
    section_key = ""            # ключ в PERMISSIONS ("candidates", ...)
    entity_type = ""            # тип объекта в audit_log ("candidate", ...)
    icon_name = "doc"           # кастомный значок раздела (см. ui/icons.py)
    title = "Раздел"
    subtitle = ""
    columns = []                # заголовки столбцов
    fields = []                 # [(атрибут модели, метка, "text"|"combo"), ...]
    searchable = True           # показывать ли строку поиска
    readonly_message = "Просмотр: изменений нет в ваших правах"
    action_button_text = None   # доп. кнопка раздела (например «Откликнуться»)
    action_button_icon = "send"

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

    # ---------------- Точки расширения ----------------
    def field_options(self, name):
        """Список вариантов для combo-поля (по умолчанию пусто)."""
        return []

    def on_action_button(self):
        """Обработка доп. кнопки раздела (переопределить у наследника)."""
        pass

    # ---------------- Построение интерфейса ----------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        # Заголовок страницы с кастомным значком раздела
        head_row = QHBoxLayout()
        head_row.setSpacing(10)
        from src.ui.icons import icon as _icon
        lbl_icon = QLabel()
        lbl_icon.setPixmap(_icon(self.icon_name, color=COLORS["primary"], size=30).pixmap(30, 30))
        head_row.addWidget(lbl_icon)
        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        lbl_title = QLabel(self.title)
        lbl_title.setObjectName("PageTitle")
        title_box.addWidget(lbl_title)
        if self.subtitle:
            lbl_sub = QLabel(self.subtitle)
            lbl_sub.setObjectName("Subtitle")
            title_box.addWidget(lbl_sub)
        head_row.addLayout(title_box)
        head_row.addStretch()
        root.addLayout(head_row)

        # Поиск
        if self.searchable:
            row = QHBoxLayout()
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Поиск по таблице…")
            self.search_input.returnPressed.connect(self.search)
            row.addWidget(self.search_input, 1)

            btn_find = QPushButton("Найти")
            btn_find.setObjectName("Primary")
            btn_find.setIcon(_icon("search", color=COLORS["on_primary"]))
            btn_find.clicked.connect(self.search)
            row.addWidget(btn_find)

            btn_reset = QPushButton("Сбросить")
            btn_reset.setIcon(_icon("refresh"))
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

        # ---- История изменений выбранной записи (под таблицей) ----
        # Один переиспользуемый контейнер: в нём показываем либо
        # карточку истории, либо тихую подсказку.
        self.history_frame = QFrame()
        self.history_frame.setObjectName("HistoryArea")
        self.history_lay = QVBoxLayout(self.history_frame)
        self.history_lay.setContentsMargins(0, 0, 0, 0)
        self.history_lay.setSpacing(6)
        self._hint = EmptyHint()
        self._history_widget = None
        self.history_lay.addWidget(self._hint)
        root.addWidget(self.history_frame)

        # Форма
        form_card = QFrame()
        form_card.setObjectName("Card")
        form_lay = QVBoxLayout(form_card)
        form_lay.setContentsMargins(14, 10, 14, 12)

        lbl_form = QLabel("Карточка записи")
        lbl_form.setObjectName("GroupBox")
        form_lay.addWidget(lbl_form)

        grid = QHBoxLayout()
        for f in self.fields:
            name, label = f[0], f[1]
            kind = f[2] if len(f) > 2 else "text"
            col = QVBoxLayout()
            col.addWidget(QLabel(label))
            inp = _make_field(kind, self.field_options(name))
            self._inputs[name] = inp
            col.addWidget(inp)
            grid.addLayout(col)
        form_lay.addLayout(grid)

        # Кнопка дополнительного действия раздела (например «Откликнуться»)
        if self.action_button_text and self.perm("add"):
            btn_action = QPushButton(self.action_button_text)
            btn_action.setObjectName("Primary")
            btn_action.setIcon(_icon(self.action_button_icon or "send",
                                     color=COLORS["on_primary"]))
            btn_action.clicked.connect(self.on_action_button)
            row_ab = QHBoxLayout()
            row_ab.addWidget(btn_action)
            row_ab.addStretch()
            form_lay.addLayout(row_ab)
        root.addWidget(form_card)

        # Кнопки (с кастомными чёрно-белыми значками)
        btns = QHBoxLayout()
        self.btn_add = QPushButton("Добавить")
        self.btn_add.setObjectName("Primary")
        self.btn_add.setIcon(_icon("plus", color=COLORS["on_primary"]))
        self.btn_add.clicked.connect(self.add_record)

        self.btn_edit = QPushButton("Изменить")
        self.btn_edit.setIcon(_icon("edit"))
        self.btn_edit.clicked.connect(self.update_record)

        self.btn_del = QPushButton("Удалить")
        self.btn_del.setObjectName("Danger")
        self.btn_del.setIcon(_icon("trash", color=COLORS["danger"]))
        self.btn_del.clicked.connect(self.delete_record)

        self.btn_clear = QPushButton("Очистить форму")
        self.btn_clear.setIcon(_icon("refresh"))
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

    # ---------------- История под записью ----------------
    def _swap_history_widget(self, widget):
        """Показать в контейнере истории либо карточку, либо подсказку."""
        if self._history_widget is not None:
            self.history_lay.removeWidget(self._history_widget)
            self._history_widget.setParent(None)
            self._history_widget.deleteLater()
            self._history_widget = None
        if widget is not None:
            self.history_lay.addWidget(widget)
            self._history_widget = widget
            self._hint.setVisible(False)
        else:
            self._hint.setVisible(True)

    def refresh_history(self):
        """Показать историю изменений текущей выбранной записи."""
        card = None
        if self.entity_type and self.current_id is not None:
            card = history_card(self.entity_type, self.current_id)
        self._swap_history_widget(card)

    # ---------------- Данные ----------------
    def value(self, name):
        """Значение поля формы по имени (QLineEdit или QComboBox)."""
        w = self._inputs[name]
        text = w.currentText() if hasattr(w, "currentText") else w.text()
        return text.strip()

    def set_values(self, mapping):
        for k, v in mapping.items():
            w = self._inputs.get(k)
            if w is None:
                continue
            text = "" if v is None else str(v)
            if hasattr(w, "setCurrentText"):
                w.setCurrentText(text)
            else:
                w.setText(text)

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
            self.current_id = None
            self.refresh_history()
            return
        self.fill_form_from_row(sel[0].row())
        self.refresh_history()

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
        rid = self.current_id
        try:
            self.do_update()
            self.load_data()
            self.clear_form()
            # оставляем выбранным изменённый объект и освежаем его историю
            self._select_row_by_id(rid)
            self.refresh_history()
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
            self.refresh_history()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def _select_row_by_id(self, rec_id):
        for i in range(self.table.rowCount()):
            it = self.table.item(i, 0)
            if it is not None and it.text() == str(rec_id):
                self.table.selectRow(i)
                return True
        return False

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
