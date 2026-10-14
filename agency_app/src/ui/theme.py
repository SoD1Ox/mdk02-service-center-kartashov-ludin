"""
Единая тема оформления приложения (QSS-стили + палитра).

Все разделы и окна берут цвета и стили отсюда, чтобы интерфейс
выглял единообразно и легко настраивался в одном месте.
"""

# ---------------- Палитра ----------------
COLORS = {
    "primary": "#2f6fed",        # основной акцент (кнопки, выделение)
    "primary_dark": "#1e4fb8",
    "bg": "#f4f6fa",             # фон окна
    "sidebar": "#1d2433",        # тёмный сайдбар
    "sidebar_text": "#cfd6e4",
    "card": "#ffffff",           # карточки/таблицы
    "border": "#dde3ee",
    "text": "#273043",
    "muted": "#7b8496",
    "success": "#1aa260",
    "danger": "#d64545",
    "warning": "#e0a100",
}

ROLE_COLORS = {
    "admin": "#d64545",
    "manager": "#2f6fed",
    "director": "#7b3ff2",
    "employer": "#1aa260",
    "candidate": "#e0a100",
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
    """QSS для главного окна и всех разделов."""
    c = COLORS
    return f"""
    QWidget {{
        font-family: 'Segoe UI', 'Arial', sans-serif;
        font-size: 13px;
        color: {c['text']};
        background: {c['bg']};
    }}

    /* ---------- Сайдбар ---------- */
    QFrame#Sidebar {{
        background: {c['sidebar']};
        border: none;
    }}
    QLabel#SidebarTitle {{
        color: #ffffff;
        font-size: 16px;
        font-weight: bold;
        padding: 4px;
    }}
    QLabel#SidebarUser {{
        color: #ffffff;
        font-size: 14px;
        font-weight: bold;
        padding: 4px;
    }}
    QLabel#SidebarRole {{
        color: {c['sidebar_text']};
        font-size: 12px;
        padding: 2px 4px;
    }}
    QLabel#Section {{
        color: {c['sidebar_text']};
        font-size: 11px;
        font-weight: bold;
        padding-top: 14px;
        padding-left: 6px;
        letter-spacing: 1px;
    }}
    QListWidget#Nav {{
        background: {c['sidebar']};
        border: none;
        outline: none;
    }}
    QListWidget#Nav::item {{
        color: {c['sidebar_text']};
        padding: 10px 14px;
        border-radius: 8px;
        margin: 2px 8px;
    }}
    QListWidget#Nav::item:hover {{
        background: rgba(255, 255, 255, 0.08);
        color: #ffffff;
    }}
    QListWidget#Nav::item:selected {{
        background: {c['primary']};
        color: #ffffff;
        font-weight: bold;
    }}

    QPushButton#Logout {{
        background: transparent;
        color: {c['sidebar_text']};
        border: 1px solid rgba(255,255,255,0.25);
        border-radius: 8px;
        padding: 8px;
    }}
    QPushButton#Logout:hover {{
        background: {c['danger']};
        border-color: {c['danger']};
        color: #ffffff;
    }}

    /* ---------- Контент ---------- */
    QLabel#PageTitle {{
        font-size: 22px;
        font-weight: bold;
        color: {c['text']};
        padding-bottom: 2px;
    }}
    QLabel#Subtitle {{
        font-size: 13px;
        color: {c['muted']};
        padding-bottom: 10px;
    }}
    QLabel#GroupBox {{
        font-size: 14px;
        font-weight: bold;
        color: {c['text']};
    }}

    QFrame#Card {{
        background: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 10px;
    }}

    /* ---------- Таблицы ---------- */
    QTableView, QTableWidget {{
        background: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        gridline-color: {c['border']};
        selection-background-color: {c['primary']};
        selection-color: #ffffff;
    }}
    QHeaderView::section {{
        background: #eef1f7;
        color: {c['text']};
        font-weight: bold;
        padding: 6px 8px;
        border: none;
        border-right: 1px solid {c['border']};
        border-bottom: 1px solid {c['border']};
    }}
    QTableWidget::item {{ padding: 4px 6px; }}

    /* ---------- Поля ввода ---------- */
    QLineEdit, QComboBox, QTextEdit, QPlainTextEdit {{
        background: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 6px 8px;
        selection-background-color: {c['primary']};
    }}
    QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
        border: 1px solid {c['primary']};
    }}
    QLineEdit:read-only {{
        background: #f0f2f6;
        color: {c['muted']};
    }}

    /* ---------- Кнопки ---------- */
    QPushButton {{
        background: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 7px 14px;
        font-weight: 600;
    }}
    QPushButton:hover {{ background: #eef1f7; }}
    QPushButton:pressed {{ background: #e2e7f0; }}
    QPushButton:disabled {{ color: {c['muted']}; background: #eef1f7; }}

    QPushButton#Primary {{
        background: {c['primary']};
        border: 1px solid {c['primary']};
        color: #ffffff;
    }}
    QPushButton#Primary:hover {{ background: {c['primary_dark']}; }}

    QPushButton#Danger {{
        background: {c['danger']};
        border: 1px solid {c['danger']};
        color: #ffffff;
    }}
    QPushButton#Danger:hover {{ background: #b83636; }}

    /* ---------- Прочее ---------- */
    QStatusBar {{ background: {c['card']}; border-top: 1px solid {c['border']}; }}
    QScrollBar:vertical {{ width: 10px; background: transparent; }}
    QScrollBar::handle:vertical {{
        background: #c3cad8; border-radius: 5px; min-height: 30px;
    }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
    """


def login_qss() -> str:
    """QSS для окна входа (тёмный градиентный фон карточки)."""
    c = COLORS
    return f"""
    QWidget {{
        font-family: 'Segoe UI', 'Arial', sans-serif;
        font-size: 13px;
        color: {c['text']};
    }}
    QFrame#LoginCard {{
        background: {c['card']};
        border: 1px solid {c['border']};
        border-radius: 14px;
    }}
    QLabel#LoginTitle {{
        font-size: 20px;
        font-weight: bold;
        color: {c['text']};
    }}
    QLabel#LoginSub {{
        font-size: 12px;
        color: {c['muted']};
    }}
    QLabel {{ color: {c['text']}; }}
    QLineEdit {{
        background: #f7f9fc;
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 9px 10px;
    }}
    QLineEdit:focus {{ border: 1px solid {c['primary']}; }}
    QPushButton#LoginBtn {{
        background: {c['primary']};
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px;
        font-size: 14px;
        font-weight: bold;
    }}
    QPushButton#LoginBtn:hover {{ background: {c['primary_dark']}; }}
    QLabel#Hint {{ color: {c['muted']}; font-size: 11px; }}
    """
