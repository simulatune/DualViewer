"""Dark theme stylesheet — zinc color palette."""

THEME = {
    "bg_darkest":      "#09090b",
    "bg_primary":      "#18181b",
    "bg_elevated":     "#202024",
    "bg_widget":       "#27272a",

    "accent":          "#3b82f6",
    "accent_hover":    "#2563eb",
    "accent_subtle":   "#1d4ed8",

    "source_a":        "#3b82f6",
    "source_b":        "#f59e0b",

    "text_primary":    "#d4d4d8",
    "text_secondary":  "#a1a1aa",
    "text_heading":    "#f4f4f5",
    "text_muted":      "#71717a",

    "border":          "#27272a",
    "border_hover":    "#3f3f46",

    "progress_bg":     "#27272a",
    "progress_fill":   "#3b82f6",
    "slider_thumb":    "#e4e4e7",

    "confidence_high": "#22c55e",
    "confidence_mid":  "#eab308",
    "confidence_low":  "#ef4444",

    "timeline_bg":     "#09090b",
    "playhead":        "#ef4444",
}

_R_SM = "4px"
_R_MD = "6px"
_R_LG = "8px"
_R_XL = "10px"


def get_stylesheet() -> str:
    t = THEME
    return f"""
    QMainWindow {{
        background-color: {t['bg_darkest']};
    }}
    QWidget {{
        background-color: transparent;
        color: {t['text_primary']};
        font-family: "Inter", "Noto Sans CJK SC", "WenQuanYi Micro Hei",
                     "Microsoft YaHei", "Segoe UI", sans-serif;
        font-size: 13px;
    }}

    /* Scrollbars */
    QScrollBar:vertical {{
        width: 8px; background: {t['bg_darkest']}; border: none;
    }}
    QScrollBar::handle:vertical {{
        background: {t['bg_widget']}; min-height: 24px; border-radius: {_R_SM};
    }}
    QScrollBar::handle:vertical:hover {{ background: {t['border_hover']}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar:horizontal {{
        height: 8px; background: {t['bg_darkest']}; border: none;
    }}
    QScrollBar::handle:horizontal {{
        background: {t['bg_widget']}; min-width: 24px; border-radius: {_R_SM};
    }}
    QScrollBar::handle:horizontal:hover {{ background: {t['border_hover']}; }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

    /* Strip (compact toolbar row) */
    QWidget#strip {{
        background-color: {t['bg_primary']};
        border-top: 1px solid {t['border']};
    }}

    /* GroupBox */
    QGroupBox {{
        background-color: {t['bg_primary']};
        border: 1px solid {t['border']};
        border-radius: {_R_LG};
        margin-top: 8px;
        padding: 20px 12px 12px 12px;
        font-weight: 600;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 12px; padding: 2px 8px;
        color: {t['text_muted']}; font-size: 11px;
        font-weight: 700; text-transform: uppercase;
    }}

    /* Buttons */
    QPushButton {{
        background-color: {t['bg_widget']};
        color: {t['text_primary']};
        border: 1px solid {t['border_hover']};
        border-radius: {_R_MD};
        padding: 6px 14px; font-weight: 500; font-size: 12px;
    }}
    QPushButton:hover {{
        background-color: {t['border_hover']};
        border-color: #52525b; color: {t['text_heading']};
    }}
    QPushButton:pressed {{ background-color: #52525b; border-color: #52525b; }}
    QPushButton:disabled {{
        background-color: {t['bg_primary']};
        border-color: {t['border']}; color: {t['text_muted']};
    }}

    QPushButton#primaryBtn {{
        background-color: {t['text_heading']};
        color: {t['bg_darkest']};
        border: none; font-weight: 600; padding: 7px 18px;
    }}
    QPushButton#primaryBtn:hover {{ background-color: #ffffff; }}
    QPushButton#primaryBtn:pressed {{ background-color: #d4d4d8; }}
    QPushButton#primaryBtn:disabled {{
        background-color: {t['border_hover']}; color: {t['text_muted']};
    }}

    QPushButton#playBtn {{
        background-color: {t['text_heading']};
        color: {t['bg_darkest']};
        border: none; border-radius: 13px;
        font-weight: 700; font-size: 11px;
        min-width: 26px; min-height: 26px;
        padding: 0px 0px 0px 1px; text-align: center;
    }}
    QPushButton#playBtn:hover {{ background-color: #ffffff; }}
    QPushButton#playBtn:pressed {{ background-color: #d4d4d8; }}

    QPushButton#frameBtn {{
        background-color: transparent; border: none;
        border-radius: 14px; color: {t['text_secondary']};
        font-size: 13px; padding: 0px;
    }}
    QPushButton#frameBtn:hover {{
        background-color: {t['bg_widget']}; color: {t['text_heading']};
    }}
    QPushButton#frameBtn:pressed {{ background-color: {t['border_hover']}; }}

    /* Labels */
    QLabel {{
        color: {t['text_primary']}; background: transparent; font-size: 12px;
    }}
    QLabel#heading {{
        color: {t['text_heading']}; font-weight: 600; font-size: 13px;
    }}
    QLabel#muted {{
        color: {t['text_muted']}; font-size: 11px;
    }}
    QLabel#mono {{
        font-family: "JetBrains Mono", "Cascadia Code", "Consolas", monospace;
        color: {t['text_primary']};
    }}

    /* Slider */
    QSlider::groove:horizontal {{
        height: 4px; background: {t['progress_bg']}; border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {t['slider_thumb']}; width: 12px; height: 12px;
        margin: -4px 0; border-radius: 6px;
        border: 2px solid {t['bg_darkest']};
    }}
    QSlider::handle:horizontal:hover {{ background: {t['accent']}; }}
    QSlider::sub-page:horizontal {{
        background: {t['accent']}; border-radius: 2px;
    }}

    /* Inputs */
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
        background-color: {t['bg_darkest']};
        color: {t['text_primary']};
        border: 1px solid {t['border']};
        border-radius: {_R_MD};
        padding: 5px 8px; font-size: 12px;
        selection-background-color: rgba(59, 130, 246, 0.3);
    }}
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
        border-color: {t['accent']};
    }}
    QSpinBox::up-button, QSpinBox::down-button,
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
        width: 0; border: none;
    }}

    QComboBox::drop-down {{ border: none; padding-right: 8px; width: 20px; }}
    QComboBox::down-arrow {{ image: none; width: 0; }}
    QComboBox QAbstractItemView {{
        background-color: {t['bg_primary']}; color: {t['text_primary']};
        border: 1px solid {t['border']};
        selection-background-color: {t['accent']}; selection-color: #ffffff;
        outline: none; padding: 2px;
    }}
    QComboBox QAbstractItemView::item {{
        padding: 4px 8px; border: none;
        background-color: {t['bg_primary']}; color: {t['text_primary']};
    }}
    QComboBox QAbstractItemView::item:selected {{
        background-color: {t['accent']}; color: #ffffff;
    }}
    QComboBox QFrame {{
        border: 1px solid {t['border']}; background-color: {t['bg_primary']};
    }}

    /* Progress bar */
    QProgressBar {{
        background-color: {t['bg_darkest']};
        border: 1px solid {t['border']};
        border-radius: {_R_MD};
        text-align: center; color: {t['text_primary']};
        font-size: 11px; min-height: 18px; max-height: 18px;
    }}
    QProgressBar::chunk {{
        background-color: {t['accent']}; border-radius: 5px;
    }}

    /* Tooltip */
    QToolTip {{
        background-color: {t['bg_primary']}; color: {t['text_primary']};
        border: 1px solid {t['border_hover']};
        padding: 6px 8px; border-radius: {_R_MD}; font-size: 12px;
    }}

    /* Video widget */
    QVideoWidget {{
        background-color: {t['bg_darkest']};
        border: 1px solid {t['border']}; border-radius: {_R_XL};
    }}

    /* System dialogs */
    QHeaderView::section {{
        background-color: {t['bg_primary']}; color: {t['text_secondary']};
        border: 1px solid {t['border']}; padding: 4px;
    }}
    QMenu {{
        background-color: {t['bg_primary']}; color: {t['text_primary']};
        border: 1px solid {t['border']}; padding: 4px;
    }}
    QMenu::item:selected {{
        background-color: {t['accent']}; color: #ffffff;
    }}
    """
