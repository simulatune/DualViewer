"""Export panel — trim range, watermarks, encoding settings."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDoubleSpinBox, QFileDialog, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QProgressBar, QPushButton, QSpinBox, QVBoxLayout,
)

from ui.i18n import tr
from ui.theme import THEME


class ExportPanel(QGroupBox):

    export_requested = Signal(dict)
    preview_range = Signal()
    set_in_point = Signal()
    set_out_point = Signal()

    def __init__(self, parent=None):
        super().__init__(tr("export"), parent)
        self._max_duration = 0.0
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Row 1: trim range
        range_row = QHBoxLayout()
        range_row.setSpacing(4)

        self._btn_in = QPushButton(tr("in_point"))
        self._btn_in.clicked.connect(self.set_in_point.emit)
        range_row.addWidget(self._btn_in)

        self._start_spin = QDoubleSpinBox()
        self._start_spin.setDecimals(3)
        self._start_spin.setSuffix(tr("suffix_seconds"))
        self._start_spin.setRange(0, 9999)
        self._start_spin.valueChanged.connect(self._on_start_changed)
        range_row.addWidget(self._start_spin)

        range_row.addSpacing(8)

        self._btn_out = QPushButton(tr("out_point"))
        self._btn_out.clicked.connect(self.set_out_point.emit)
        range_row.addWidget(self._btn_out)

        self._end_spin = QDoubleSpinBox()
        self._end_spin.setDecimals(3)
        self._end_spin.setSuffix(tr("suffix_seconds"))
        self._end_spin.setRange(0, 9999)
        self._end_spin.valueChanged.connect(self._on_end_changed)
        range_row.addWidget(self._end_spin)

        range_row.addSpacing(8)

        self._duration_label = QLabel(tr("duration_label", value=0.0))
        self._duration_label.setStyleSheet(f"color: {THEME['text_secondary']};")
        range_row.addWidget(self._duration_label)

        range_row.addStretch()

        self._btn_preview = QPushButton(tr("preview"))
        self._btn_preview.clicked.connect(self.preview_range.emit)
        range_row.addWidget(self._btn_preview)

        layout.addLayout(range_row)

        # Row 2: watermarks
        wm_row = QHBoxLayout()
        self._wm_label_a = QLabel(tr("label_a"))
        wm_row.addWidget(self._wm_label_a)
        self._wm_a = QLineEdit(tr("default_wm_a"))
        wm_row.addWidget(self._wm_a)
        self._wm_label_b = QLabel(tr("label_b"))
        wm_row.addWidget(self._wm_label_b)
        self._wm_b = QLineEdit(tr("default_wm_b"))
        wm_row.addWidget(self._wm_b)
        layout.addLayout(wm_row)

        # Row 3: encoding params + export button
        param_row = QHBoxLayout()
        self._width_label = QLabel(tr("width"))
        param_row.addWidget(self._width_label)
        self._width_spin = QSpinBox()
        self._width_spin.setRange(640, 7680)
        self._width_spin.setValue(1920)
        self._width_spin.setSingleStep(2)
        param_row.addWidget(self._width_spin)

        self._crf_label = QLabel(tr("crf"))
        param_row.addWidget(self._crf_label)
        self._crf_spin = QSpinBox()
        self._crf_spin.setRange(0, 51)
        self._crf_spin.setValue(18)
        param_row.addWidget(self._crf_spin)

        self._crf_hint = QLabel("\u24d8")
        self._crf_hint.setStyleSheet(
            f"color: {THEME['text_secondary']}; font-size: 15px; "
            "background: transparent; padding: 0 2px;"
        )
        self._crf_hint.setCursor(Qt.WhatsThisCursor)
        self._crf_hint.setToolTip(tr("crf_tooltip"))
        param_row.addWidget(self._crf_hint)

        param_row.addStretch()

        self._btn_export = QPushButton(tr("export_video"))
        self._btn_export.setObjectName("primaryBtn")
        self._btn_export.clicked.connect(self._on_export)
        param_row.addWidget(self._btn_export)
        layout.addLayout(param_row)

        # Progress bar (hidden)
        self._progress = QProgressBar()
        self._progress.setValue(0)
        self._progress.setFormat("%p%")
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        # Status label (hidden)
        self._status_label = QLabel("")
        self._status_label.setWordWrap(True)
        self._status_label.setVisible(False)
        layout.addWidget(self._status_label)

    def retranslate(self):
        self.setTitle(tr("export"))
        self._btn_in.setText(tr("in_point"))
        self._btn_out.setText(tr("out_point"))
        self._start_spin.setSuffix(tr("suffix_seconds"))
        self._end_spin.setSuffix(tr("suffix_seconds"))
        self._update_duration_label()
        self._btn_preview.setText(tr("preview"))
        self._wm_label_a.setText(tr("label_a"))
        self._wm_label_b.setText(tr("label_b"))
        self._width_label.setText(tr("width"))
        self._crf_label.setText(tr("crf"))
        self._crf_hint.setToolTip(tr("crf_tooltip"))
        if self._btn_export.isEnabled():
            self._btn_export.setText(tr("export_video"))
        else:
            self._btn_export.setText(tr("exporting"))

    # -- Range management --

    def set_default_width(self, width: int):
        self._width_spin.setValue(width + width % 2)

    def set_range_limits(self, overlap_start: float, overlap_end: float,
                         reset: bool = False):
        self._start_spin.setRange(overlap_start, overlap_end)
        self._end_spin.setRange(overlap_start, overlap_end)
        if reset:
            self._start_spin.setValue(overlap_start)
            self._end_spin.setValue(overlap_end)
        self._max_duration = overlap_end - overlap_start
        self._update_duration_label()

    def set_in(self, seconds: float):
        self._start_spin.setValue(seconds)

    def set_out(self, seconds: float):
        self._end_spin.setValue(seconds)

    def get_start(self) -> float:
        return self._start_spin.value()

    def get_end(self) -> float:
        return self._end_spin.value()

    def get_duration(self) -> float:
        return max(0, self._end_spin.value() - self._start_spin.value())

    def _on_start_changed(self):
        if self._start_spin.value() > self._end_spin.value():
            self._end_spin.blockSignals(True)
            self._end_spin.setValue(self._start_spin.value())
            self._end_spin.blockSignals(False)
        self._update_duration_label()

    def _on_end_changed(self):
        if self._end_spin.value() < self._start_spin.value():
            self._start_spin.blockSignals(True)
            self._start_spin.setValue(self._end_spin.value())
            self._start_spin.blockSignals(False)
        self._update_duration_label()

    def _update_duration_label(self):
        self._duration_label.setText(tr("duration_label", value=self.get_duration()))

    # -- Export --

    def _on_export(self):
        if self.get_duration() <= 0:
            self.show_error(tr("in_before_out"))
            return
        path, _ = QFileDialog.getSaveFileName(
            self, tr("save_dialog_title"), "comparison.mp4", tr("save_dialog_filter")
        )
        if not path:
            return
        self._status_label.setVisible(False)
        self.export_requested.emit({
            "output": path,
            "watermark_a": self._wm_a.text(),
            "watermark_b": self._wm_b.text(),
            "width": self._width_spin.value(),
            "crf": self._crf_spin.value(),
            "start_time": self.get_start(),
            "duration": self.get_duration(),
        })

    # -- Progress / status --

    def set_exporting(self, exporting: bool):
        self._btn_export.setEnabled(not exporting)
        self._progress.setVisible(exporting)
        if exporting:
            self._progress.setValue(0)
            self._status_label.setVisible(False)
            self._btn_export.setText(tr("exporting"))
        else:
            self._btn_export.setText(tr("export_video"))

    def set_progress(self, value: float):
        self._progress.setVisible(True)
        self._progress.setValue(int(value * 100))

    def show_success(self, output_path: str):
        self._progress.setValue(100)
        self._status_label.setText(tr("exported", path=output_path))
        self._status_label.setStyleSheet(
            f"color: {THEME['confidence_high']}; padding: 4px;")
        self._status_label.setVisible(True)

    def show_error(self, message: str):
        self._status_label.setText(tr("error_prefix", message=message))
        self._status_label.setStyleSheet(
            f"color: {THEME['confidence_low']}; padding: 4px;")
        self._status_label.setVisible(True)

    def clear_status(self):
        self._status_label.setVisible(False)
        self._progress.setVisible(False)
