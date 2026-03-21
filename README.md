# DualViewer

English | [中文](./README_ZH.md) | [日本語](./README_JA.md)

Side-by-side dual video comparison tool — **auto sync → preview → merged export**.

Supports **English / 中文 / 日本語** UI with automatic system language detection.

![DualViewer Interface](pics/example_1.png)

### Export Result

![Export Result](pics/example_2.png)

---

## Features

### Sync Alignment
- **Auto audio sync** — FFT cross-correlation computes time offset between two videos, with SNR confidence scoring
- **Manual fine-tuning** — Per-frame / ±10 frame offset adjustment, real-time preview while paused
- **Independent stepping** — Step each video independently for visual alignment

### Side-by-Side Preview
- Dual video equal-height playback with 500ms auto drift correction
- Real-time frame number display for each video
- Click-to-seek on timeline with smooth dragging

### Merged Export
- FFmpeg hstack merge (default width = sum of both source widths)
- Custom watermark text (Pillow rendering, CJK support)
- Custom trim range (In / Out points) with range preview
- Background thread export with progress bar
- CRF quality control (default 18, visually lossless)

### Multi-Language
- Supports **English**, **中文**, **日本語**
- Auto-detects system language, switchable at runtime

### Interface
- Dark theme optimized for video comparison
- Timeline visualization: overlap region, trim range, playhead
- Full keyboard shortcut coverage

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play / Pause |
| `←` `→` | Both videos ±1 frame |
| `[` `]` | Offset ±1 frame |
| `{` `}` | Offset ±10 frames |
| `I` | Set export in-point |
| `O` | Set export out-point |
| `Q` `E` | Video A ±1 frame |
| `A` `D` | Video B ±1 frame |

---

## Quick Start

### Run from Source

```bash
git clone https://github.com/simulatune/DualViewer.git
cd DualViewer

# Install dependencies
pip install -r requirements.txt

# Ensure ffmpeg is in PATH
# Ubuntu: sudo apt install ffmpeg
# Windows: https://www.gyan.dev/ffmpeg/builds/

# Launch
python main.py
```

### Download Pre-built

Go to [Releases](https://github.com/simulatune/DualViewer/releases) to download:

| Platform | File |
|----------|------|
| Linux x64 | `DualViewer` |
| Windows x64 | `DualViewer.exe` |

> Pre-built versions include FFmpeg and CJK fonts — no extra installation needed.

---

## Usage

1. **Import videos** — Click "Video A" and "Video B" to select two video files
2. **Sync alignment** — Click "Auto Sync" for automatic alignment, or switch to "Manual" and use `[` `]` to fine-tune
3. **Preview** — Space to play, arrow keys for frame-by-frame comparison
4. **Set range** — Press `I` for in-point, `O` for out-point, click "Preview" to confirm
5. **Export** — Enter watermark text, set quality, click "Export Video"
6. **Switch language** — Use the dropdown in the bottom-left corner

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| GUI | PySide6 (Qt6) |
| Video | FFmpeg / FFprobe (subprocess) |
| Audio Analysis | NumPy + SciPy (FFT cross-correlation) |
| Watermarks | Pillow |
| Packaging | PyInstaller |
| CI/CD | GitHub Actions (Linux + Windows) |

---

## Build

```bash
pip install -r requirements.txt

# Prepare FFmpeg (place in resources/)
# Linux:
curl -L -o ffmpeg.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar xf ffmpeg.tar.xz
cp ffmpeg-*-static/ffmpeg resources/ffmpeg
cp ffmpeg-*-static/ffprobe resources/ffprobe

# Windows:
# Download from https://www.gyan.dev/ffmpeg/builds/, place ffmpeg.exe / ffprobe.exe in resources/

# Build
python build.py

# Output: dist/DualViewer (or DualViewer.exe)
```

---

## License

MIT
