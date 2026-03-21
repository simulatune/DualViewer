"""QPainter-drawn transport icons."""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap, QPolygonF

from ui.theme import THEME


def _make_pixmap(size: int, color: str, draw_fn) -> QPixmap:
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor(color))
    p.setPen(Qt.NoPen)
    draw_fn(p, size)
    p.end()
    return pm


def _draw_play(p: QPainter, s: int):
    cx, cy = s / 2, s / 2
    r = s * 0.32
    p.drawPolygon(QPolygonF([
        QPointF(cx - r * 0.7, cy - r),
        QPointF(cx + r, cy),
        QPointF(cx - r * 0.7, cy + r),
    ]))


def _draw_pause(p: QPainter, s: int):
    cx, cy = s / 2, s / 2
    bw, bh, gap = s * 0.13, s * 0.52, s * 0.1
    p.drawRoundedRect(QRectF(cx - gap - bw, cy - bh / 2, bw, bh), 1.5, 1.5)
    p.drawRoundedRect(QRectF(cx + gap, cy - bh / 2, bw, bh), 1.5, 1.5)


def _draw_step_left(p: QPainter, s: int):
    cx, cy = s / 2, s / 2
    r = s * 0.28
    p.drawPolygon(QPolygonF([
        QPointF(cx + r * 0.7, cy - r),
        QPointF(cx - r, cy),
        QPointF(cx + r * 0.7, cy + r),
    ]))


def _draw_step_right(p: QPainter, s: int):
    cx, cy = s / 2, s / 2
    r = s * 0.28
    p.drawPolygon(QPolygonF([
        QPointF(cx - r * 0.7, cy - r),
        QPointF(cx + r, cy),
        QPointF(cx - r * 0.7, cy + r),
    ]))


def icon_play(size: int = 26, color: str = THEME["bg_darkest"]) -> QIcon:
    return QIcon(_make_pixmap(size, color, _draw_play))


def icon_pause(size: int = 26, color: str = THEME["bg_darkest"]) -> QIcon:
    return QIcon(_make_pixmap(size, color, _draw_pause))


def icon_step_left(size: int = 28, color: str = THEME["text_secondary"]) -> QIcon:
    return QIcon(_make_pixmap(size, color, _draw_step_left))


def icon_step_right(size: int = 28, color: str = THEME["text_secondary"]) -> QIcon:
    return QIcon(_make_pixmap(size, color, _draw_step_right))
