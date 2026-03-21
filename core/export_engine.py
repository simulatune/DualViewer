"""
FFmpeg 导出引擎 / FFmpeg export engine with Pillow-based CJK watermarks.

负责将两个视频并排合并导出，支持自定义水印（含中日文等 CJK 字符）。
"""

import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont
from PySide6.QtCore import QThread, Signal

from core.ffmpeg_utils import find_ffmpeg
from core.resource_path import resource_path

# 系统字体候选列表（Linux），按优先级排列
_FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


@dataclass
class ExportConfig:
    """导出配置参数"""
    video_a: str            # 视频 A 路径
    video_b: str            # 视频 B 路径
    output: str             # 输出文件路径
    offset_seconds: float   # 时间偏移量（秒）
    start_time: float = 0.0     # 裁剪起始时间
    duration: float = 0.0       # 裁剪时长（0 = 不裁剪）
    watermark_a: str = "Phone A"  # 视频 A 水印文字
    watermark_b: str = "Phone B"  # 视频 B 水印文字
    output_width: int = 1920      # 输出总宽度（像素）
    crf: int = 18                 # 视频质量（CRF 值，越小越清晰）


def _find_font(size: int = 28) -> ImageFont.FreeTypeFont:
    """查找可用字体：优先使用打包内置字体，其次系统字体，最后回退到默认字体"""
    bundled = resource_path("font.ttc")
    if bundled:
        return ImageFont.truetype(bundled, size)
    for path in _FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def create_watermark_image(text: str, width: int, height: int,
                           font_size: int = 28, padding: int = 10) -> str:
    """
    使用 Pillow 渲染水印文字为透明 PNG 图片。
    返回临时文件路径，后续作为 FFmpeg overlay 输入。
    """
    # 创建透明画布
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = _find_font(font_size)

    # 计算文字尺寸
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # 绘制半透明黑色背景矩形 + 白色文字
    pad_x, pad_y = 8, 6
    draw.rectangle(
        [padding, padding,
         padding + text_w + pad_x * 2,
         padding + text_h + pad_y * 2],
        fill=(0, 0, 0, 128),  # 半透明黑色背景
    )
    draw.text(
        (padding + pad_x - bbox[0], padding + pad_y - bbox[1]),
        text, font=font, fill=(255, 255, 255, 255),  # 白色文字
    )

    # 保存为临时 PNG 文件
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    img.save(path, "PNG")
    return path


def build_export_command(config: ExportConfig) -> tuple[list[str], list[str]]:
    """
    构建 FFmpeg hstack 并排合并命令。
    返回 (命令列表, 需要清理的临时文件列表)。
    """
    from core.video_info import get_video_info

    # 获取两个视频的分辨率信息
    info_a = get_video_info(config.video_a)
    info_b = get_video_info(config.video_b)

    # 按宽高比分配输出宽度，保持等高
    aspect_a = info_a.width / info_a.height
    aspect_b = info_b.width / info_b.height
    total_aspect = aspect_a + aspect_b

    w_a = int(config.output_width * aspect_a / total_aspect)
    w_b = config.output_width - w_a
    out_h = int(w_a / aspect_a)

    # x264 编码器要求宽高为偶数
    w_a += w_a % 2
    w_b += w_b % 2
    out_h += out_h % 2

    # 根据偏移方向计算各视频的起始时间
    if config.offset_seconds >= 0:
        ss_a = config.start_time
        ss_b = config.start_time + config.offset_seconds
    else:
        ss_a = config.start_time + abs(config.offset_seconds)
        ss_b = config.start_time

    # 生成水印图片
    wm_a_path = create_watermark_image(config.watermark_a, w_a, out_h)
    wm_b_path = create_watermark_image(config.watermark_b, w_b, out_h)
    temp_files = [wm_a_path, wm_b_path]

    # FFmpeg 滤镜链：缩放 → 填充 → 叠加水印 → 左右拼接
    filter_complex = (
        f"[0:v]scale={w_a}:{out_h}:force_original_aspect_ratio=decrease,"
        f"pad={w_a}:{out_h}:(ow-iw)/2:(oh-ih)/2[va];"
        f"[1:v]scale={w_b}:{out_h}:force_original_aspect_ratio=decrease,"
        f"pad={w_b}:{out_h}:(ow-iw)/2:(oh-ih)/2[vb];"
        f"[va][2:v]overlay=0:0[left];"     # 叠加视频 A 水印
        f"[vb][3:v]overlay=0:0[right];"    # 叠加视频 B 水印
        f"[left][right]hstack=inputs=2[out]"  # 左右并排拼接
    )

    # 构建完整命令
    cmd = [
        find_ffmpeg(), "-y",
        "-ss", f"{ss_a:.3f}", "-i", config.video_a,
        "-ss", f"{ss_b:.3f}", "-i", config.video_b,
        "-i", wm_a_path, "-i", wm_b_path,
    ]
    if config.duration > 0:
        cmd += ["-t", f"{config.duration:.3f}"]
    cmd += [
        "-filter_complex", filter_complex,
        "-map", "[out]", "-map", "0:a",
        "-c:v", "libx264", "-crf", str(config.crf),
        "-preset", "medium", "-c:a", "aac", "-b:a", "128k",
        config.output,
    ]
    return cmd, temp_files


def cleanup_temp_files(paths: list[str]) -> None:
    """清理临时文件（水印图片等）"""
    for p in paths:
        try:
            os.remove(p)
        except OSError:
            pass


def parse_ffmpeg_progress(line: str, total_duration: float) -> float | None:
    """从 FFmpeg stderr 输出中解析编码进度，返回 0.0–1.0 的进度值"""
    match = re.search(r"time=(\d+):(\d+):(\d+\.\d+)", line)
    if match:
        h, m, s = match.groups()
        current = int(h) * 3600 + int(m) * 60 + float(s)
        return min(1.0, current / total_duration)
    return None


class ExportThread(QThread):
    """后台导出线程，避免阻塞 UI，实时报告进度"""

    progress = Signal(float)   # 导出进度 0.0–1.0
    finished = Signal(str)     # 导出完成，携带输出文件路径
    error = Signal(str)        # 导出出错，携带错误信息

    def __init__(self, cmd: list[str], duration: float,
                 temp_files: list[str], parent=None):
        super().__init__(parent)
        self.cmd = cmd
        self.duration = duration
        self.temp_files = temp_files

    def run(self):
        try:
            kwargs = dict(
                stderr=subprocess.PIPE, stdout=subprocess.DEVNULL,
                encoding="utf-8", errors="replace",
            )
            # Windows 下隐藏控制台窗口
            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
            process = subprocess.Popen(self.cmd, **kwargs)

            # 逐行读取 FFmpeg 输出，解析进度
            for line in process.stderr:
                p = parse_ffmpeg_progress(line, self.duration)
                if p is not None:
                    self.progress.emit(p)

            process.wait()
            if process.returncode == 0:
                self.finished.emit(self.cmd[-1])  # 输出文件路径
            else:
                self.error.emit(f"FFmpeg exit code {process.returncode}")
        except Exception as e:
            self.error.emit(str(e))
        finally:
            cleanup_temp_files(self.temp_files)  # 无论成败都清理临时文件
