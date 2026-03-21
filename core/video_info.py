"""FFprobe video metadata extraction."""

import json
from dataclasses import dataclass

from core.ffmpeg_utils import run_ffprobe


@dataclass
class VideoInfo:
    path: str
    width: int
    height: int
    fps: float
    duration: float
    codec: str
    audio_sample_rate: int
    audio_channels: int

    @property
    def resolution_str(self) -> str:
        return f"{self.width}x{self.height}"

    @property
    def fps_str(self) -> str:
        return f"{self.fps:.2f}FPS"


def get_video_info(video_path: str) -> VideoInfo:
    result = run_ffprobe([
        "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", video_path,
    ])

    data = json.loads(result.stdout)
    video_stream = None
    audio_stream = None

    for stream in data["streams"]:
        if stream["codec_type"] == "video" and video_stream is None:
            video_stream = stream
        elif stream["codec_type"] == "audio" and audio_stream is None:
            audio_stream = stream

    if video_stream is None:
        raise ValueError(f"No video stream found in {video_path}")

    fps_parts = video_stream["r_frame_rate"].split("/")
    fps = int(fps_parts[0]) / int(fps_parts[1])
    duration = float(data["format"]["duration"])
    audio_sr = int(audio_stream["sample_rate"]) if audio_stream else 0
    audio_ch = int(audio_stream["channels"]) if audio_stream else 0

    return VideoInfo(
        path=video_path,
        width=int(video_stream["width"]),
        height=int(video_stream["height"]),
        fps=fps,
        duration=duration,
        codec=video_stream["codec_name"],
        audio_sample_rate=audio_sr,
        audio_channels=audio_ch,
    )
