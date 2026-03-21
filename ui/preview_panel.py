"""
预览面板 / Preview panel — dual side-by-side video display with per-video frame stepping.

负责双视频并排显示，支持独立逐帧步进。
"""

from PySide6.QtCore import QSize, Qt, QTimer, QUrl, Signal
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.i18n import tr
from ui.icons import icon_step_left, icon_step_right


class PreviewPanel(QWidget):

    step_single = Signal(str, int)  # ("a"|"b", 方向 ±1)

    def __init__(self, fps: float = 30.0, parent=None):
        super().__init__(parent)
        self._fps = fps

        # 创建双播放器实例，视频 B 静音（避免双音轨）
        self.player_a = QMediaPlayer()
        self.player_b = QMediaPlayer()
        self.audio_a = QAudioOutput()
        self.audio_b = QAudioOutput()
        self.player_a.setAudioOutput(self.audio_a)
        self.player_b.setAudioOutput(self.audio_b)
        self.audio_b.setVolume(0.0)  # 视频 B 静音

        # 视频渲染控件
        self.widget_a = QVideoWidget()
        self.widget_b = QVideoWidget()
        self.player_a.setVideoOutput(self.widget_a)
        self.player_b.setVideoOutput(self.widget_b)

        # 首帧显示跟踪标志
        # 加载视频后需要播放一帧再暂停，否则画面为黑屏
        self._need_first_frame_a = False
        self._need_first_frame_b = False
        self._first_frame_connected_a = False
        self._first_frame_connected_b = False
        self.player_a.mediaStatusChanged.connect(self._on_status_a)
        self.player_b.mediaStatusChanged.connect(self._on_status_b)

        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        for which, widget, label_text in [
            ("a", self.widget_a, tr("video_a")),
            ("b", self.widget_b, tr("video_b")),
        ]:
            col = QVBoxLayout()
            info = QLabel(label_text)
            col.addWidget(info)
            col.addWidget(widget, 1)
            col.addLayout(self._make_frame_controls(which))
            layout.addLayout(col, 1)
            if which == "a":
                self._info_a = info
            else:
                self._info_b = info

    def _make_frame_controls(self, which: str) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 2, 0, 2)
        row.setSpacing(4)
        row.addStretch()

        btn_prev = QPushButton()
        btn_prev.setObjectName("frameBtn")
        btn_prev.setFixedSize(28, 28)
        btn_prev.setIcon(icon_step_left())
        btn_prev.setIconSize(QSize(28, 28))
        btn_prev.setToolTip(tr("step_back", which=which.upper()))
        btn_prev.clicked.connect(lambda: self.step_single.emit(which, -1))
        row.addWidget(btn_prev, 0, Qt.AlignVCenter)

        pos_label = QLabel(tr("frame_n", n=0))
        pos_label.setObjectName("mono")
        pos_label.setAlignment(Qt.AlignCenter)
        pos_label.setFixedSize(80, 28)
        row.addWidget(pos_label, 0, Qt.AlignVCenter)

        btn_next = QPushButton()
        btn_next.setObjectName("frameBtn")
        btn_next.setFixedSize(28, 28)
        btn_next.setIcon(icon_step_right())
        btn_next.setIconSize(QSize(28, 28))
        btn_next.setToolTip(tr("step_forward", which=which.upper()))
        btn_next.clicked.connect(lambda: self.step_single.emit(which, 1))
        row.addWidget(btn_next, 0, Qt.AlignVCenter)

        row.addStretch()

        if which == "a":
            self._pos_label_a = pos_label
            self._btn_prev_a = btn_prev
            self._btn_next_a = btn_next
        else:
            self._pos_label_b = pos_label
            self._btn_prev_b = btn_prev
            self._btn_next_b = btn_next
        return row

    def retranslate(self):
        self._btn_prev_a.setToolTip(tr("step_back", which="A"))
        self._btn_next_a.setToolTip(tr("step_forward", which="A"))
        self._btn_prev_b.setToolTip(tr("step_back", which="B"))
        self._btn_next_b.setToolTip(tr("step_forward", which="B"))
        self.update_position_labels()

    # -- 视频加载 / Video loading --

    def load_videos(self, path_a: str, path_b: str):
        """加载两个视频文件，并触发首帧显示"""
        self._cleanup_first_frame_connections()
        self._need_first_frame_a = True
        self._need_first_frame_b = True
        self.player_a.setSource(QUrl.fromLocalFile(path_a))
        self.player_b.setSource(QUrl.fromLocalFile(path_b))
        self._info_a.setText(f"{tr('video_a')}: {path_a.split('/')[-1]}")
        self._info_b.setText(f"{tr('video_b')}: {path_b.split('/')[-1]}")

    def _cleanup_first_frame_connections(self):
        """断开之前的首帧监听信号，避免重复连接"""
        if self._first_frame_connected_a:
            self._first_frame_connected_a = False
            self.player_a.positionChanged.disconnect(self._check_first_frame_a)
        if self._first_frame_connected_b:
            self._first_frame_connected_b = False
            self.player_b.positionChanged.disconnect(self._check_first_frame_b)

    # -- 首帧显示：播放直到 position > 0，然后异步暂停 --
    # GStreamer 后端在 pause 状态下不解码画面，所以需要先 play() 再延迟 pause()

    def _on_status_a(self, status):
        """视频 A 媒体加载完成后，启动首帧显示流程"""
        if self._need_first_frame_a and status == QMediaPlayer.MediaStatus.LoadedMedia:
            self._need_first_frame_a = False
            if not self._first_frame_connected_a:
                self._first_frame_connected_a = True
                self.player_a.positionChanged.connect(self._check_first_frame_a)
            self.player_a.play()

    def _check_first_frame_a(self, position):
        """检测到视频 A 已解码首帧（position > 0），异步暂停"""
        if self._first_frame_connected_a and position > 0:
            self._first_frame_connected_a = False
            self.player_a.positionChanged.disconnect(self._check_first_frame_a)
            QTimer.singleShot(30, self.player_a.pause)  # 延迟 30ms 暂停，避免 GStreamer 死锁

    def _on_status_b(self, status):
        """视频 B 媒体加载完成后，启动首帧显示流程"""
        if self._need_first_frame_b and status == QMediaPlayer.MediaStatus.LoadedMedia:
            self._need_first_frame_b = False
            if not self._first_frame_connected_b:
                self._first_frame_connected_b = True
                self.player_b.positionChanged.connect(self._check_first_frame_b)
            self.player_b.play()

    def _check_first_frame_b(self, position):
        """检测到视频 B 已解码首帧，异步暂停（延迟 60ms，错开 A 的暂停时机）"""
        if self._first_frame_connected_b and position > 0:
            self._first_frame_connected_b = False
            self.player_b.positionChanged.disconnect(self._check_first_frame_b)
            QTimer.singleShot(60, self.player_b.pause)  # 与 A 错开，避免同时暂停导致的竞态

    # -- 公共接口 / Public API --

    def set_info(self, info_a: str, info_b: str):
        self._info_a.setText(info_a)
        self._info_b.setText(info_b)

    def set_fps(self, fps: float):
        self._fps = fps

    def update_position_labels(self):
        """更新两个视频的当前帧号显示"""
        self._pos_label_a.setText(tr("frame_n", n=self._ms_to_frame(self.player_a.position())))
        self._pos_label_b.setText(tr("frame_n", n=self._ms_to_frame(self.player_b.position())))

    def _ms_to_frame(self, ms: int) -> int:
        """毫秒转帧号"""
        return round(ms / 1000 * self._fps) if self._fps > 0 else 0

    def mousePressEvent(self, event):
        """点击预览区域时将焦点返回主窗口（确保快捷键可用）"""
        self.window().setFocus()
        super().mousePressEvent(event)

    def seek_paused(self, player: QMediaPlayer, position_ms: int):
        """
        暂停状态下跳转：先设置位置，再短暂播放以强制后端解码渲染画面。
        GStreamer 在 pause 状态下 setPosition 不会立即更新画面，
        所以需要 play() + 延迟 pause() 来刷新显示。
        """
        player.setPosition(max(0, position_ms))
        if player.playbackState() != QMediaPlayer.PlayingState:
            player.play()
            QTimer.singleShot(30, player.pause)
