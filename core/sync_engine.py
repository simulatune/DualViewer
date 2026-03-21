"""
音频互相关同步引擎 / Audio cross-correlation sync engine.

通过 FFT 互相关算法计算两段音频的时间偏移，用于自动对齐双视频。
"""

import tempfile
from dataclasses import dataclass, field

import numpy as np
from scipy.io import wavfile
from PySide6.QtCore import QThread, Signal

from core.ffmpeg_utils import extract_audio


@dataclass
class SyncResult:
    """同步结果数据类"""
    offset_seconds: float   # 正值 = B 比 A 晚开始 / positive = B starts later than A
    offset_frames: int      # 帧为单位的偏移量
    method: str             # 同步方法标识
    confidence: float       # 置信度 0.0–1.0（基于 SNR）
    sample_rate: int = 16000
    verifications: dict[str, float] = field(default_factory=dict)


class SyncEngine:
    """音频互相关同步引擎，使用 FFT 加速互相关计算"""

    def __init__(self, sample_rate: int = 16000, max_duration: float = 30.0):
        self.sample_rate = sample_rate      # 音频重采样率（Hz）
        self.max_duration = max_duration    # 最大分析时长（秒），限制内存使用

    def auto_sync(self, video_a: str, video_b: str, fps: float = 30.0) -> SyncResult:
        """自动同步：提取音频 → FFT 互相关 → 返回偏移量和置信度"""
        # 创建临时 WAV 文件
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f_a:
            wav_a = f_a.name
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f_b:
            wav_b = f_b.name

        # 从视频中提取音频，统一采样率
        extract_audio(video_a, wav_a, self.sample_rate)
        extract_audio(video_b, wav_b, self.sample_rate)

        # 计算互相关偏移
        offset, confidence = self._compute_offset_xcorr(wav_a, wav_b)
        return SyncResult(
            offset_seconds=offset,
            offset_frames=round(offset * fps),
            method="audio_xcorr",
            confidence=confidence,
            sample_rate=self.sample_rate,
        )

    def _compute_offset_xcorr(self, wav_a: str, wav_b: str) -> tuple[float, float]:
        """核心算法：FFT 互相关计算时间偏移"""
        # 读取 WAV 文件
        sr_a, data_a = wavfile.read(wav_a)
        sr_b, data_b = wavfile.read(wav_b)
        assert sr_a == sr_b, f"Sample rate mismatch: {sr_a} vs {sr_b}"
        sr = sr_a

        # 归一化到 [-1.0, 1.0] 范围
        a = data_a.astype(np.float64) / 32768.0
        b = data_b.astype(np.float64) / 32768.0

        # 截断到最大分析时长，避免内存溢出
        max_samples = int(sr * self.max_duration)
        a = a[:max_samples]
        b = b[:max_samples]

        # FFT 互相关：利用频域乘法加速时域卷积
        n = len(a) + len(b) - 1
        fft_size = 2 ** int(np.ceil(np.log2(n)))  # 补零到 2 的幂次，提升 FFT 效率
        fft_a = np.fft.rfft(a, fft_size)
        fft_b = np.fft.rfft(b, fft_size)
        xcorr = np.fft.irfft(fft_a * np.conj(fft_b), fft_size)  # 互相关 = IFFT(A · conj(B))

        # 找到互相关峰值位置
        peak_index = int(np.argmax(np.abs(xcorr)))
        confidence = self._compute_confidence(xcorr, peak_index)

        # 将峰值索引转换为实际偏移量（处理环绕）
        if peak_index > fft_size // 2:
            offset_samples = peak_index - fft_size  # 负偏移：A 比 B 晚
        else:
            offset_samples = peak_index              # 正偏移：B 比 A 晚

        return offset_samples / sr, confidence

    @staticmethod
    def _compute_confidence(xcorr: np.ndarray, peak_index: int) -> float:
        """
        基于信噪比（SNR）的置信度计算。
        峰值 / 噪声标准差，归一化到 [0, 1]（SNR >= 20 时为 1.0）。
        """
        peak_value = np.abs(xcorr[peak_index])
        # 排除峰值附近 ±100 个样本，剩余部分作为噪声基底
        mask = np.ones(len(xcorr), dtype=bool)
        start = max(0, peak_index - 100)
        end = min(len(xcorr), peak_index + 100)
        mask[start:end] = False
        noise_std = np.std(np.abs(xcorr[mask]))
        return min(1.0, peak_value / (noise_std + 1e-10) / 20.0)


class SyncThread(QThread):
    """后台同步线程，避免阻塞 UI"""

    finished = Signal(object)  # 同步完成，携带 SyncResult
    error = Signal(str)        # 同步出错，携带错误信息

    def __init__(self, video_a: str, video_b: str, fps: float,
                 sample_rate: int = 16000, parent=None):
        super().__init__(parent)
        self.video_a = video_a
        self.video_b = video_b
        self.fps = fps
        self.sample_rate = sample_rate

    def run(self):
        try:
            engine = SyncEngine(sample_rate=self.sample_rate)
            result = engine.auto_sync(self.video_a, self.video_b, self.fps)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
