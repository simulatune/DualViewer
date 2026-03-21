"""Resolve resource paths for both dev and PyInstaller-bundled modes."""

import os
import sys


def resource_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "resources")
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources")


def resource_path(filename: str) -> str | None:
    path = os.path.join(resource_dir(), filename)
    return path if os.path.isfile(path) else None
