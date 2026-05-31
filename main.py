"""DualViewer — 应用入口 / Entry point."""

import faulthandler
import sys

# Windows 以 console=False 打包后 sys.stderr 为 None，需要守护
if sys.stderr is not None:
    faulthandler.enable()

from core.qt_compat import configure_qt_environment

configure_qt_environment()

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
