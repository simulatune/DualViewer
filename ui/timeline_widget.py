"""Custom-painted timeline — overlap region, trim range, playhead, click/drag seek."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui.theme import THEME


class TimelineWidget(QWidget):

    position_changed = Signal(float)  # 0.0–1.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(28)
        self.setMaximumHeight(28)
        self.setCursor(Qt.PointingHandCursor)

        self._position = 0.0
        self._trim_start = 0.0
        self._trim_end = 1.0
        self._overlap_start = 0.0
        self._overlap_end = 1.0
        self._dragging = False

    def is_dragging(self) -> bool:
        return self._dragging

    def set_position(self, pos: float):
        self._position = max(0.0, min(1.0, pos))
        self.update()

    def set_trim(self, start: float, end: float):
        self._trim_start = max(0.0, min(1.0, start))
        self._trim_end = max(0.0, min(1.0, end))
        self.update()

    def set_overlap(self, start: float, end: float):
        self._overlap_start = max(0.0, min(1.0, start))
        self._overlap_end = max(0.0, min(1.0, end))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        painter.fillRect(0, 0, w, h, QColor(THEME["timeline_bg"]))

        # Overlap region
        ox0, ox1 = int(self._overlap_start * w), int(self._overlap_end * w)
        painter.fillRect(ox0, 0, ox1 - ox0, h, QColor(THEME["progress_bg"]))

        # Trim region
        tx0, tx1 = int(self._trim_start * w), int(self._trim_end * w)
        painter.fillRect(tx0, 0, tx1 - tx0, h, QColor(THEME["accent"] + "30"))

        # Trim boundary lines
        pen = QPen(QColor(THEME["accent"]), 2)
        painter.setPen(pen)
        painter.drawLine(tx0, 0, tx0, h)
        painter.drawLine(tx1, 0, tx1, h)

        # I/O labels
        painter.setPen(QColor(THEME["accent"]))
        font = painter.font()
        font.setPixelSize(9)
        painter.setFont(font)
        painter.drawText(tx0 + 3, 10, "I")
        painter.drawText(tx1 - 9, 10, "O")

        # Playhead
        px = int(self._position * w)
        painter.setPen(QPen(QColor(THEME["playhead"]), 2))
        painter.drawLine(px, 0, px, h)

        painter.end()

    def _x_to_ratio(self, x: float) -> float:
        return max(0.0, min(1.0, x / max(1, self.width())))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self.position_changed.emit(self._x_to_ratio(event.position().x()))
            self.window().setFocus()

    def mouseMoveEvent(self, event):
        if self._dragging:
            self.position_changed.emit(self._x_to_ratio(event.position().x()))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._dragging:
            self._dragging = False
