"""Единое оформление приложения: тёмно-мятная палитра, подписи и QSS для всех окон.

Требования стиля:
  * тёмно-мятная (dark mint / deep teal-green) гамма;
  * никакой цветной «эмодзи»-графики — только монохромные текстовые символы;
  * весь текст контрастный и читаемый (светлый на тёмном).
"""

# ---------------- Палитра (приглушённая тёмная мята) ----------------
# Цвета специально «глуше»: меньше ядовитой яркости, больше спокойного deep teal.
COLORS = {
    "primary": "#57b18f",        # приглушённый мятный акцент (кнопки, выделение)
    "primary_dark": "#44987a",
    "accent_soft": "rgba(87, 177, 143, 0.12)",
    "bg": "#152420",             # основной фон окна (тёмная мята)
    "bg_alt": "#1a2d27",         # чуть светлее (полосы, подложки)
    "sidebar": "#111e1a",        # сайдбар — самый тёмный
    "card": "#1e332d",           # карточки/таблицы
    "card_hover": "#254038",
    "border": "#315047",
    "text": "#d7e8e0",           # основной текст — мягкий светло-мятный
    "muted": "#8faea3",          # вторичный текст — приглушённая мята
    "on_primary": "#0d1a15",     # текст НА мятной кнопке — тёмный
    "success": "#79c9a2",
    "danger": "#e08f8f",         # мягкий кирпичный, читаемый на тёмном
    "warning": "#d9bd7e",
    "info": "#8fbcb4",
}

ROLE_COLORS = {
    "admin": "#d9bd7e",
    "manager": "#57b18f",
    "director": "#a29ac2",
    "employer": "#8fbcb4",
    "candidate": "#c99ab0",
}

ROLE_LABELS = {
    "admin": "Администратор",
    "manager": "Менеджер",
    "director": "Директор",
    "employer": "Работодатель",
    "candidate": "Соискатель",
}

ACTION_LABELS = {
    "CREATE": "Создание",
    "UPDATE": "Изменение",
    "DELETE": "Удаление",
    "LOGIN": "Вход",
}

ENTITY_LABELS = {
    "candidate": "Соискатель",
    "resume": "Резюме",
    "skill": "Навык",
    "employer": "Работодатель",
    "vacancy": "Вакансия",
    "response": "Отклик",
    "deal": "Сделка",
    "user": "Пользователь",
}


def main_qss() -> str:
    """QSS для главного окна и всех разделов (тёмная мята)."""
    c = COLORS
    return f"""
    QWidget {{
        font-family: 'Segoe UI', 'DejaVu Sans', 'Arial', sans-serif;
        font-size: 13px;
        color: {c['text']};
        background-color: {c['bg']};
    }}
    QLabel {{ color: {c['text']}; background-color: transparent; }}
    QToolTip {{
        color: {c['text']};
        background-color: {c['sidebar']};
        border: 1px solid {c['border']};
    }}

    /* ---------- Сайдбар ---------- */
    QFrame#Sidebar {{
        background-color: {c['sidebar']};
        border: none;
    }}
    QLabel#SidebarTitle {{
        color: {c['primary']};
        font-size: 16px;
        font-weight: bold;
        padding: 4px;
        background-color: transparent;
    }}
    QLabel#SidebarUser {{
        color: {c['text']};
        font-size: 14px;
        font-weight: bold;
        padding: 4px;
        background-color: transparent;
    }}
    QLabel#SidebarRole {{
        color: {c['muted']};
        font-size: 12px;
        font-weight: bold;
        padding: 2px 4px;
        background-color: transparent;
    }}
    QLabel#Section {{
        color: {c['muted']};
        font-size: 11px;
        font-weight: bold;
        padding-top: 14px;
        padding-left: 6px;
        letter-spacing: 1px;
        background-color: transparent;
    }}
    QListWidget#Nav {{
        background-color: {c['sidebar']};
        border: none;
        outline: none;
    }}
    QListWidget#Nav::item {{
        color: {c['muted']};
        padding: 10px 14px;
        border-radius: 8px;
        margin: 2px 8px;
    }}
    QListWidget#Nav::item:hover {{
        background-color: rgba(87, 177, 143, 0.10);
        color: {c['text']};
    }}
    QListWidget#Nav::item:selected {{
        background-color: {c['primary']};
        color: {c['on_primary']};
        font-weight: bold;
    }}

    QPushButton#Logout {{
        background-color: transparent;
        color: {c['muted']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 8px;
    }}
    QPushButton#Logout:hover {{
        background-color: {c['danger']};
        border-color: {c['danger']};
        color: {c['on_primary']};
    }}

    /* ---------- Контент ---------- */
    QLabel#PageTitle {{
        font-size: 22px;
        font-weight: bold;
        color: {c['text']};
        padding-bottom: 2px;
        background-color: transparent;
    }}
    QLabel#Subtitle {{
        font-size: 13px;
        color: {c['muted']};
        padding-bottom: 10px;
        background-color: transparent;
    }}
    QLabel#GroupBox {{
        font-size: 14px;
        font-weight: bold;
        color: {c['primary']};
        background-color: transparent;
    }}

    QFrame#Card {{
        background-color: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 10px;
    }}

    /* Карточка истории изменений под записью */
    QFrame#HistoryCard {{
        background-color: {c['bg_alt']};
        border: 1px solid {c['border']};
        border-left: 4px solid {c['primary']};
        border-radius: 8px;
    }}

    /* ---------- Таблицы ---------- */
    QTableView, QTableWidget {{
        background-color: {c['card']};
        alternate-background-color: {c['bg_alt']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        gridline-color: {c['border']};
        color: {c['text']};
        selection-background-color: {c['primary']};
        selection-color: {c['on_primary']};
    }}
    QTableView::item, QTableWidget::item {{
        color: {c['text']};
        padding: 4px 6px;
    }}
    QTableView::item:selected, QTableWidget::item:selected {{
        background-color: {c['primary']};
        color: {c['on_primary']};
    }}
    QHeaderView::section {{
        background-color: {c['bg_alt']};
        color: {c['primary']};
        font-weight: bold;
        padding: 6px 8px;
        border: none;
        border-right: 1px solid {c['border']};
        border-bottom: 1px solid {c['border']};
    }}

    /* ---------- Поля ввода ---------- */
    QLineEdit, QComboBox, QTextEdit, QPlainTextEdit {{
        background-color: {c['bg_alt']};
        color: {c['text']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 6px 8px;
        selection-background-color: {c['primary']};
        selection-color: {c['on_primary']};
    }}
    QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border: 1px solid {c['primary']};
    }}
    QLineEdit:read-only {{
        background-color: {c['sidebar']};
        color: {c['muted']};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 22px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {c['card']};
        color: {c['text']};
        border: 1px solid {c['border']};
        selection-background-color: {c['primary']};
        selection-color: {c['on_primary']};
    }}
    QCheckBox {{ color: {c['text']}; background-color: transparent; spacing: 6px; }}
    QCheckBox::indicator {{
        width: 16px; height: 16px;
        border: 1px solid {c['border']};
        border-radius: 4px;
        background-color: {c['bg_alt']};
    }}
    QCheckBox::indicator:checked {{
        background-color: {c['primary']};
        border-color: {c['primary']};
    }}

    /* ---------- Кнопки ---------- */
    QPushButton {{
        background-color: {c['card']};
        color: {c['text']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 7px 14px;
        font-weight: 600;
    }}
    QPushButton:hover {{ background-color: {c['card_hover']}; border-color: {c['primary']}; }}
    QPushButton:pressed {{ background-color: {c['bg_alt']}; }}
    QPushButton:disabled {{ color: {c['muted']}; background-color: {c['bg_alt']}; border-color: {c['border']}; }}

    QPushButton#Primary {{
        background-color: {c['primary']};
        border: 1px solid {c['primary']};
        color: {c['on_primary']};
    }}
    QPushButton#Primary:hover {{ background-color: {c['primary_dark']}; border-color: {c['primary_dark']}; }}
    QPushButton#Primary:disabled {{ background-color: {c['bg_alt']}; color: {c['muted']}; border-color: {c['border']}; }}

    QPushButton#Danger {{
        background-color: transparent;
        border: 1px solid {c['danger']};
        color: {c['danger']};
    }}
    QPushButton#Danger:hover {{ background-color: {c['danger']}; color: {c['on_primary']}; }}

    /* ---------- Прочее ---------- */
    QStatusBar {{ background-color: {c['sidebar']}; color: {c['muted']}; border-top: 1px solid {c['border']}; }}
    QMessageBox {{ background-color: {c['card']}; }}
    QMessageBox QLabel {{ color: {c['text']}; }}
    QDialogButtonBox QPushButton {{ min-width: 80px; }}
    QScrollBar:vertical {{ width: 10px; background: transparent; }}
    QScrollBar::handle:vertical {{
        background: {c['border']}; border-radius: 5px; min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{ background: {c['primary']}; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
    QScrollBar:horizontal {{ height: 10px; background: transparent; }}
    QScrollBar::handle:horizontal {{
        background: {c['border']}; border-radius: 5px; min-width: 30px;
    }}
    """


def login_qss() -> str:
    """QSS для окна входа (тёмная мята)."""
    c = COLORS
    return f"""
    QWidget {{
        font-family: 'Segoe UI', 'DejaVu Sans', 'Arial', sans-serif;
        font-size: 13px;
        color: {c['text']};
        background-color: {c['sidebar']};
    }}
    QFrame#LoginCard {{
        background-color: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 14px;
    }}
    QLabel#LoginTitle {{
        font-size: 21px;
        font-weight: bold;
        color: {c['primary']};
        background-color: transparent;
    }}
    QLabel#LoginSub {{
        font-size: 12px;
        color: {c['muted']};
        background-color: transparent;
    }}
    QLabel {{ color: {c['text']}; background-color: transparent; }}
    QLineEdit {{
        background-color: {c['bg_alt']};
        color: {c['text']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 9px 10px;
        selection-background-color: {c['primary']};
        selection-color: {c['on_primary']};
    }}
    QLineEdit:focus {{ border: 1px solid {c['primary']}; }}
    QPushButton#LoginBtn {{
        background-color: {c['primary']};
        color: {c['on_primary']};
        border: none;
        border-radius: 8px;
        padding: 10px;
        font-size: 14px;
        font-weight: bold;
    }}
    QPushButton#LoginBtn:hover {{ background-color: {c['primary_dark']}; }}
    QLabel#Hint {{ color: {c['muted']}; font-size: 11px; background-color: transparent; }}
    """
