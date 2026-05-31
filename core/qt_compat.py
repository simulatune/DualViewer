"""Qt runtime compatibility helpers."""

from __future__ import annotations

import os
import sys
from collections.abc import MutableMapping


_TRUTHY = {"1", "true", "yes", "on"}
_NATIVE_WAYLAND_ENV = "DUALVIEWER_NATIVE_WAYLAND"
_ENABLE_HW_VIDEO_ENV = "DUALVIEWER_ENABLE_HW_VIDEO"


def configure_qt_environment(
    env: MutableMapping[str, str] | None = None,
    platform: str | None = None,
) -> list[str]:
    """
    Apply environment fixes that must be in place before Qt is imported.

    Returns symbolic action names for tests and diagnostics.
    """
    env = os.environ if env is None else env
    platform = sys.platform if platform is None else platform
    actions: list[str] = []

    if not platform.startswith("linux"):
        return actions

    if not any(env.get(var) for var in ("LC_ALL", "LC_CTYPE", "LANG")):
        env["LC_ALL"] = "C.UTF-8"
        actions.append("locale")

    if not env.get("QT_MEDIA_BACKEND"):
        env["QT_MEDIA_BACKEND"] = "ffmpeg"
        actions.append("media_backend_ffmpeg")

    if _is_wayland_session(env):
        if not _env_truthy(env, _NATIVE_WAYLAND_ENV):
            _prefer_xwayland(env, actions)
        if not _env_truthy(env, _ENABLE_HW_VIDEO_ENV):
            _prefer_software_video(env, actions)

    return actions


def _is_wayland_session(env: MutableMapping[str, str]) -> bool:
    return bool(env.get("WAYLAND_DISPLAY")) or env.get(
        "XDG_SESSION_TYPE", ""
    ).lower() == "wayland"


def _prefer_xwayland(env: MutableMapping[str, str], actions: list[str]) -> None:
    if env.get("QT_QPA_PLATFORM"):
        return

    # Ubuntu Wayland sessions normally expose DISPLAY through XWayland. Using
    # xcb avoids QVideoWidget repaint/corruption glitches on native Wayland.
    env["QT_QPA_PLATFORM"] = "xcb" if env.get("DISPLAY") else "xcb;wayland"
    actions.append("prefer_xwayland")


def _prefer_software_video(env: MutableMapping[str, str], actions: list[str]) -> None:
    if not env.get("QT_DISABLE_HW_TEXTURES_CONVERSION"):
        env["QT_DISABLE_HW_TEXTURES_CONVERSION"] = "1"
        actions.append("disable_hw_texture_conversion")

    if "QT_FFMPEG_DECODING_HW_DEVICE_TYPES" not in env:
        env["QT_FFMPEG_DECODING_HW_DEVICE_TYPES"] = ","
        actions.append("disable_hw_decoding")


def _env_truthy(env: MutableMapping[str, str], name: str) -> bool:
    return env.get(name, "").strip().lower() in _TRUTHY
