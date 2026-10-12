from __future__ import annotations
"""
Centralised theme management for all batoolset-based Qt applications.

Two built-in themes (Catppuccin palette):
  "dark"   – Catppuccin Mocha  [default]
  "white"  – Catppuccin Latte

Public API
----------
apply_theme(app, name, *, font_size=None)
    Apply a theme to a QApplication.  Pass font_size (px) to also set the
    application font; omit to leave the font unchanged.

current_theme() -> str
    Return the name of the currently active theme.

painter_colors() -> dict
    Colour-token dict for the active theme.  Use this in QPainter-based
    widgets that QSS cannot reach.

load_theme(settings_path=None, default='dark') -> str
    Read the saved theme from a JSON file.  If settings_path is None the
    call returns default without touching the filesystem.

save_theme(name, settings_path=None) -> None
    Persist the theme name to a JSON file.  No-op when settings_path is None.

Typical usage in an application
---------------------------------
    import os
    from batoolset.theme import apply_theme, load_theme, save_theme, current_theme

    _SETTINGS = os.path.join(os.path.dirname(__file__), 'settings.json')

    # On startup:
    t = load_theme(_SETTINGS)
    apply_theme(app, t)

    # When the user picks a theme:
    apply_theme(app, 'dark')
    save_theme('dark', _SETTINGS)
"""

import json
import os

from qtpy.QtCore    import Qt
from qtpy.QtGui     import QColor, QFont, QPainter, QPainterPath, QPalette
from qtpy.QtWidgets import QApplication, QProxyStyle, QStyle

# ---------------------------------------------------------------------------
# Proxy style – draws visible filled-triangle arrows for QSpinBox / QComboBox
#
# When QSS sets background-color on QSpinBox, Fusion hands full sub-control
# ownership to the stylesheet engine and the native arrows vanish unless an
# image: rule is provided.  We intercept all four PE_IndicatorArrow* primitives
# and paint filled triangles in the palette's ButtonText colour, which tracks
# theme changes automatically.
# ---------------------------------------------------------------------------

class _FusionArrowFix(QProxyStyle):
    _ARROW_ELEMENTS = frozenset({
        QStyle.PrimitiveElement.PE_IndicatorArrowUp,
        QStyle.PrimitiveElement.PE_IndicatorArrowDown,
        QStyle.PrimitiveElement.PE_IndicatorArrowLeft,
        QStyle.PrimitiveElement.PE_IndicatorArrowRight,
    })

    def drawPrimitive(self, element, option, painter, widget=None):
        if element not in self._ARROW_ELEMENTS:
            super().drawPrimitive(element, option, painter, widget)
            return
        color = QApplication.instance().palette().color(QPalette.ColorRole.ButtonText)
        r    = option.rect
        cx   = r.center().x()
        cy   = r.center().y()
        half = max(3, min(r.width(), r.height()) // 4)
        path = QPainterPath()
        PE   = QStyle.PrimitiveElement
        if element == PE.PE_IndicatorArrowUp:
            path.moveTo(cx,        cy - half)
            path.lineTo(cx - half, cy + half)
            path.lineTo(cx + half, cy + half)
        elif element == PE.PE_IndicatorArrowDown:
            path.moveTo(cx,        cy + half)
            path.lineTo(cx - half, cy - half)
            path.lineTo(cx + half, cy - half)
        elif element == PE.PE_IndicatorArrowLeft:
            path.moveTo(cx - half, cy)
            path.lineTo(cx + half, cy - half)
            path.lineTo(cx + half, cy + half)
        else:
            path.moveTo(cx + half, cy)
            path.lineTo(cx - half, cy - half)
            path.lineTo(cx - half, cy + half)
        path.closeSubpath()
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawPath(path)
        painter.restore()


# Kept alive at module level so GC does not destroy it after setStyle()
# transfers C++ ownership.
_proxy_style: _FusionArrowFix | None = None
_active: str = "default"
# Original palette/style captured before the first theme change so 'default'
# can restore the platform appearance.
_original_palette: QPalette | None = None
_original_style_name: str | None = None

# ---------------------------------------------------------------------------
# WHITE — Catppuccin Latte
# ---------------------------------------------------------------------------

WHITE_QSS = """
QWidget {
    background-color: #eff1f5;
    color: #4c4f69;
    font-size: 13px;
}
QMainWindow, QDialog { background-color: #eff1f5; }
QFrame { background-color: #eff1f5; border: none; }
QSplitter::handle { background-color: #ccd0da; }

QMenuBar {
    background-color: #e6e9ef;
    color: #4c4f69;
    border-bottom: 1px solid #ccd0da;
}
QMenuBar::item:selected { background-color: #ccd0da; }
QMenu {
    background-color: #eff1f5;
    border: 1px solid #bcc0cc;
    color: #4c4f69;
}
QMenu::item:selected { background-color: #ccd0da; }
QMenu::separator { height: 1px; background: #bcc0cc; margin: 2px 8px; }

QToolBar {
    background-color: #e6e9ef;
    border-bottom: 1px solid #ccd0da;
    spacing: 3px;
    padding: 2px 4px;
}
QToolBar::separator { background-color: #bcc0cc; width: 1px; margin: 3px 4px; }

QPushButton {
    background-color: #ccd0da;
    color: #4c4f69;
    border: 1px solid #bcc0cc;
    border-radius: 4px;
    padding: 3px 10px;
}
QPushButton:hover   { background-color: #bcc0cc; border-color: #acb0be; }
QPushButton:pressed { background-color: #acb0be; }
QPushButton:checked { background-color: #1e66f5; color: #eff1f5; border-color: #1e66f5; }
QPushButton:disabled { background-color: #dce0e8; color: #9ca0b0; border-color: #ccd0da; }

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    color: #4c4f69;
    border: 1px solid #bcc0cc;
    border-radius: 4px;
    padding: 2px 6px;
    selection-background-color: #1e66f5;
    selection-color: #ffffff;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus { border-color: #1e66f5; }
QLineEdit:read-only { background-color: #eff1f5; color: #9ca0b0; }

/* SpinBox / date-time: styled only via the palette so Fusion renders
   up/down buttons and arrows natively.  Only font-size is set here. */
QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit { font-size: 13px; }

QComboBox {
    background-color: #ffffff;
    color: #4c4f69;
    border: 1px solid #bcc0cc;
    border-radius: 4px;
    padding: 2px 6px;
}
QComboBox:focus { border-color: #1e66f5; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #4c4f69;
    selection-background-color: #ccd0da;
    border: 1px solid #bcc0cc;
}

QLabel { background: transparent; color: #4c4f69; }

QCheckBox { color: #4c4f69; spacing: 6px; }
QCheckBox::indicator {
    width: 14px; height: 14px;
    border: 1px solid #bcc0cc;
    border-radius: 3px;
    background-color: #ffffff;
}
QCheckBox::indicator:checked { background-color: #1e66f5; border-color: #1e66f5; }

QListWidget, QTreeWidget, QListView, QTreeView {
    background-color: #ffffff;
    color: #4c4f69;
    border: 1px solid #ccd0da;
    border-radius: 4px;
    alternate-background-color: #eff1f5;
    outline: none;
}
QListWidget::item, QTreeWidget::item { padding: 3px 6px; }
QListWidget::item:selected, QTreeWidget::item:selected {
    background-color: #ccd0da; color: #1e66f5;
}
QListWidget::item:hover, QTreeWidget::item:hover { background-color: #e6e9ef; }

QTableWidget, QTableView {
    background-color: #ffffff;
    color: #4c4f69;
    gridline-color: #ccd0da;
    border: 1px solid #ccd0da;
    alternate-background-color: #eff1f5;
    outline: none;
}
QTableWidget::item:selected, QTableView::item:selected {
    background-color: #ccd0da; color: #1e66f5;
}
QHeaderView::section {
    background-color: #e6e9ef;
    color: #5c5f77;
    border: none;
    border-right: 1px solid #ccd0da;
    border-bottom: 1px solid #ccd0da;
    padding: 4px 8px;
    font-weight: 600;
}
QHeaderView::section:checked { background-color: #ccd0da; }

QScrollBar:vertical { background: #e6e9ef; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #bcc0cc; border-radius: 5px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: #acb0be; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #e6e9ef; height: 10px; margin: 0; }
QScrollBar::handle:horizontal { background: #bcc0cc; border-radius: 5px; min-width: 20px; }
QScrollBar::handle:horizontal:hover { background: #acb0be; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

QTabWidget::pane { border: 1px solid #ccd0da; background-color: #eff1f5; }
QTabBar::tab {
    background-color: #e6e9ef; color: #6c6f85;
    border: 1px solid #ccd0da; border-bottom: none;
    padding: 5px 14px;
    border-top-left-radius: 4px; border-top-right-radius: 4px;
}
QTabBar::tab:selected { background-color: #eff1f5; color: #4c4f69; border-bottom: 2px solid #1e66f5; }
QTabBar::tab:hover:!selected { background-color: #dce0e8; }

QDockWidget { color: #4c4f69; titlebar-close-icon: none; }
QDockWidget::title {
    background-color: #e6e9ef; color: #4c4f69;
    padding: 4px 8px; border-bottom: 1px solid #ccd0da;
}

QGroupBox {
    border: 1px solid #ccd0da; border-radius: 4px;
    margin-top: 12px; color: #6c6f85;
}
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 4px; left: 10px; }

QStatusBar { background-color: #e6e9ef; color: #5c5f77; border-top: 1px solid #ccd0da; }
QStatusBar::item { border: none; }

QProgressDialog { background-color: #eff1f5; color: #4c4f69; }
QProgressBar {
    background-color: #dce0e8; border: 1px solid #bcc0cc;
    border-radius: 4px; text-align: center; color: #4c4f69; height: 14px;
}
QProgressBar::chunk { background-color: #1e66f5; border-radius: 4px; }

QScrollArea { border: none; background-color: transparent; }
QScrollArea > QWidget > QWidget { background-color: transparent; }
QMessageBox { background-color: #eff1f5; }
"""

# ---------------------------------------------------------------------------
# DARK — Catppuccin Mocha
# ---------------------------------------------------------------------------

DARK_QSS = """
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-size: 13px;
}
QMainWindow, QDialog { background-color: #1e1e2e; }
QFrame { background-color: #1e1e2e; border: none; }
QSplitter::handle { background-color: #313244; }

QMenuBar {
    background-color: #181825;
    color: #cdd6f4;
    border-bottom: 1px solid #313244;
}
QMenuBar::item:selected { background-color: #313244; }
QMenu {
    background-color: #1e1e2e;
    border: 1px solid #45475a;
    color: #cdd6f4;
}
QMenu::item:selected { background-color: #313244; }
QMenu::separator { height: 1px; background: #45475a; margin: 2px 8px; }

QToolBar {
    background-color: #181825;
    border-bottom: 1px solid #313244;
    spacing: 3px;
    padding: 2px 4px;
}
QToolBar::separator { background-color: #45475a; width: 1px; margin: 3px 4px; }

QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 3px 10px;
}
QPushButton:hover   { background-color: #45475a; border-color: #585b70; }
QPushButton:pressed { background-color: #585b70; }
QPushButton:checked { background-color: #89b4fa; color: #1e1e2e; border-color: #89b4fa; }
QPushButton:disabled { background-color: #27273a; color: #6c7086; border-color: #313244; }

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 2px 6px;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus { border-color: #89b4fa; }
QLineEdit:read-only { background-color: #1e1e2e; color: #6c7086; }

/* SpinBox / date-time: styled only via the palette so Fusion renders
   up/down buttons and arrows natively. */
QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit { font-size: 13px; }

QComboBox {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 2px 6px;
}
QComboBox:focus { border-color: #89b4fa; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background-color: #181825;
    color: #cdd6f4;
    selection-background-color: #313244;
    border: 1px solid #45475a;
}

QLabel { background: transparent; color: #cdd6f4; }

QCheckBox { color: #cdd6f4; spacing: 6px; }
QCheckBox::indicator {
    width: 14px; height: 14px;
    border: 1px solid #45475a;
    border-radius: 3px;
    background-color: #181825;
}
QCheckBox::indicator:checked { background-color: #89b4fa; border-color: #89b4fa; }

QListWidget, QTreeWidget, QListView, QTreeView {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #313244;
    border-radius: 4px;
    alternate-background-color: #1e1e2e;
    outline: none;
}
QListWidget::item, QTreeWidget::item { padding: 3px 6px; }
QListWidget::item:selected, QTreeWidget::item:selected {
    background-color: #313244; color: #89b4fa;
}
QListWidget::item:hover, QTreeWidget::item:hover { background-color: #27273a; }

QTableWidget, QTableView {
    background-color: #181825;
    color: #cdd6f4;
    gridline-color: #313244;
    border: 1px solid #313244;
    alternate-background-color: #1e1e2e;
    outline: none;
}
QTableWidget::item:selected, QTableView::item:selected {
    background-color: #313244; color: #89b4fa;
}
QHeaderView::section {
    background-color: #1e1e2e;
    color: #a6adc8;
    border: none;
    border-right: 1px solid #313244;
    border-bottom: 1px solid #313244;
    padding: 4px 8px;
    font-weight: 600;
}
QHeaderView::section:checked { background-color: #313244; }

QScrollBar:vertical { background: #181825; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #45475a; border-radius: 5px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: #585b70; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #181825; height: 10px; margin: 0; }
QScrollBar::handle:horizontal { background: #45475a; border-radius: 5px; min-width: 20px; }
QScrollBar::handle:horizontal:hover { background: #585b70; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

QTabWidget::pane { border: 1px solid #313244; background-color: #1e1e2e; }
QTabBar::tab {
    background-color: #181825; color: #a6adc8;
    border: 1px solid #313244; border-bottom: none;
    padding: 5px 14px;
    border-top-left-radius: 4px; border-top-right-radius: 4px;
}
QTabBar::tab:selected { background-color: #1e1e2e; color: #cdd6f4; border-bottom: 2px solid #89b4fa; }
QTabBar::tab:hover:!selected { background-color: #27273a; }

QDockWidget { color: #cdd6f4; titlebar-close-icon: none; }
QDockWidget::title {
    background-color: #181825; color: #cdd6f4;
    padding: 4px 8px; border-bottom: 1px solid #313244;
}

QGroupBox {
    border: 1px solid #313244; border-radius: 4px;
    margin-top: 12px; color: #a6adc8;
}
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 4px; left: 10px; }

QStatusBar { background-color: #181825; color: #a6adc8; border-top: 1px solid #313244; }
QStatusBar::item { border: none; }

QProgressDialog { background-color: #1e1e2e; color: #cdd6f4; }
QProgressBar {
    background-color: #181825; border: 1px solid #45475a;
    border-radius: 4px; text-align: center; color: #cdd6f4; height: 14px;
}
QProgressBar::chunk { background-color: #89b4fa; border-radius: 4px; }

QScrollArea { border: none; background-color: transparent; }
QScrollArea > QWidget > QWidget { background-color: transparent; }
QMessageBox { background-color: #1e1e2e; }
"""

# ---------------------------------------------------------------------------
# Painter colour tokens
# For QPainter-based widgets that QSS cannot reach (canvas, ruler, etc.)
# ---------------------------------------------------------------------------

_DARK_COLORS: dict = {
    "bg":             "#1e1e2e",
    "bg_empty":       "#1e1e2e",
    "empty_text":     "#888888",
    "backbone":       "#cccccc",
    "tick_minor":     "#555555",
    "tick_major":     "#888888",
    "tick_label":     "#999999",
    "title":          "#eeeeee",
    "ruler_line":     "#555555",
    "ruler_tick":     "#888888",
    "ruler_label":    "#999999",
    "sel_outline":    "#ffffff",
    "feat_label_sel": "#ffffff",
    "seq_row_bg":     "#181825",
    "seq_text":       "#cdd6f4",
}

_WHITE_COLORS: dict = {
    "bg":             "#eff1f5",
    "bg_empty":       "#eff1f5",
    "empty_text":     "#9ca0b0",
    "backbone":       "#4c4f69",
    "tick_minor":     "#bcc0cc",
    "tick_major":     "#9ca0b0",
    "tick_label":     "#6c6f85",
    "title":          "#4c4f69",
    "ruler_line":     "#bcc0cc",
    "ruler_tick":     "#9ca0b0",
    "ruler_label":    "#6c6f85",
    "sel_outline":    "#313244",
    "feat_label_sel": "#1e1e2e",
    "seq_row_bg":     "#ffffff",
    "seq_text":       "#4c4f69",
}

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def current_theme() -> str:
    """Return the name of the currently active theme ('dark' or 'white')."""
    return _active


def painter_colors() -> dict:
    """Return the colour-token dict for the active theme.

    Use these values in QPainter-based widgets that cannot be reached by QSS.
    Falls back to white palette tokens for the 'default' theme.
    """
    if _active == "dark":
        return _DARK_COLORS
    return _WHITE_COLORS


def apply_theme(app: QApplication, name: str, *, font_size: int | None = None) -> None:
    """Apply a theme to *app*.

    Parameters
    ----------
    app:
        The QApplication instance to style.
    name:
        'dark', 'white', or 'default'.  'default' restores the platform
        appearance (clears QSS and resets the palette/style to what they were
        before the first call to apply_theme).  Any unrecognised value is
        treated as 'default'.
    font_size:
        If given, set the application-wide font to this pixel size.
        Omit to leave the font unchanged.
    """
    global _active, _proxy_style, _original_palette, _original_style_name

    # Capture the pristine palette/style name on the very first call.
    if _original_palette is None:
        _original_palette = QPalette(app.palette())
    if _original_style_name is None:
        _original_style_name = app.style().objectName()  # e.g. 'windowsvista'

    name_lc = name.lower() if name else 'default'
    _active = name_lc if name_lc in ('dark', 'white') else 'default'

    # --- Default: restore platform appearance ---
    if _active == 'default':
        app.setStyleSheet('')
        app.setPalette(_original_palette)
        if _proxy_style is not None:
            app.setStyle(_original_style_name)
        return

    # --- Dark / White: apply Fusion + Catppuccin ---
    if _proxy_style is None:
        _proxy_style = _FusionArrowFix('Fusion')
        app.setStyle(_proxy_style)

    if font_size is not None:
        f = QFont(app.font())
        f.setPixelSize(font_size)
        app.setFont(f)

    app.setStyleSheet(DARK_QSS if _active == 'dark' else WHITE_QSS)

    CR  = QPalette.ColorRole
    pal = app.palette()
    if _active == 'dark':
        pal.setColor(CR.Window,          QColor("#1e1e2e"))
        pal.setColor(CR.WindowText,      QColor("#cdd6f4"))
        pal.setColor(CR.Base,            QColor("#181825"))
        pal.setColor(CR.AlternateBase,   QColor("#1e1e2e"))
        pal.setColor(CR.Text,            QColor("#cdd6f4"))
        pal.setColor(CR.Button,          QColor("#313244"))
        pal.setColor(CR.ButtonText,      QColor("#cdd6f4"))
        pal.setColor(CR.Mid,             QColor("#45475a"))
        pal.setColor(CR.Dark,            QColor("#585b70"))
        pal.setColor(CR.Highlight,       QColor("#89b4fa"))
        pal.setColor(CR.HighlightedText, QColor("#1e1e2e"))
        pal.setColor(CR.ToolTipBase,     QColor("#181825"))
        pal.setColor(CR.ToolTipText,     QColor("#cdd6f4"))
    else:
        pal.setColor(CR.Window,          QColor("#eff1f5"))
        pal.setColor(CR.WindowText,      QColor("#4c4f69"))
        pal.setColor(CR.Base,            QColor("#ffffff"))
        pal.setColor(CR.AlternateBase,   QColor("#eff1f5"))
        pal.setColor(CR.Text,            QColor("#4c4f69"))
        pal.setColor(CR.Button,          QColor("#dce0e8"))
        pal.setColor(CR.ButtonText,      QColor("#4c4f69"))
        pal.setColor(CR.Mid,             QColor("#bcc0cc"))
        pal.setColor(CR.Dark,            QColor("#9ca0b0"))
        pal.setColor(CR.Highlight,       QColor("#1e66f5"))
        pal.setColor(CR.HighlightedText, QColor("#ffffff"))
        pal.setColor(CR.ToolTipBase,     QColor("#ffffff"))
        pal.setColor(CR.ToolTipText,     QColor("#4c4f69"))
    app.setPalette(pal)


def load_theme(settings_path: str | None = None, default: str = "dark") -> str:
    """Load the saved theme name from a JSON settings file.

    Parameters
    ----------
    settings_path:
        Path to a JSON file that contains a ``"theme"`` key.
        Pass None (or omit) to skip file I/O and just return *default*.
    default:
        Fallback value when the file is missing, unreadable, or has no
        ``"theme"`` key.  Must be ``'dark'`` or ``'white'``.
    """
    if settings_path is None:
        return default
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("theme", default)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def save_theme(name: str, settings_path: str | None = None) -> None:
    """Persist *name* to a JSON settings file.

    Parameters
    ----------
    name:
        Theme name to save (``'dark'`` or ``'white'``).
    settings_path:
        Path to the JSON file.  If None the call is a no-op.
    """
    if settings_path is None:
        return
    data: dict = {}
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    data["theme"] = name
    try:
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass
