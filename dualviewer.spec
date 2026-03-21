# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for DualViewer — single-file mode."""

import sys
from pathlib import Path

block_cipher = None
project_dir = Path(SPECPATH)

a = Analysis(
    [str(project_dir / "main.py")],
    pathex=[str(project_dir)],
    binaries=[],
    datas=[
        (str(project_dir / "resources"), "resources"),
    ],
    hiddenimports=[
        "PySide6.QtMultimedia",
        "PySide6.QtMultimediaWidgets",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "IPython",
        "notebook",
        "pytest",
        "PySide6.QtQml",
        "PySide6.QtQuick",
        "PySide6.QtQuickWidgets",
        "PySide6.QtPdf",
        "PySide6.QtWebEngine",
        "PySide6.QtWebEngineWidgets",
        "PySide6.Qt3DCore",
        "PySide6.Qt3DRender",
        "PySide6.Qt3DInput",
        "PySide6.QtBluetooth",
        "PySide6.QtNfc",
        "PySide6.QtPositioning",
        "PySide6.QtSensors",
        "PySide6.QtSerialPort",
        "PySide6.QtTest",
        "PySide6.QtDesigner",
        "PySide6.QtHelp",
        "PySide6.QtSvg",
        "PySide6.QtSvgWidgets",
        "PySide6.QtCharts",
        "PySide6.QtDataVisualization",
        "PySide6.QtOpenGL",
        "PySide6.QtOpenGLWidgets",
        "PySide6.QtRemoteObjects",
        "PySide6.QtScxml",
        "PySide6.QtSql",
        "PySide6.QtXml",
        # Only scipy.signal + scipy.io.wavfile are used
        "scipy.optimize",
        "scipy.interpolate",
        "scipy.integrate",
        "scipy.stats",
        "scipy.spatial",
        "scipy.cluster",
        "scipy.odr",
        "scipy.misc",
        "scipy.constants",
        "scipy.ndimage",
        "scipy.special",
    ],
    noarchive=False,
    optimize=0,
)

# Platform-specific Qt library cleanup
if sys.platform == "linux":
    qt_libs_to_remove = ["libQt6Pdf", "libQt6ShaderTools"]
    a.binaries = [
        b for b in a.binaries
        if not any(rm in b[0] for rm in qt_libs_to_remove)
    ]
elif sys.platform == "win32":
    qt_dlls_to_remove = ["Qt6Pdf", "Qt6ShaderTools"]
    a.binaries = [
        b for b in a.binaries
        if not any(rm in b[0] for rm in qt_dlls_to_remove)
    ]

# Remove Qt translation files (~7MB savings)
a.datas = [
    d for d in a.datas
    if "translations" not in d[0]
]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

app_name = "DualViewer"

# Set icon per platform
if sys.platform == "win32":
    app_icon = str(project_dir / "resources" / "icon.ico")
else:
    app_icon = str(project_dir / "resources" / "icon.png")

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=app_icon,
)
