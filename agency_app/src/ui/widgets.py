"""
Общие виджеты интерфейса: карточки статистики и блок истории изменений.

«История изменений» (HistoryPanel) показывается прямо под выбранной
записью в таблице — чтобы не открывать общий журнал, который виден
только администратору.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy,
)

from src.services.audit_service import get_history, format_row
from src.ui.theme import COLORS


class StatCard(QFrame):
    """Мини-карточка «показатель / значение» для отчётов и аналитики."""

    def __init__(self, title, value, accent=None, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(2)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {COLORS['muted']}; font-size: 12px; border: none; background: transparent;")
        lay.addWidget(lbl_title)

        self.value_label = QLabel(str(value))
        color = accent or COLORS["primary"]
        self.value_label.setStyleSheet(
            f"color: {color}; font-size: 20px; font-weight: bold; border: none; background: transparent;"
        )
        lay.addWidget(self.value_label)

    def set_value(self, value):
        self.value_label.setText(str(value))


def history_card(entity_type, entity_id, max_lines=6):
    """
    Возвращает готовый блок «История изменений» для конкретной записи
    либо None, если записей нет. Компактный, светлый, под таблицей.
    """
    if entity_id is None:
        return None
    rows = get_history(entity_type, entity_id)
    if not rows:
        return None

    card = QFrame()
    card.setObjectName("HistoryCard")
    lay = QVBoxLayout(card)
    lay.setContentsMargins(14, 8, 14, 8)
    lay.setSpacing(3)

    head = QLabel(f"🕒 История изменений (последние {min(len(rows), max_lines)} из {len(rows)})")
    head.setStyleSheet(
        f"color: {COLORS['muted']}; font-weight: bold; font-size: 12px; border: none; background: transparent;"
    )
    lay.addWidget(head)

    for r in rows[:max_lines]:
        action = (r.get("action") or "").upper()
        if action == "CREATE":
            color = COLORS["success"]
        elif action == "DELETE":
            color = COLORS["danger"]
        else:
            color = COLORS["primary"]
        item = QLabel(format_row(r))
        item.setWordWrap(True)
        item.setStyleSheet(f"color: {color}; font-size: 12px; border: none; background: transparent;")
        item.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lay.addWidget(item)

    return card


class EmptyHint(QLabel):
    """Тихая подсказка «выберите строку…»."""

    def __init__(self, text="Выберите запись в таблице, чтобы увидеть её историю изменений."):
        super().__init__(text)
        self.setObjectName("Subtitle")
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
