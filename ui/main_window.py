"""主窗口 — 组装所有 UI 面板，管理播放/同步/导出逻辑。"""

import traceback

from PySide6.QtCore import QTimer, Qt
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QMainWindow, QMessageBox,
    QVBoxLayout, QWidget,
)

from core.export_engine import ExportConfig, ExportThread, build_export_command
from core.sync_engine import SyncThread
from core.video_info import get_video_info
from ui.export_panel import ExportPanel
from ui.i18n import I18n, LANGUAGES, tr
from ui.import_panel import ImportPanel
from ui.playback_control import PlaybackControl
from ui.preview_panel import PreviewPanel
from ui.sync_control import SyncControl
from ui.theme import THEME, get_stylesheet

__version__ = "1.0.0"


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("window_title"))
        self.setMinimumSize(1200, 700)
        self.setStyleSheet(get_stylesheet())

        self._video_a_path = ""
        self._video_b_path = ""
        self._offset_ms = 0          # 视频 B 相对于 A 的偏移量（毫秒）
        self._fps = 30.0
        self._duration_a = 0.0       # 视频 A 时长（秒）
        self._duration_b = 0.0       # 视频 B 时长（秒）
        self._overlap_start_s = 0.0  # 两视频重叠区域起点（秒）
        self._overlap_end_s = 0.0    # 两视频重叠区域终点（秒）
        self._export_thread: ExportThread | None = None
        self._sync_thread: SyncThread | None = None
        self._previewing_range = False  # 是否正在预览导出区间

        self._init_ui()
        self._connect_signals()

        # 同步校正定时器：播放时每 500ms 检查 A/B 是否漂移
        self._sync_timer = QTimer()
        self._sync_timer.setInterval(500)
        self._sync_timer.timeout.connect(self._correct_sync)

        # 位置更新定时器：每 50ms 刷新进度条和帧号
        self._pos_timer = QTimer()
        self._pos_timer.setInterval(50)
        self._pos_timer.timeout.connect(self._update_position)

        # 语言切换信号
        I18n.instance().language_changed.connect(self._retranslate)

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._import_panel = ImportPanel()       # 顶部：视频选择
        layout.addWidget(self._import_panel)

        self._preview = PreviewPanel()           # 中部：双视频并排预览
        layout.addWidget(self._preview, 1)

        self._playback = PlaybackControl()       # 播放控制 + 时间轴
        layout.addWidget(self._playback)

        self._sync_control = SyncControl()       # 同步控制条
        layout.addWidget(self._sync_control)

        self._export_panel = ExportPanel()       # 底部：导出面板
        layout.addWidget(self._export_panel)

        # 页脚：语言选择器（左） + 版本信息（右）
        footer = QHBoxLayout()
        footer.setContentsMargins(12, 0, 12, 4)

        self._lang_combo = QComboBox()
        self._lang_combo.setFixedWidth(90)
        for code, name in LANGUAGES:
            self._lang_combo.addItem(name, code)
        # 下拉框默认选中当前语言
        default_idx = self._lang_combo.findData(I18n.instance().lang)
        if default_idx >= 0:
            self._lang_combo.setCurrentIndex(default_idx)
        self._lang_combo.currentIndexChanged.connect(self._on_language_changed)
        footer.addWidget(self._lang_combo)

        footer.addStretch()

        self._credit_label = QLabel(tr("credit", version=__version__))
        self._credit_label.setStyleSheet(
            f"color: {THEME['text_muted']}; font-size: 10px; background: transparent;"
        )
        footer.addWidget(self._credit_label)
        layout.addLayout(footer)

    def _connect_signals(self):
        self._import_panel.videos_selected.connect(self._on_videos_selected)
        self._sync_control.sync_requested.connect(self._on_sync_requested)
        self._sync_control.offset_changed.connect(self._on_offset_changed)
        self._playback.play_pause.connect(self._toggle_play)
        self._playback.seek.connect(self._seek)
        self._playback.step_frame.connect(self._step_frame)
        self._preview.step_single.connect(self._step_single)
        self._export_panel.export_requested.connect(self._on_export_requested)
        self._export_panel.set_in_point.connect(self._set_in_point)
        self._export_panel.set_out_point.connect(self._set_out_point)
        self._export_panel.preview_range.connect(self._preview_range)
        self._export_panel._start_spin.valueChanged.connect(self._update_trim_on_timeline)
        self._export_panel._end_spin.valueChanged.connect(self._update_trim_on_timeline)
        self._preview.player_a.mediaStatusChanged.connect(self._on_media_end)
        self._preview.player_b.mediaStatusChanged.connect(self._on_media_end)

    # -- 语言切换 --

    def _on_language_changed(self, index: int):
        code = self._lang_combo.itemData(index)
        if code:
            I18n.instance().set_language(code)

    def _retranslate(self):
        """语言切换时更新所有面板的文本。"""
        self.setWindowTitle(tr("window_title"))
        self._credit_label.setText(tr("credit", version=__version__))
        self._import_panel.retranslate()
        self._preview.retranslate()
        self._sync_control.retranslate()
        self._export_panel.retranslate()

    # -- 辅助方法 --

    def _has_videos(self) -> bool:
        return bool(self._video_a_path and self._video_b_path)

    def _stop_playback(self):
        """停止播放，暂停两个播放器并停止定时器。"""
        if self._preview.player_a.playbackState() == QMediaPlayer.PlayingState:
            self._preview.player_a.pause()
        if self._preview.player_b.playbackState() == QMediaPlayer.PlayingState:
            self._preview.player_b.pause()
        self._sync_timer.stop()
        self._pos_timer.stop()
        self._playback.set_playing(False)
        self._previewing_range = False

    # -- 视频加载 --

    def _on_videos_selected(self, path_a: str, path_b: str):
        try:
            self._load_videos(path_a, path_b)
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, tr("load_error"), str(e))

    def _load_videos(self, path_a: str, path_b: str):
        self._stop_playback()
        self._video_a_path = path_a
        self._video_b_path = path_b

        info_a = get_video_info(path_a)
        info_b = get_video_info(path_b)
        self._fps = info_a.fps

        self._preview.load_videos(path_a, path_b)
        self._preview.set_info(
            f"A: {info_a.resolution_str} {info_a.fps_str}",
            f"B: {info_b.resolution_str} {info_b.fps_str}",
        )
        self._duration_a = info_a.duration
        self._duration_b = info_b.duration
        self._playback.set_duration(int(info_a.duration * 1000))
        self._sync_control.set_fps(self._fps)
        self._preview.set_fps(self._fps)
        self._export_panel.set_default_width(info_a.width + info_b.width)
        self._export_panel.clear_status()
        self._recalc_overlap(reset_trim=True)

    # -- 同步 --

    def _on_sync_requested(self):
        if not self._has_videos():
            return
        if self._sync_thread and self._sync_thread.isRunning():
            return
        if self._sync_control.get_method_index() == 1:  # 手动模式不触发自动同步
            return

        self._sync_control.set_syncing(True)
        self._sync_thread = SyncThread(
            self._video_a_path, self._video_b_path, self._fps, parent=self)
        self._sync_thread.finished.connect(self._on_sync_finished)
        self._sync_thread.error.connect(self._on_sync_error)
        self._sync_thread.start()

    def _on_sync_finished(self, result):
        self._sync_control.set_syncing(False)
        self._sync_control.set_result(
            result.offset_frames, result.offset_seconds,
            result.confidence, result.method,
        )
        self._offset_ms = int(result.offset_seconds * 1000)
        self._recalc_overlap(reset_trim=True)

    def _on_sync_error(self, message: str):
        self._sync_control.set_syncing(False)
        self._sync_control.show_error(message)

    def _on_offset_changed(self, frames: int):
        """手动调整偏移量时，更新偏移并刷新 B 的位置。"""
        self._offset_ms = int(frames / self._fps * 1000)
        if self._preview.player_a.playbackState() != QMediaPlayer.PlayingState:
            pos_a = self._preview.player_a.position()
            self._preview.seek_paused(self._preview.player_b, pos_a + self._offset_ms)
        self._preview.update_position_labels()
        self._recalc_overlap()

    # -- 播放控制 --

    def _toggle_play(self):
        if not self._has_videos():
            return
        if self._preview.player_a.playbackState() == QMediaPlayer.PlayingState:
            self._stop_playback()
        else:
            self._previewing_range = False
            # 播放前先同步 B 的位置
            self._preview.player_b.setPosition(
                self._preview.player_a.position() + self._offset_ms)
            self._preview.player_a.play()
            self._preview.player_b.play()
            self._sync_timer.start()
            self._pos_timer.start()
            self._playback.set_playing(True)

    def _on_media_end(self, status):
        """两个视频都播放到末尾时自动停止。"""
        if status != QMediaPlayer.MediaStatus.EndOfMedia:
            return
        if not self._pos_timer.isActive():
            return
        a_end = self._preview.player_a.mediaStatus() == QMediaPlayer.MediaStatus.EndOfMedia
        b_end = self._preview.player_b.mediaStatus() == QMediaPlayer.MediaStatus.EndOfMedia
        if a_end and b_end:
            self._stop_playback()

    def _seek(self, pos_ms: int):
        if not self._has_videos():
            return
        pos_ms = max(0, pos_ms)
        # 用定时器状态判断是否正在播放，避免 GStreamer 的 playbackState 竞态
        if self._pos_timer.isActive():
            self._preview.player_a.setPosition(pos_ms)
            self._preview.player_b.setPosition(pos_ms + self._offset_ms)
        else:
            self._preview.seek_paused(self._preview.player_a, pos_ms)
            self._preview.seek_paused(self._preview.player_b, pos_ms + self._offset_ms)
        self._playback.update_position(pos_ms)
        self._preview.update_position_labels()

    def _step_frame(self, direction: int):
        """双视频同步步进 ±1 帧。"""
        if not self._has_videos():
            return
        frame_ms = int(1000 / self._fps)
        self._seek(max(0, self._preview.player_a.position() + direction * frame_ms))

    def _step_single(self, which: str, direction: int):
        """单独步进某一路视频，同时调整偏移量。"""
        frame_ms = int(1000 / self._fps)
        player = self._preview.player_a if which == "a" else self._preview.player_b
        new_pos = max(0, player.position() + direction * frame_ms)

        if player.playbackState() != QMediaPlayer.PlayingState:
            self._preview.seek_paused(player, new_pos)
        else:
            player.setPosition(new_pos)
        self._preview.update_position_labels()

        # 同步更新偏移量
        delta = direction if which == "b" else -direction
        self._sync_control._offset_spin.blockSignals(True)
        self._sync_control._offset_spin.setValue(
            self._sync_control._offset_spin.value() + delta)
        self._sync_control._offset_spin.blockSignals(False)
        self._sync_control._update_offset_sec_label()
        self._offset_ms = int(
            self._sync_control._offset_spin.value() / self._fps * 1000)
        self._recalc_overlap()

    def _correct_sync(self):
        """播放中定期校正 A/B 同步漂移（>50ms 时重新对齐）。"""
        end = QMediaPlayer.MediaStatus.EndOfMedia
        if (self._preview.player_a.mediaStatus() == end
                or self._preview.player_b.mediaStatus() == end):
            return
        pos_a = self._preview.player_a.position()
        expected_b = pos_a + self._offset_ms
        if abs(self._preview.player_b.position() - expected_b) > 50:
            self._preview.player_b.setPosition(expected_b)

    def _update_position(self):
        """定时刷新进度条位置和帧号显示。"""
        if self._playback.is_dragging():
            return
        pos = self._preview.player_a.position()
        self._playback.update_position(pos)
        self._preview.update_position_labels()

        # 预览区间模式下，到达终点自动停止
        if self._previewing_range:
            end_ms = int(self._export_panel.get_end() * 1000)
            if end_ms > 0 and pos >= end_ms:
                self._previewing_range = False
                if self._preview.player_a.playbackState() == QMediaPlayer.PlayingState:
                    self._toggle_play()

    # -- 重叠区域 / 裁剪范围 --

    def _recalc_overlap(self, reset_trim: bool = False):
        """根据偏移量重新计算两视频的重叠区域，并更新时间轴显示。"""
        if self._duration_a <= 0:
            return
        offset_s = self._offset_ms / 1000.0
        self._overlap_start_s = max(0.0, -offset_s)
        self._overlap_end_s = min(self._duration_a, self._duration_b - offset_s)
        self._overlap_end_s = max(self._overlap_start_s, self._overlap_end_s)

        self._export_panel.set_range_limits(
            self._overlap_start_s, self._overlap_end_s, reset=reset_trim)

        dur_a = self._duration_a
        self._playback.timeline.set_overlap(
            self._overlap_start_s / dur_a, self._overlap_end_s / dur_a)
        self._update_trim_on_timeline()

    def _update_trim_on_timeline(self):
        if self._duration_a <= 0:
            return
        self._playback.timeline.set_trim(
            self._export_panel.get_start() / self._duration_a,
            self._export_panel.get_end() / self._duration_a,
        )

    def _set_in_point(self):
        pos_s = self._preview.player_a.position() / 1000.0
        self._export_panel.set_in(
            max(self._overlap_start_s, min(self._overlap_end_s, pos_s)))

    def _set_out_point(self):
        pos_s = self._preview.player_a.position() / 1000.0
        self._export_panel.set_out(
            max(self._overlap_start_s, min(self._overlap_end_s, pos_s)))

    def _preview_range(self):
        """从 In 点开始播放到 Out 点，预览导出区间。"""
        if not self._has_videos():
            return
        self._previewing_range = True
        start_ms = int(self._export_panel.get_start() * 1000)
        self._preview.player_a.setPosition(start_ms)
        self._preview.player_b.setPosition(start_ms + self._offset_ms)
        self._playback.update_position(start_ms)
        self._preview.player_a.play()
        self._preview.player_b.play()
        self._sync_timer.start()
        self._pos_timer.start()
        self._playback.set_playing(True)

    # -- 导出 --

    def _on_export_requested(self, params: dict):
        if not self._has_videos():
            return
        if self._export_thread and self._export_thread.isRunning():
            return

        config = ExportConfig(
            video_a=self._video_a_path,
            video_b=self._video_b_path,
            output=params["output"],
            offset_seconds=self._offset_ms / 1000.0,
            start_time=params.get("start_time", 0),
            duration=params.get("duration", 0),
            watermark_a=params["watermark_a"],
            watermark_b=params["watermark_b"],
            output_width=params["width"],
            crf=params["crf"],
        )
        cmd, temp_files = build_export_command(config)
        duration = params.get("duration", 0) or self._duration_a

        self._export_thread = ExportThread(cmd, duration, temp_files, self)
        self._export_thread.progress.connect(self._export_panel.set_progress)
        self._export_thread.finished.connect(self._on_export_finished)
        self._export_thread.error.connect(self._on_export_error)
        self._export_panel.set_exporting(True)
        self._export_thread.start()

    def _on_export_finished(self, output_path: str):
        self._export_panel.set_exporting(False)
        self._export_panel.show_success(output_path)

    def _on_export_error(self, message: str):
        self._export_panel.set_exporting(False)
        self._export_panel.show_error(message)

    # -- 快捷键 --

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Space:
            self._toggle_play()             # 空格：播放/暂停
        elif key == Qt.Key_Left:
            self._step_frame(-1)            # ←：后退 1 帧
        elif key == Qt.Key_Right:
            self._step_frame(1)             # →：前进 1 帧
        elif key == Qt.Key_BracketLeft:
            self._adjust_offset(-1)         # [：偏移 -1 帧
        elif key == Qt.Key_BracketRight:
            self._adjust_offset(1)          # ]：偏移 +1 帧
        elif key == Qt.Key_BraceLeft:
            self._adjust_offset(-10)        # {：偏移 -10 帧
        elif key == Qt.Key_BraceRight:
            self._adjust_offset(10)         # }：偏移 +10 帧
        elif key == Qt.Key_I:
            self._set_in_point()            # I：设置导出起点
        elif key == Qt.Key_O:
            self._set_out_point()           # O：设置导出终点
        elif key == Qt.Key_Q:
            self._step_single("a", -1)      # Q：视频 A 后退 1 帧
        elif key == Qt.Key_E:
            self._step_single("a", 1)       # E：视频 A 前进 1 帧
        elif key == Qt.Key_A:
            self._step_single("b", -1)      # A：视频 B 后退 1 帧
        elif key == Qt.Key_D:
            self._step_single("b", 1)       # D：视频 B 前进 1 帧
        else:
            super().keyPressEvent(event)

    def _adjust_offset(self, delta: int):
        self._sync_control._offset_spin.setValue(
            self._sync_control._offset_spin.value() + delta)
