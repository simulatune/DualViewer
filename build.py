#!/usr/bin/env python3
"""
Build script for DualViewer.

Usage:
    python build.py              # Directory mode (recommended, fast startup)
    python build.py --onefile    # Single-file mode (convenient, slower startup)

Prerequisites:
    1. pip install -r requirements.txt
    2. resources/ directory must contain:
       - font.ttc   (Chinese font)
       - ffmpeg      (FFmpeg binary)
       - ffprobe     (FFprobe binary)

Cross-platform notes:
    PyInstaller can only build for the current platform.
    - Linux:   needs static Linux ffmpeg/ffprobe
    - Windows: needs ffmpeg.exe/ffprobe.exe
    - macOS:   needs macOS ffmpeg/ffprobe

    FFmpeg downloads:
      Linux:   https://johnvansickle.com/ffmpeg/
      Windows: https://www.gyan.dev/ffmpeg/builds/
      macOS:   https://evermeet.cx/ffmpeg/
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def check_resources():
    """Verify required resource files exist."""
    res_dir = Path(__file__).parent / "resources"
    required = ["font.ttc"]

    if sys.platform == "win32":
        required += ["ffmpeg.exe", "ffprobe.exe"]
    else:
        required += ["ffmpeg", "ffprobe"]

    missing = []
    for name in required:
        if not (res_dir / name).is_file():
            missing.append(str(res_dir / name))

    if missing:
        print("Missing required resource files:")
        for m in missing:
            print(f"  - {m}")
        print("\nSee build.py header comments for download links.")
        sys.exit(1)

    print(f"Resource check passed ({len(required)} files)")


def build(onefile: bool = False):
    """Run PyInstaller build."""
    project_dir = Path(__file__).parent
    spec_file = project_dir / "dualviewer.spec"

    for d in ["build", "dist"]:
        p = project_dir / d
        if p.exists():
            shutil.rmtree(p)
            print(f"Cleaned {d}/")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
    ]

    if onefile:
        cmd += [
            "--onefile",
            "--noconsole",
            "--name", "DualViewer",
            "--add-data", f"resources{os.pathsep}resources",
            "--hidden-import", "PySide6.QtMultimedia",
            "--hidden-import", "PySide6.QtMultimediaWidgets",
            "--exclude-module", "tkinter",
            "--exclude-module", "matplotlib",
            "--exclude-module", "IPython",
            "main.py",
        ]
    else:
        cmd.append(str(spec_file))

    mode = "single-file" if onefile else "directory"
    print(f"\nStarting build ({mode} mode)...")
    print(f"Command: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, cwd=str(project_dir))

    if result.returncode == 0:
        dist = project_dir / "dist"
        if onefile:
            out = dist / ("DualViewer.exe" if sys.platform == "win32" else "DualViewer")
        else:
            out = dist / "DualViewer"
        print(f"\nBuild successful!")
        print(f"Output: {out}")
        if not onefile:
            total = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
            print(f"Total size: {total / 1024 / 1024:.1f} MB")
    else:
        print("\nBuild failed!", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Build DualViewer")
    parser.add_argument(
        "--onefile", action="store_true",
        help="Build as single executable (convenient but slower startup)",
    )
    args = parser.parse_args()

    check_resources()
    build(onefile=args.onefile)


if __name__ == "__main__":
    main()
