"""Sync controls — method selector, offset adjustment, auto-sync button."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QPushButton, QSpinBox, QWidget,
)

from ui.i18n import tr
from ui.theme import THEME


class SyncControl(QWidget):

    sync_requested = Signal()
    offset_changed = Signal(int)

    def __init__(self, fps: float = 30.0, parent=None):
        super().__init__(parent)
        self.setObjectName("strip")
        self._fps = fps
        self._init_ui()

    def _init_ui(self):
        row = QHBoxLayout(self)
        row.setContentsMargins(8, 4, 8, 4)
        row.setSpacing(6)

        self._method_label = QLabel(tr("method"))
        row.addWidget(self._method_label)

        self._method_combo = QComboBox()
        self._method_combo.addItems([tr("auto_audio"), tr("manual")])
        self._method_combo.setFixedWidth(140)
        self._method_combo.currentIndexChanged.connect(self._on_method_changed)
        row.addWidget(self._method_combo)

        self._confidence_title = QLabel(tr("confidence"))
        row.addWidget(self._confidence_title)

        self._confidence_label = QLabel(tr("confidence_default"))
        self._confidence_label.setFixedWidth(40)
        row.addWidget(self._confidence_label)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet(f"color: {THEME['text_secondary']};")
        self._status_label.setVisible(False)
        row.addWidget(self._status_label)

        row.addStretch()

        self._offset_label = QLabel(tr("offset"))
        row.addWidget(self._offset_label)

        self._offset_spin = QSpinBox()
        self._offset_spin.setRange(-9999, 9999)
        self._offset_spin.setValue(0)
        self._offset_spin.setSuffix(tr("suffix_frame"))
        self._offset_spin.setFixedWidth(90)
        self._offset_spin.valueChanged.connect(self._on_offset_spin_changed)
        row.addWidget(self._offset_spin)

        self._offset_sec_label = QLabel("(0.000s)")
        self._offset_sec_label.setStyleSheet(f"color: {THEME['text_secondary']};")
        self._offset_sec_label.setFixedWidth(65)
        row.addWidget(self._offset_sec_label)

        self._btn_sync = QPushButton(tr("auto_sync"))
        self._btn_sync.setObjectName("primaryBtn")
        self._btn_sync.clicked.connect(self.sync_requested.emit)
        row.addWidget(self._btn_sync)

        self._btn_reset = QPushButton(tr("reset"))
        self._btn_reset.clicked.connect(lambda: self._offset_spin.setValue(0))
        row.addWidget(self._btn_reset)

    def retranslate(self):
        self._method_label.setText(tr("method"))
        cur_idx = self._method_combo.currentIndex()
        self._method_combo.blockSignals(True)
        self._method_combo.clear()
        self._method_combo.addItems([tr("auto_audio"), tr("manual")])
        self._method_combo.setCurrentIndex(cur_idx)
        self._method_combo.blockSignals(False)
        self._confidence_title.setText(tr("confidence"))
        self._offset_label.setText(tr("offset"))
        self._offset_spin.setSuffix(tr("suffix_frame"))
        self._btn_sync.setText(tr("auto_sync"))
        self._btn_reset.setText(tr("reset"))

    def set_fps(self, fps: float):
        self._fps = fps
        self._update_offset_sec_label()

    def _on_offset_spin_changed(self, frames: int):
        self._update_offset_sec_label()
        self.offset_changed.emit(frames)

    def _update_offset_sec_label(self):
        frames = self._offset_spin.value()
        secs = frames / self._fps if self._fps > 0 else 0
        self._offset_sec_label.setText(f"({secs:+.3f}s)")

    def _on_method_changed(self, index: int):
        # index 0 = auto, 1 = manual
        self._btn_sync.setEnabled(index != 1)

    def get_method_index(self) -> int:
        return self._method_combo.currentIndex()

    def set_syncing(self, syncing: bool):
        self._btn_sync.setEnabled(not syncing)
        self._method_combo.setEnabled(not syncing)
        if syncing:
            self._btn_sync.setText(tr("syncing"))
            self._status_label.setText(tr("analyzing"))
            self._status_label.setStyleSheet(f"color: {THEME['text_secondary']};")
            self._status_label.setVisible(True)
        else:
            self._btn_sync.setText(tr("auto_sync"))

    def set_result(self, offset_frames: int, offset_seconds: float,
                   confidence: float, method: str):
        self._offset_spin.setValue(offset_frames)

        if confidence >= 0.7:
            color = THEME["confidence_high"]
            level = tr("confidence_high")
        elif confidence >= 0.4:
            color = THEME["confidence_mid"]
            level = tr("confidence_mid")
        else:
            color = THEME["confidence_low"]
            level = tr("confidence_low")

        self._confidence_label.setText(f"{confidence:.0%}")
        self._confidence_label.setStyleSheet(f"color: {color}; font-weight: bold;")

        # Switch to matching method in combo
        method_to_idx = {
            "audio_xcorr": 0, "Audio XCorr": 0,
            "manual": 1, "Manual": 1,
        }
        idx = method_to_idx.get(method)
        if idx is not None:
            self._method_combo.setCurrentIndex(idx)

        if confidence < 0.5:
            msg = tr("sync_low_confidence", level=level)
            self._method_combo.setCurrentIndex(1)  # Manual
        else:
            msg = tr("sync_result", offset=f"{offset_seconds:+.3f}", level=level)

        self._status_label.setText(msg)
        self._status_label.setStyleSheet(f"color: {color};")
        self._status_label.setVisible(True)

    def show_error(self, message: str):
        self._status_label.setText(tr("sync_failed", message=message))
        self._status_label.setStyleSheet(f"color: {THEME['confidence_low']};")
        self._status_label.setVisible(True)
