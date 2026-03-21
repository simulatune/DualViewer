"""Import panel — select two video files."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QPushButton, QWidget

from ui.i18n import tr


class ImportPanel(QWidget):

    videos_selected = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("strip")
        self._video_a: str = ""
        self._video_b: str = ""
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        self._btn_a = QPushButton(tr("video_a"))
        self._btn_a.clicked.connect(lambda: self._select_video("a"))
        layout.addWidget(self._btn_a)

        self._label_a = QLabel(tr("not_selected"))
        self._label_a.setObjectName("muted")
        layout.addWidget(self._label_a, 1)

        sep = QLabel("|")
        sep.setObjectName("muted")
        sep.setFixedWidth(12)
        layout.addWidget(sep)

        self._btn_b = QPushButton(tr("video_b"))
        self._btn_b.clicked.connect(lambda: self._select_video("b"))
        layout.addWidget(self._btn_b)

        self._label_b = QLabel(tr("not_selected"))
        self._label_b.setObjectName("muted")
        layout.addWidget(self._label_b, 1)

    def retranslate(self):
        self._btn_a.setText(tr("video_a"))
        self._btn_b.setText(tr("video_b"))
        if not self._video_a:
            self._label_a.setText(tr("not_selected"))
        if not self._video_b:
            self._label_b.setText(tr("not_selected"))

    def _select_video(self, which: str):
        title = tr("select_video_a") if which == "a" else tr("select_video_b")
        path, _ = QFileDialog.getOpenFileName(
            self, title, "", tr("video_filter")
        )
        if not path:
            return
        if which == "a":
            self._video_a = path
            self._label_a.setText(path.split("/")[-1])
            self._label_a.setObjectName("")
            self._label_a.setStyleSheet("")
        else:
            self._video_b = path
            self._label_b.setText(path.split("/")[-1])
            self._label_b.setObjectName("")
            self._label_b.setStyleSheet("")

        if self._video_a and self._video_b:
            self.videos_selected.emit(self._video_a, self._video_b)
