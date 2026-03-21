"""Internationalization — English, Chinese, Japanese translations."""

from PySide6.QtCore import QObject, Signal

_TRANSLATIONS = {
    "en": {
        # Main window
        "window_title": "DualViewer",
        "load_error": "Load Error",
        "credit": "v{version}  ·  Developed by Calibur",

        # Import panel
        "video_a": "Video A",
        "video_b": "Video B",
        "not_selected": "Not selected",
        "select_video_a": "Select Video A",
        "select_video_b": "Select Video B",
        "video_filter": "Video (*.mp4 *.mkv *.avi *.mov)",

        # Preview panel
        "frame_n": "Frame {n}",
        "step_back": "Video {which} step back",
        "step_forward": "Video {which} step forward",

        # Sync control
        "method": "Method:",
        "auto_audio": "Auto (Audio)",
        "manual": "Manual",
        "confidence": "Confidence:",
        "confidence_default": "—",
        "offset": "Offset:",
        "suffix_frame": " fr",
        "auto_sync": "Auto Sync",
        "reset": "Reset",
        "syncing": "Syncing...",
        "analyzing": "Analyzing...",
        "confidence_high": "High",
        "confidence_mid": "Medium",
        "confidence_low": "Low",
        "sync_low_confidence": "Confidence {level} — manual calibration recommended",
        "sync_result": "Offset {offset}s, confidence {level}",
        "sync_failed": "Failed: {message}",

        # Export panel
        "export": "Export",
        "in_point": "In I",
        "out_point": "Out O",
        "suffix_seconds": " s",
        "duration_label": "Duration: {value:.3f}s",
        "preview": "Preview",
        "label_a": "Label A:",
        "label_b": "Label B:",
        "default_wm_a": "Phone A",
        "default_wm_b": "Phone B",
        "width": "Width:",
        "crf": "CRF:",
        "crf_tooltip": (
            "Quality (Constant Rate Factor)\n"
            "0 = lossless (largest file)\n"
            "18 = visually lossless (recommended)\n"
            "23 = FFmpeg default\n"
            "51 = lowest quality (smallest file)\n"
            "Lower = better quality, +6 halves bitrate"
        ),
        "export_video": "Export Video",
        "exporting": "Exporting...",
        "in_before_out": "In point must be before out point",
        "save_dialog_title": "Export Video",
        "save_dialog_filter": "Video (*.mp4)",
        "exported": "Exported: {path}",
        "error_prefix": "Error: {message}",

        # Playback
        "time_format": "{pos} / {dur}",
    },

    "zh": {
        "window_title": "DualViewer",
        "load_error": "加载错误",
        "credit": "v{version}  ·  由 Calibur 开发",

        "video_a": "视频 A",
        "video_b": "视频 B",
        "not_selected": "未选择",
        "select_video_a": "选择视频 A",
        "select_video_b": "选择视频 B",
        "video_filter": "视频 (*.mp4 *.mkv *.avi *.mov)",

        "frame_n": "帧 {n}",
        "step_back": "视频 {which} 后退一帧",
        "step_forward": "视频 {which} 前进一帧",

        "method": "方法：",
        "auto_audio": "自动（音频）",
        "manual": "手动",
        "confidence": "置信度：",
        "confidence_default": "—",
        "offset": "偏移：",
        "suffix_frame": " 帧",
        "auto_sync": "自动同步",
        "reset": "重置",
        "syncing": "同步中…",
        "analyzing": "分析中…",
        "confidence_high": "高",
        "confidence_mid": "中",
        "confidence_low": "低",
        "sync_low_confidence": "置信度{level} — 建议手动校准",
        "sync_result": "偏移 {offset}s，置信度{level}",
        "sync_failed": "失败：{message}",

        "export": "导出",
        "in_point": "入点 I",
        "out_point": "出点 O",
        "suffix_seconds": " 秒",
        "duration_label": "时长：{value:.3f}秒",
        "preview": "预览",
        "label_a": "标签 A：",
        "label_b": "标签 B：",
        "default_wm_a": "手机 A",
        "default_wm_b": "手机 B",
        "width": "宽度：",
        "crf": "CRF：",
        "crf_tooltip": (
            "质量（固定码率因子）\n"
            "0 = 无损（文件最大）\n"
            "18 = 视觉无损（推荐）\n"
            "23 = FFmpeg 默认\n"
            "51 = 最低质量（文件最小）\n"
            "数值越低质量越好，+6 码率减半"
        ),
        "export_video": "导出视频",
        "exporting": "导出中…",
        "in_before_out": "入点必须在出点之前",
        "save_dialog_title": "导出视频",
        "save_dialog_filter": "视频 (*.mp4)",
        "exported": "已导出：{path}",
        "error_prefix": "错误：{message}",

        "time_format": "{pos} / {dur}",
    },

    "ja": {
        "window_title": "DualViewer",
        "load_error": "読み込みエラー",
        "credit": "v{version}  ·  Developed by Calibur",

        "video_a": "ビデオ A",
        "video_b": "ビデオ B",
        "not_selected": "未選択",
        "select_video_a": "ビデオ A を選択",
        "select_video_b": "ビデオ B を選択",
        "video_filter": "動画 (*.mp4 *.mkv *.avi *.mov)",

        "frame_n": "フレーム {n}",
        "step_back": "ビデオ {which} 1フレーム戻る",
        "step_forward": "ビデオ {which} 1フレーム進む",

        "method": "方式：",
        "auto_audio": "自動（音声）",
        "manual": "手動",
        "confidence": "信頼度：",
        "confidence_default": "—",
        "offset": "オフセット：",
        "suffix_frame": " fr",
        "auto_sync": "自動同期",
        "reset": "リセット",
        "syncing": "同期中…",
        "analyzing": "分析中…",
        "confidence_high": "高",
        "confidence_mid": "中",
        "confidence_low": "低",
        "sync_low_confidence": "信頼度{level} — 手動調整を推奨",
        "sync_result": "オフセット {offset}s、信頼度{level}",
        "sync_failed": "失敗：{message}",

        "export": "エクスポート",
        "in_point": "In I",
        "out_point": "Out O",
        "suffix_seconds": " 秒",
        "duration_label": "長さ：{value:.3f}秒",
        "preview": "プレビュー",
        "label_a": "ラベル A：",
        "label_b": "ラベル B：",
        "default_wm_a": "スマホ A",
        "default_wm_b": "スマホ B",
        "width": "幅：",
        "crf": "CRF：",
        "crf_tooltip": (
            "品質（固定レートファクター）\n"
            "0 = ロスレス（最大ファイル）\n"
            "18 = 視覚的ロスレス（推奨）\n"
            "23 = FFmpeg デフォルト\n"
            "51 = 最低品質（最小ファイル）\n"
            "値が低いほど高品質、+6でビットレート半減"
        ),
        "export_video": "ビデオをエクスポート",
        "exporting": "エクスポート中…",
        "in_before_out": "In ポイントは Out ポイントより前にしてください",
        "save_dialog_title": "ビデオをエクスポート",
        "save_dialog_filter": "動画 (*.mp4)",
        "exported": "エクスポート完了：{path}",
        "error_prefix": "エラー：{message}",

        "time_format": "{pos} / {dur}",
    },
}

LANGUAGES = [
    ("en", "English"),
    ("zh", "中文"),
    ("ja", "日本語"),
]


class I18n(QObject):
    """Singleton translation manager."""

    language_changed = Signal()

    _instance: "I18n | None" = None

    def __init__(self):
        super().__init__()
        self._lang = self._detect_system_language()

    @staticmethod
    def _detect_system_language() -> str:
        """Pick default language based on OS locale."""
        import locale
        try:
            lang_code = locale.getdefaultlocale()[0] or ""
        except Exception:
            lang_code = ""
        lang_code = lang_code.lower()
        if lang_code.startswith("zh"):
            return "zh"
        if lang_code.startswith("ja"):
            return "ja"
        return "en"

    @classmethod
    def instance(cls) -> "I18n":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def lang(self) -> str:
        return self._lang

    def set_language(self, lang: str):
        if lang == self._lang:
            return
        if lang not in _TRANSLATIONS:
            return
        self._lang = lang
        self.language_changed.emit()

    def tr(self, key: str, **kwargs) -> str:
        table = _TRANSLATIONS.get(self._lang, _TRANSLATIONS["en"])
        text = table.get(key)
        if text is None:
            text = _TRANSLATIONS["en"].get(key, key)
        if kwargs:
            text = text.format(**kwargs)
        return text


def tr(key: str, **kwargs) -> str:
    """Shortcut for I18n.instance().tr(key, **kwargs)."""
    return I18n.instance().tr(key, **kwargs)
