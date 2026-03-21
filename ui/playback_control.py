"""Playback controls — play/pause, step, embedded timeline, time display."""

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from ui.icons import icon_pause, icon_play, icon_step_left, icon_step_right
from ui.timeline_widget import TimelineWidget


class PlaybackControl(QWidget):

    play_pause = Signal()
    seek = Signal(int)          # position_ms
    step_frame = Signal(int)    # +1 or -1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("strip")
        self._duration_ms = 0
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        self._btn_prev = QPushButton()
        self._btn_prev.setObjectName("frameBtn")
        self._btn_prev.setFixedSize(28, 28)
        self._btn_prev.setIcon(icon_step_left())
        self._btn_prev.setIconSize(QSize(28, 28))
        self._btn_prev.clicked.connect(lambda: self.step_frame.emit(-1))
        layout.addWidget(self._btn_prev)

        self._btn_play = QPushButton()
        self._btn_play.setObjectName("playBtn")
        self._btn_play.setFixedSize(26, 26)
        self._icon_play = icon_play()
        self._icon_pause = icon_pause()
        self._btn_play.setIcon(self._icon_play)
        self._btn_play.setIconSize(QSize(16, 16))
        self._btn_play.clicked.connect(self.play_pause.emit)
        layout.addWidget(self._btn_play)

        self._btn_next = QPushButton()
        self._btn_next.setObjectName("frameBtn")
        self._btn_next.setFixedSize(28, 28)
        self._btn_next.setIcon(icon_step_right())
        self._btn_next.setIconSize(QSize(28, 28))
        self._btn_next.clicked.connect(lambda: self.step_frame.emit(1))
        layout.addWidget(self._btn_next)

        self.timeline = TimelineWidget()
        layout.addWidget(self.timeline, 1)

        self._time_label = QLabel("00:00.000 / 00:00.000")
        self._time_label.setObjectName("mono")
        self._time_label.setFixedWidth(155)
        layout.addWidget(self._time_label)

        self.timeline.position_changed.connect(self._on_timeline_seek)

    def _on_timeline_seek(self, ratio: float):
        pos_ms = int(ratio * self._duration_ms)
        self.seek.emit(pos_ms)
        # Update playhead directly (update_position is blocked by is_dragging guard)
        self.timeline.set_position(ratio)
        self._time_label.setText(
            f"{self._format_time(pos_ms)} / {self._format_time(self._duration_ms)}"
        )

    def is_dragging(self) -> bool:
        return self.timeline.is_dragging()

    def set_duration(self, duration_ms: int):
        self._duration_ms = duration_ms

    def update_position(self, position_ms: int):
        if self.timeline.is_dragging():
            return
        self._time_label.setText(
            f"{self._format_time(position_ms)} / {self._format_time(self._duration_ms)}"
        )
        if self._duration_ms > 0:
            self.timeline.set_position(position_ms / self._duration_ms)

    def set_playing(self, is_playing: bool):
        self._btn_play.setIcon(self._icon_pause if is_playing else self._icon_play)

    @staticmethod
    def _format_time(ms: int) -> str:
        s = ms / 1000
        m = int(s // 60)
        s = s % 60
        return f"{m:02d}:{s:06.3f}"
