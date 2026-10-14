"""LaTeX maths inside text labels: ``$…$`` typeset in place.

A label's QTextDocument is left untouched (it is what is saved and edited);
for drawing and sizing, ``typeset(doc)`` returns a copy in which every
``$…$`` is replaced by an inline object drawn by ``MathObject`` as a vector
path from Matplotlib's mathtext, at the size and colour of the surrounding
text. ``\\$`` stays a literal dollar.

Engines (label_math_engine): with a LaTeX installation each formula is typeset
by LaTeX itself — full LaTeX: siunitx, bm, any amsmath construct — in Latin
Modern (sans-serif maths for sans-serif labels), and kept as an SVG in the
caches of batoolset.latex_tools (PyFigures puts the figure's own
``equations/labels`` folder first, so the formulas travel with the figure and
render identically on computers without TeX). Otherwise Matplotlib's mathtext
is used, with the label's own font family for letters when Matplotlib knows it
("custom" fontset), else STIX sans (or STIX for serif fonts). The LaTeX export
still hands the $…$ to LaTeX itself.
"""
from __future__ import annotations

import functools
import re

from qtpy.QtCore import QPointF, QRectF, QSizeF, Qt
from qtpy.QtGui import (QColor, QFont, QFontInfo, QFontMetricsF, QPainterPath, QTextCharFormat,
                        QTextCursor, QTextDocument, QTextFormat)

try:  # PyQt
    from qtpy.QtGui import QPyTextObject as _TextObjectBase
except ImportError:  # PySide
    from qtpy.QtCore import QObject
    from qtpy.QtGui import QTextObjectInterface

    class _TextObjectBase(QObject, QTextObjectInterface):
        pass

MATH = re.compile(r"(?<!\\)\$(?!\s)([^$\n]*?[^\s\\$])\$")
OBJECT_TYPE = int(QTextFormat.ObjectTypes.UserObject.value if hasattr(QTextFormat.ObjectTypes.UserObject, "value")
                  else QTextFormat.ObjectTypes.UserObject) + 41
PROP_TEX = int(QTextFormat.Property.UserProperty.value if hasattr(QTextFormat.Property.UserProperty, "value")
               else QTextFormat.Property.UserProperty) + 41
_OBJECT_CHAR = "￼"


def has_math(text) -> bool:
    return bool(text) and MATH.search(text) is not None


def _fontset_for(family, italic_ok=True):
    """rcParams for mathtext matching *family* (see module docstring)."""
    from matplotlib import font_manager
    try:
        font_manager.findfont(font_manager.FontProperties(family=family), fallback_to_default=False)
        return {"mathtext.fontset": "custom", "mathtext.rm": family, "mathtext.it": f"{family}:italic",
                "mathtext.bf": f"{family}:bold", "mathtext.sf": family}
    except Exception:
        serif = any(k in (family or "").lower() for k in ("times", "serif", "roman", "georgia", "garamond"))
        return {"mathtext.fontset": "stix" if serif else "stixsans"}


@functools.lru_cache(maxsize=512)
def math_path(tex, size_px, family):
    """(QPainterPath with the baseline at y=0, advance width, ascent, descent)
    of the formula *tex* (without dollars) at *size_px* pixels per em."""
    import matplotlib
    from matplotlib.font_manager import FontProperties
    from matplotlib.textpath import TextPath
    with matplotlib.rc_context(_fontset_for(family)):
        tp = TextPath((0, 0), f"${tex}$", size=size_px, prop=FontProperties(family=family, size=size_px))
        verts = tp.vertices
        codes = tp.codes
    path = QPainterPath()
    i = 0
    n = len(verts)
    while i < n:
        code = codes[i] if codes is not None else (1 if i == 0 else 2)
        x, y = float(verts[i][0]), -float(verts[i][1])          # y up -> y down
        if code == 1:
            path.moveTo(x, y)
            i += 1
        elif code == 2:
            path.lineTo(x, y)
            i += 1
        elif code == 3 and i + 1 < n:
            path.quadTo(QPointF(x, y), QPointF(float(verts[i + 1][0]), -float(verts[i + 1][1])))
            i += 2
        elif code == 4 and i + 2 < n:
            path.cubicTo(QPointF(x, y), QPointF(float(verts[i + 1][0]), -float(verts[i + 1][1])),
                         QPointF(float(verts[i + 2][0]), -float(verts[i + 2][1])))
            i += 3
        else:                                                   # CLOSEPOLY / STOP
            path.closeSubpath()
            i += 1
    box = path.boundingRect()
    width = max(box.right(), 0.0) + size_px * 0.06
    ascent = max(-box.top(), 0.0)
    descent = max(box.bottom(), 0.0)
    return path, width, ascent, descent


def _em_px(font: QFont) -> float:
    if font.pixelSize() > 0:
        return float(font.pixelSize())
    info = QFontInfo(font)
    if info.pixelSize() > 0 and font.pointSizeF() > 0:
        # the same px/pt the text layout uses, without QFontInfo's rounding
        return font.pointSizeF() * info.pixelSize() / max(info.pointSizeF(), 1e-6)
    return float(info.pixelSize() or 12)


def label_math_engine():
    """"auto" (default: LaTeX when installed, or when the formula was already
    typeset by LaTeX and is cached; else mathtext), "latex" or "mathtext"
    (environment variable PYFIGURES_LABEL_MATH)."""
    import os
    value = (os.environ.get("PYFIGURES_LABEL_MATH") or "auto").strip().lower()
    return value if value in ("auto", "latex", "mathtext") else "auto"


_SERIF_HINTS = ("times", "serif", "roman", "georgia", "garamond", "palatino", "computer modern",
                "cmu", "latin modern", "baskerville", "cambria", "book")


@functools.lru_cache(maxsize=256)
def _svg_renderer(path):
    from qtpy.QtSvg import QSvgRenderer
    return QSvgRenderer(path)


def _latex_math(tex, font, color):
    """(svg path, width, height, depth) in points from the LaTeX installation
    or its caches (batoolset.latex_tools), or None (-> mathtext)."""
    engine = label_math_engine()
    if engine == "mathtext":
        return None
    try:
        from batoolset import latex_tools as LT
    except ImportError:
        return None
    size_pt = font.pointSizeF() if font.pointSizeF() > 0 else _em_px(font) * 0.75
    family = (font.family() or "").lower()
    sans = "sans" in family or not any(h in family for h in _SERIF_HINTS)
    return LT.inline_math_svg(tex, round(size_pt, 2), sans=sans, color=color.name(),
                              compile_missing=LT.latex_available())


class MathObject(_TextObjectBase):
    """Draws the formula stored in an object character's format. Placed with
    Qt's AlignMiddle (centred half an x-height above the baseline, i.e. on the
    maths axis), its box sized so the formula's own baseline lands on the text
    baseline. Typeset by LaTeX when available (label_math_engine), else by
    Matplotlib's mathtext."""

    def _geometry(self, fmt):
        cf = _char_format(fmt)
        font = cf.font()
        tex = str(fmt.property(PROP_TEX))
        brush = cf.foreground()
        color = brush.color() if brush.style() != Qt.BrushStyle.NoBrush else QColor("black")
        em = _em_px(font)
        latex = _latex_math(tex, font, color)
        if latex is not None:
            svg, w_pt, h_pt, d_pt = latex
            size_pt = font.pointSizeF() if font.pointSizeF() > 0 else em * 0.75
            k = em / max(size_pt, 1e-6)                          # px per pt, as the text uses
            drawing = ("svg", svg, w_pt * k, h_pt * k, d_pt * k)
            width, ascent, descent = w_pt * k, h_pt * k, d_pt * k
        else:
            path, width, ascent, descent = math_path(tex, round(em, 3), font.family())
            drawing = ("path", path, color)
        half_x = QFontMetricsF(font).xHeight() / 2.0
        # Qt (AlignMiddle): object ascent = (h + half_x) / 2, descent = (h - half_x) / 2
        height = max(2 * ascent - half_x, 2 * descent + half_x, 1.0)
        return drawing, width, height, (height + half_x) / 2.0

    # Qt calls these two from C++: an exception escaping them aborts the
    # process (PyQt), so a formula that cannot be typeset is left empty
    def intrinsicSize(self, doc, pos, fmt):
        try:
            _, width, height, _ = self._geometry(fmt)
            return QSizeF(width, height)
        except Exception:
            _log_failure(fmt)
            return QSizeF(0, 0)

    def drawObject(self, painter, rect, doc, pos, fmt):
        try:
            drawing, _, _, baseline = self._geometry(fmt)
            painter.save()
            try:
                painter.translate(rect.left(), rect.top() + baseline)
                if drawing[0] == "svg":
                    _, svg, w, h, d = drawing
                    # the SVG's baseline is y = 0: its box spans [-h, +d]
                    _svg_renderer(svg).render(painter, QRectF(0.0, -h, w, h + d))
                else:
                    painter.fillPath(drawing[1], drawing[2])
            finally:
                painter.restore()
        except Exception:
            _log_failure(fmt)


def _char_format(fmt):
    return fmt if isinstance(fmt, QTextCharFormat) else fmt.toCharFormat()


def _log_failure(fmt):
    import traceback
    from batoolset.tools.logger import TA_logger
    TA_logger().error("cannot typeset $" + str(fmt.property(PROP_TEX)) + "$:\n" + traceback.format_exc())


_OWNER_CACHE = {}      # id(owner) -> (weakref to owner, key, typeset document)


def typeset_for(owner, doc: QTextDocument) -> QTextDocument:
    """typeset(doc), cached per *owner* (a label or text box) until *doc*
    changes. The cache lives here, not on the owner, so it is never saved
    with the figure nor copied with the shape."""
    import weakref
    key = (id(doc), doc.revision(), doc.defaultFont().toString())
    entry = _OWNER_CACHE.get(id(owner))
    if entry is not None and entry[0]() is owner and entry[1] == key:
        return entry[2]
    out = typeset(doc)
    try:
        ref = weakref.ref(owner, lambda _r, k=id(owner): _OWNER_CACHE.pop(k, None))
    except TypeError:
        return out
    _OWNER_CACHE[id(owner)] = (ref, key, out)
    return out


def typeset(doc: QTextDocument) -> QTextDocument:
    """A copy of *doc* with every $…$ drawn as maths (see module docstring);
    *doc* itself if it has none."""
    if not has_math(doc.toPlainText()):
        return doc
    out = doc.clone()
    handler = MathObject()
    out.documentLayout().registerHandler(OBJECT_TYPE, handler)
    out._pyf_math_handler = handler                          # keep it alive with the document
    text = out.toPlainText()
    for m in reversed(list(MATH.finditer(text))):
        cursor = QTextCursor(out)
        cursor.setPosition(m.start() + 1)                    # format of the formula's first char
        base = cursor.charFormat()
        cursor.setPosition(m.start())
        cursor.setPosition(m.end(), QTextCursor.MoveMode.KeepAnchor)
        fmt = QTextCharFormat(base)
        fmt.setObjectType(OBJECT_TYPE)
        fmt.setProperty(PROP_TEX, m.group(1))
        fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignMiddle)
        cursor.insertText(_OBJECT_CHAR, fmt)
    # escaped dollars are shown as dollars
    cursor = QTextCursor(out)
    while True:
        cursor = out.find("\\$", cursor)
        if cursor.isNull():
            break
        cursor.insertText("$")
    out.adjustSize()
    return out
