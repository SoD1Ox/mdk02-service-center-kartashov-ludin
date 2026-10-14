"""Кастомные значки приложения.

Все иконки рисуются кодом (мини-SVG) — никаких сторонних картинок и цветных
эмодзи. Иконка — это чёрно-белый контурный рисунок: по умолчанию он красится
в цвет текста виджета, а на мятной кнопке — в тёмный, чтобы оставаться
читаемой.

Использование:
    from src.ui.icons import icon
    button.setIcon(icon("edit", color="#08130f"))
    item.setIcon(icon("users", color="#9fc4b8"))
"""
from PyQt5.QtCore import QByteArray, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QApplication

# viewBox у всех иконок 24x24, обводка stroke-width=1.8
_PATHS = {
    # --- навигация по разделам ---
    "users": '<circle cx="9" cy="8" r="3.2"/><path d="M3.5 19c0-3.4 2.4-5.2 5.5-5.2s5.5 1.8 5.5 5.2"/>'
             '<circle cx="17" cy="9" r="2.4"/><path d="M16 13.9c2.8.2 4.5 1.9 4.5 4.6"/>',
    "doc": '<rect x="6" y="3" width="12" height="18" rx="2"/>'
           '<path d="M9 8h6M9 12h6M9 16h4"/>',
    "star": '<path d="M12 3.5l2.6 5.3 5.9.9-4.2 4.1 1 5.9-5.3-2.8-5.3 2.8 1-5.9L3.5 9.7l5.9-.9z"/>',
    "building": '<rect x="4" y="4" width="10" height="17" rx="1"/>'
                '<path d="M14 9h5a1 1 0 0 1 1 1v11"/>'
                '<path d="M7 8h1M10 8h1M7 11.5h1M10 11.5h1M7 15h1M10 15h1M7 18.5h4"/>',
    "briefcase": '<rect x="3" y="8" width="18" height="12" rx="2"/>'
                 '<path d="M9 8V6a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/>'
                 '<path d="M3 13.5h18"/>',
    "mail": '<rect x="3" y="5.5" width="18" height="13" rx="2"/>'
            '<path d="M3.5 7l8.5 6.5L20.5 7"/>',
    "handshake": '<path d="M2.5 12l4-4 5 4.5 2-1.5 4 3.5"/>'
                 '<path d="M2.5 12l4 4 3.5-3 3 2.5 3-2.5 5.5-4.5"/>'
                 '<path d="M6.5 8V5.5h5M17.5 12V5.5h-4"/>',
    "chart": '<path d="M4 20V4"/><path d="M4 20h16"/>'
             '<rect x="7.5" y="12" width="3" height="5.5"/>'
             '<rect x="12.5" y="8.5" width="3" height="9"/>'
             '<rect x="17.5" y="5.5" width="3" height="12"/>',
    "trend": '<path d="M4 20V4"/><path d="M4 20h16"/>'
             '<path d="M6.5 15.5l4-4.5 3 2.5 5.5-6.5"/>'
             '<path d="M15.5 7h4v4"/>',
    "shield": '<path d="M12 3l7 2.5V12c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V5.5z"/>'
              '<path d="M8.8 12l2.2 2.2 4.2-4.4"/>',

    # --- действия ---
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "edit": '<path d="M4 20h4L20 8l-4-4L4 16z"/><path d="M14 6l4 4"/>',
    "trash": '<path d="M4 7h16"/><path d="M9 7V4.8A.8.8 0 0 1 9.8 4h4.4a.8.8 0 0 1 .8.8V7"/>'
             '<path d="M6.5 7l.9 12.2a1.5 1.5 0 0 0 1.5 1.3h6.2a1.5 1.5 0 0 0 1.5-1.3L17.5 7"/>'
             '<path d="M10 11v6M14 11v6"/>',
    "refresh": '<path d="M20 12a8 8 0 1 1-2.3-5.6"/>'
               '<path d="M20 4v4.5h-4.5"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5 5"/>',
    "logout": '<path d="M9 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h3"/>'
              '<path d="M15 8l4 4-4 4"/><path d="M19 12H9"/>',
    "lock": '<rect x="5.5" y="10.5" width="13" height="9.5" rx="2"/>'
            '<path d="M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5"/><path d="M12 14v2.5"/>',
    "clock": '<circle cx="12" cy="12" r="8"/><path d="M12 7.5V12l3 2"/>',
    "key": '<circle cx="8" cy="14" r="4"/><path d="M10.8 11.2L20 4"/>'
           '<path d="M16.5 7.5l2.5 2.5M18.5 5.5l2.5 2.5"/>',
}

_CACHE = {}


def _color_for(color):
    if color is None:
        pal = QApplication.instance().palette()
        if pal is not None:
            return pal.color(pal.WindowText).name()
        return "#dfe9e4"
    return color


def icon(name, color=None, size=24):
    """Вернуть QIcon по имени; неизвестное имя -> пустая иконка."""
    body = _PATHS.get(name)
    if body is None:
        return QIcon()
    col = _color_for(color)
    key = (name, col, size)
    cached = _CACHE.get(key)
    if cached is not None:
        return cached

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        f'width="{size}" height="{size}" fill="none" stroke="{col}" '
        f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
        f"{body}</svg>"
    )
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    painter = None
    from PyQt5.QtGui import QPainter
    painter = QPainter(pm)
    renderer.render(painter)
    painter.end()
    ic = QIcon(pm)
    _CACHE[key] = ic
    return ic
