"""FFmpeg / FFprobe subprocess wrappers."""

import os
import shutil
import subprocess
import sys

from core.resource_path import resource_path


def find_ffmpeg() -> str:
    bundled = resource_path("ffmpeg" + (".exe" if sys.platform == "win32" else ""))
    if bundled:
        os.chmod(bundled, 0o755)
        return bundled
    path = shutil.which("ffmpeg")
    if path:
        return path
    raise FileNotFoundError("ffmpeg not found. Install ffmpeg and ensure it is on PATH.")


def find_ffprobe() -> str:
    bundled = resource_path("ffprobe" + (".exe" if sys.platform == "win32" else ""))
    if bundled:
        os.chmod(bundled, 0o755)
        return bundled
    path = shutil.which("ffprobe")
    if path:
        return path
    raise FileNotFoundError("ffprobe not found. Install ffmpeg and ensure it is on PATH.")


def _subprocess_kwargs() -> dict:
    if sys.platform == "win32":
        return {"creationflags": subprocess.CREATE_NO_WINDOW}
    return {}


def run_ffmpeg(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    cmd = [find_ffmpeg()] + args
    return subprocess.run(
        cmd, check=check, capture_output=True, encoding="utf-8", errors="replace",
        **_subprocess_kwargs(),
    )


def run_ffprobe(args: list[str]) -> subprocess.CompletedProcess:
    cmd = [find_ffprobe()] + args
    return subprocess.run(
        cmd, check=True, capture_output=True, encoding="utf-8", errors="replace",
        **_subprocess_kwargs(),
    )


def extract_audio(video_path: str, output_wav: str, sample_rate: int = 16000) -> None:
    run_ffmpeg([
        "-y", "-i", video_path,
        "-vn", "-ac", "1", "-ar", str(sample_rate),
        "-sample_fmt", "s16", "-f", "wav",
        output_wav,
    ])
