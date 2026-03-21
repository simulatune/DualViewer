"""DualViewer — 应用入口 / Entry point."""

import faulthandler
import os
import sys

# Windows 以 console=False 打包后 sys.stderr 为 None，需要守护
if sys.stderr is not None:
    faulthandler.enable()

# Linux 下如果没有设置 locale，可能导致中文标题乱码
if sys.platform == "linux":
    for var in ("LC_ALL", "LC_CTYPE", "LANG"):
        if os.environ.get(var):
            break
    else:
        os.environ["LC_ALL"] = "C.UTF-8"

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from core.resource_path import resource_path
from ui.main_window import MainWindow

__version__ = "1.0.0"


def main():
    app = QApplication(sys.argv)

    # 设置应用图标
    icon_path = resource_path("icon.png")
    if icon_path:
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
