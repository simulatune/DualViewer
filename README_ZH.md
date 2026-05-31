# DualViewer

[English](./README.md) | 中文 | [日本語](./README_JA.md)

双视频并排对比工具 — **自动同步对齐 → 并排播放对比 → 合并导出**。

支持 **中文 / English / 日本語** 三语界面，自动根据系统语言选择默认语言。

![DualViewer 界面](pics/example_1.png)

### 导出效果

![导出效果](pics/example_2.png)

---

## 功能特性

### 同步对齐
- **音频自动同步** — FFT 互相关算法计算两个视频的时间偏移，SNR 置信度评分
- **手动微调** — 逐帧 / ±10 帧精细调整偏移量，暂停时实时刷新画面
- **独立逐帧** — 左右视频可分别独立步进，方便肉眼对齐

### 并排预览
- 双视频等高并排播放，500ms 间隔自动校正同步漂移
- 实时显示各视频当前帧号
- 点击时间轴直接跳转，支持流畅拖动

### 导出合并
- FFmpeg hstack 并排合并（默认宽度 = 两源视频宽度之和）
- 自定义水印文字（Pillow 渲染，支持中日文等 CJK 字符）
- 自定义裁剪范围（In / Out 点），可预览选段
- 后台线程导出 + 实时进度条
- CRF 画质控制（默认 18，视觉无损）

### 多语言
- 支持 **中文**、**English**、**日本語**
- 自动检测系统语言，运行时可实时切换

### 界面
- 深色主题，适合视频对比场景
- 时间轴可视化：重叠区域、裁剪区间、播放头
- 键盘快捷键覆盖全部核心操作

---

## 快捷键

| 按键 | 功能 |
|------|------|
| `Space` | 播放 / 暂停 |
| `←` `→` | 双视频同步 ±1 帧 |
| `[` `]` | 偏移量 ±1 帧 |
| `{` `}` | 偏移量 ±10 帧 |
| `I` | 设置导出起点 |
| `O` | 设置导出终点 |
| `Q` `E` | 视频 A 独立 ±1 帧 |
| `A` `D` | 视频 B 独立 ±1 帧 |

---

## 快速开始

### 从源码运行

```bash
git clone https://github.com/simulatune/DualViewer.git
cd DualViewer

# 安装依赖
pip install -r requirements.txt

# 确保 ffmpeg 在 PATH 中
# Ubuntu: sudo apt install ffmpeg
# Windows: https://www.gyan.dev/ffmpeg/builds/

# 启动
python main.py
```

> Linux/Wayland 下会在启动前优先使用 XWayland：检测到 `DISPLAY` 时设置 `QT_QPA_PLATFORM=xcb`（纯 Wayland 环境保留 `xcb;wayland` 兜底），并固定 `QT_MEDIA_BACKEND=ffmpeg`，默认关闭 Qt FFmpeg 硬件纹理转换/硬解码，以规避不同 Ubuntu / 显卡驱动上的花屏、黑屏、错位或刷新异常。需要测试原生 Wayland 时，可运行 `DUALVIEWER_NATIVE_WAYLAND=1 python main.py`；需要重新启用硬件视频路径时，可运行 `DUALVIEWER_ENABLE_HW_VIDEO=1 python main.py`；也可以用 `QT_QPA_PLATFORM=wayland python main.py` 手动覆盖。
>
> 如果预构建版本在 Ubuntu 上提示 `xcb` platform plugin 或依赖缺失，请先安装常见运行库：`sudo apt install xwayland libxcb-cursor0 libxkbcommon-x11-0`。

### 下载预构建版本

前往 [Releases](https://github.com/simulatune/DualViewer/releases) 下载对应平台的文件：

| 平台 | 文件 |
|------|------|
| Linux x64 | `DualViewer` |
| Windows x64 | `DualViewer.exe` |

> 预构建版本已内置 FFmpeg 和中文字体，无需额外安装。

---

## 使用流程

1. **导入视频** — 点击「视频 A」「视频 B」选择两个视频文件
2. **同步对齐** — 点击「自动同步」自动对齐，或切到「手动」用 `[` `]` 键微调
3. **预览对比** — 空格播放，方向键逐帧对比
4. **设置范围** — 按 `I` 设起点、`O` 设终点，点击「预览」确认
5. **导出视频** — 填写水印文字、设置画质，点击「导出视频」
6. **切换语言** — 左下角下拉菜单选择 English / 中文 / 日本語

---

## 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.11+ |
| GUI | PySide6 (Qt6) |
| 视频处理 | FFmpeg / FFprobe (subprocess) |
| 音频分析 | NumPy + SciPy (FFT 互相关) |
| 水印渲染 | Pillow |
| 打包 | PyInstaller |
| CI/CD | GitHub Actions (Linux + Windows) |

---

## 本地构建

```bash
# 安装依赖
pip install -r requirements.txt

# 准备 FFmpeg（放到 resources/ 目录）
# Linux:
curl -L -o ffmpeg.tar.xz https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar xf ffmpeg.tar.xz
cp ffmpeg-*-static/ffmpeg resources/ffmpeg
cp ffmpeg-*-static/ffprobe resources/ffprobe

# Windows:
# 从 https://www.gyan.dev/ffmpeg/builds/ 下载，将 ffmpeg.exe / ffprobe.exe 放入 resources/

# 构建
python build.py

# 产物: dist/DualViewer (或 DualViewer.exe)
```

---

## License

MIT
