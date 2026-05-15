from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QIcon, QPainter, QPen, QPixmap, QPolygon


def toolbar_icon(name: str, dark_theme: bool = False) -> QIcon:
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    ink = QColor("#e8edf2") if dark_theme else QColor("#263238")
    accent = QColor("#69a7ff") if dark_theme else QColor("#2f80ed")
    warning = QColor("#ffd866") if dark_theme else QColor("#f2c94c")
    danger = QColor("#ff6b6b") if dark_theme else QColor("#d64545")
    painter.setPen(QPen(ink, 2))
    painter.setBrush(Qt.NoBrush)

    def draw_page(x: int = 8, y: int = 5, w: int = 16, h: int = 22) -> None:
        painter.drawRect(x, y, w, h)
        painter.drawLine(x + w - 5, y, x + w, y + 5)
        painter.drawLine(x + w - 5, y, x + w - 5, y + 5)

    def draw_arrow(points: list[QPoint], color: QColor = accent) -> None:
        painter.setPen(QPen(color, 2))
        painter.setBrush(QBrush(color))
        painter.drawPolygon(QPolygon(points))
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(ink, 2))

    if name == "open":
        painter.drawRect(5, 11, 22, 14)
        painter.drawLine(5, 11, 11, 6)
        painter.drawLine(11, 6, 18, 6)
        painter.drawLine(18, 6, 22, 11)
    elif name == "save":
        painter.drawRect(7, 5, 18, 22)
        painter.drawRect(10, 7, 10, 6)
        painter.drawRect(11, 19, 10, 6)
    elif name == "markdown":
        draw_page()
        painter.setFont(QFont("Arial", 7, QFont.Bold))
        painter.drawText(QRect(8, 14, 16, 10), Qt.AlignCenter, "MD")
    elif name == "html":
        draw_page()
        painter.setFont(QFont("Arial", 7, QFont.Bold))
        painter.drawText(QRect(7, 14, 18, 10), Qt.AlignCenter, "HTML")
    elif name == "previous":
        draw_arrow([QPoint(8, 16), QPoint(18, 8), QPoint(18, 24)])
        painter.drawLine(19, 16, 26, 16)
    elif name == "next":
        draw_arrow([QPoint(24, 16), QPoint(14, 8), QPoint(14, 24)])
        painter.drawLine(6, 16, 13, 16)
    elif name in {"zoom_in", "zoom_out"}:
        painter.drawEllipse(7, 7, 14, 14)
        painter.drawLine(19, 19, 26, 26)
        painter.drawLine(11, 14, 17, 14)
        if name == "zoom_in":
            painter.drawLine(14, 11, 14, 17)
    elif name == "rotate":
        painter.drawArc(7, 7, 18, 18, 25 * 16, 290 * 16)
        draw_arrow([QPoint(23, 7), QPoint(25, 15), QPoint(17, 12)])
    elif name == "delete":
        painter.drawLine(10, 9, 22, 9)
        painter.drawLine(13, 6, 19, 6)
        painter.drawRect(11, 11, 10, 15)
        painter.drawLine(14, 14, 14, 23)
        painter.drawLine(18, 14, 18, 23)
    elif name == "move_up":
        draw_arrow([QPoint(16, 6), QPoint(8, 16), QPoint(13, 16), QPoint(13, 26), QPoint(19, 26), QPoint(19, 16), QPoint(24, 16)])
    elif name == "move_down":
        draw_arrow([QPoint(16, 26), QPoint(8, 16), QPoint(13, 16), QPoint(13, 6), QPoint(19, 6), QPoint(19, 16), QPoint(24, 16)])
    elif name == "text":
        painter.setFont(QFont("Arial", 18, QFont.Bold))
        painter.drawText(QRect(6, 4, 18, 22), Qt.AlignCenter, "T")
        painter.setPen(QPen(accent, 2))
        painter.drawLine(24, 18, 24, 26)
        painter.drawLine(20, 22, 28, 22)
    elif name == "edit_text":
        painter.setFont(QFont("Arial", 15, QFont.Bold))
        painter.drawText(QRect(4, 4, 18, 20), Qt.AlignCenter, "T")
        painter.setPen(QPen(accent, 2))
        painter.drawLine(17, 24, 25, 16)
        painter.drawLine(22, 13, 27, 18)
        painter.drawLine(16, 25, 21, 24)
    elif name == "highlight":
        painter.setBrush(QBrush(warning))
        painter.setPen(QPen(warning, 2))
        painter.drawRect(6, 19, 20, 5)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(ink, 2))
        painter.drawLine(8, 10, 24, 10)
        painter.drawLine(8, 15, 21, 15)
    elif name == "remove_highlight":
        painter.setBrush(QBrush(warning))
        painter.setPen(QPen(warning, 2))
        painter.drawRect(6, 19, 20, 5)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(danger, 3))
        painter.drawLine(8, 24, 25, 7)
    elif name == "image":
        painter.drawRect(6, 7, 20, 18)
        painter.drawEllipse(19, 10, 4, 4)
        painter.drawLine(8, 23, 14, 16)
        painter.drawLine(14, 16, 18, 20)
        painter.drawLine(18, 20, 23, 14)
    elif name == "merge":
        draw_page(6, 7, 12, 17)
        draw_page(14, 5, 12, 19)
        painter.setPen(QPen(accent, 2))
        painter.drawLine(16, 16, 24, 16)
        painter.drawLine(20, 12, 20, 20)
    elif name == "split":
        draw_page(8, 5, 16, 22)
        painter.setPen(QPen(danger, 2, Qt.DashLine))
        painter.drawLine(16, 7, 16, 25)
        painter.setPen(QPen(ink, 2))
        painter.drawEllipse(9, 12, 5, 5)
        painter.drawEllipse(18, 12, 5, 5)
    elif name == "metadata":
        painter.drawEllipse(7, 5, 18, 18)
        painter.setFont(QFont("Arial", 14, QFont.Bold))
        painter.drawText(QRect(7, 6, 18, 18), Qt.AlignCenter, "i")
        painter.drawLine(9, 27, 23, 27)
    elif name == "compress":
        draw_page(6, 6, 20, 20)
        painter.setPen(QPen(accent, 2))
        painter.drawLine(11, 16, 21, 16)
        painter.drawLine(11, 16, 15, 12)
        painter.drawLine(11, 16, 15, 20)
        painter.drawLine(21, 16, 17, 12)
        painter.drawLine(21, 16, 17, 20)
    elif name == "protect":
        painter.drawRoundedRect(8, 14, 16, 11, 2, 2)
        painter.drawArc(11, 6, 10, 12, 0, 180 * 16)
    elif name == "unlock":
        painter.drawRoundedRect(8, 14, 16, 11, 2, 2)
        painter.drawArc(15, 6, 10, 12, 0, 180 * 16)
    elif name == "pdf_to_images":
        draw_page(5, 5, 13, 18)
        painter.drawRect(15, 12, 12, 11)
        painter.drawLine(17, 21, 20, 17)
        painter.drawLine(20, 17, 23, 20)
    elif name == "images_to_pdf":
        painter.drawRect(5, 7, 13, 11)
        painter.drawLine(7, 16, 11, 12)
        painter.drawLine(11, 12, 15, 16)
        draw_page(16, 8, 11, 17)
    elif name == "extract_images":
        draw_page(5, 5, 14, 20)
        painter.drawRect(14, 14, 12, 10)
        painter.setPen(QPen(accent, 2))
        painter.drawLine(12, 17, 21, 17)
        painter.drawLine(21, 17, 18, 14)
        painter.drawLine(21, 17, 18, 20)
    elif name == "watermark":
        painter.setFont(QFont("Arial", 13, QFont.Bold))
        painter.setPen(QPen(accent, 2))
        painter.drawText(QRect(4, 7, 24, 18), Qt.AlignCenter, "W")
        painter.setPen(QPen(ink, 1))
        painter.drawLine(7, 24, 25, 8)
    elif name == "page_numbers":
        painter.setFont(QFont("Arial", 14, QFont.Bold))
        painter.drawText(QRect(4, 6, 24, 20), Qt.AlignCenter, "123")

    painter.end()
    return QIcon(pixmap)
