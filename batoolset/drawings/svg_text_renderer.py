"""Draw an SVG's ``<text>`` elements as real text, the rest with Qt's renderer.

Qt's SVG renderer draws SVG text as glyph outlines when the target is another
SVG (QSvgGenerator), so the text of a Matplotlib plot exported with
``svg.fonttype = 'none'`` still arrived as shapes in the editable PowerPoint /
Illustrator exports: tick labels and axis titles could not be edited.
``TextAsTextRenderer`` renders the SVG without its text, then draws each text
run with ``QPainter.drawText`` at the same place, size, colour and rotation,
which an SVG painter records as a ``<text>`` element.

Single-glyph runs on one baseline (Matplotlib writes mathtext one glyph per
``<tspan>``) are joined into one run, so a label stays one editable string.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from qtpy.QtCore import QByteArray, QPointF, QRectF, Qt
from qtpy.QtGui import QColor, QFont, QFontMetricsF, QTransform
from qtpy.QtSvg import QSvgRenderer

from batoolset.drawings.pdf_svg_renderer import parse_transform

_SVG_NS = "http://www.w3.org/2000/svg"
_NUM = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def _tag(el):
    return el.tag.split("}", 1)[-1] if isinstance(el.tag, str) else ""


def _f(v, d=0.0):
    try:
        return float(_NUM.match(str(v).strip()).group(0))
    except (AttributeError, TypeError, ValueError):
        return d


def _style(el, inherited):
    st = dict(inherited)
    for part in (el.get("style") or "").split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            st[k.strip()] = v.strip()
    for k in ("font-size", "font-family", "font-weight", "font-style", "fill", "text-anchor", "opacity",
              "fill-opacity"):
        if el.get(k) is not None:
            st[k] = el.get(k)
    return st


def _family(value):
    """First family of a CSS font-family list, without quotes."""
    first = (value or "").split(",")[0].strip().strip("'\"")
    return first or "Arial"


def _color(value, opacity):
    c = QColor(0, 0, 0)
    if value and value != "none":
        m = re.match(r"rgb\(\s*([\d.]+)%?\s*,\s*([\d.]+)%?\s*,\s*([\d.]+)%?\s*\)", value)
        if m:
            c = QColor(int(float(m.group(1))), int(float(m.group(2))), int(float(m.group(3))))
        else:
            c = QColor(value)
            if not c.isValid():
                c = QColor(0, 0, 0)
    c.setAlphaF(max(0.0, min(1.0, opacity)))
    return c


def _runs_of(text_el, style, transform):
    """[(text, x, y, style, transform)] for a <text> element and its tspans."""
    runs = []
    own_x = _f(text_el.get("x"))
    own_y = _f(text_el.get("y"))
    if text_el.text and text_el.text.strip():
        runs.append([text_el.text, own_x, own_y, style, transform])
    for span in text_el:
        if _tag(span) != "tspan":
            continue
        st = _style(span, style)
        x = _f(span.get("x"), own_x)
        y = _f(span.get("y"), own_y)
        if span.text:
            runs.append([span.text.replace("\xa0", " "), x, y, st, transform])
    # mathtext writes its glyphs in drawing order, not reading order
    runs.sort(key=lambda r: (round(r[2], 3), r[1]))
    merged = []
    for run in runs:
        prev = merged[-1] if merged else None
        if (prev is not None and abs(prev[2] - run[2]) < 1e-6 and prev[4] == run[4]
                and prev[3].get("font-size") == run[3].get("font-size")
                and prev[3].get("text-anchor", "start") == "start"):
            prev[0] += run[0]
        else:
            merged.append(run)
    return merged


class TextAsTextRenderer(QSvgRenderer):
    """QSvgRenderer for an SVG whose text should stay text (see module doc)."""

    def __init__(self, svg_bytes, make_renderer=None):
        root = ET.fromstring(svg_bytes)
        self._texts = []
        self._collect(root, QTransform(), {}, None)
        ET.register_namespace("", _SVG_NS)
        ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
        stripped = ET.tostring(root)
        super().__init__(QByteArray(stripped))
        # the drawing without its text, by the usual renderer (clip paths...)
        self._inner = make_renderer(stripped) if make_renderer is not None else QSvgRenderer(QByteArray(stripped))
        self._pyf_svg_source = bytes(svg_bytes)

    def _collect(self, el, parent_t, parent_style, parent):
        t = parse_transform(el.get("transform")) * parent_t
        style = _style(el, parent_style)
        for child in list(el):
            if _tag(child) == "text":
                child_t = parse_transform(child.get("transform")) * t
                self._texts.extend(_runs_of(child, _style(child, style), child_t))
                el.remove(child)
            elif _tag(child) not in ("defs", "clipPath", "style", "metadata"):
                self._collect(child, t, style, el)

    def text_runs(self):
        return [(r[0], r[1], r[2]) for r in self._texts]

    def setAspectRatioMode(self, mode):
        super().setAspectRatioMode(mode)
        self._inner.setAspectRatioMode(mode)

    def render(self, painter, *args):
        if len(args) == 1 and isinstance(args[0], str) or len(args) >= 2:
            return self._inner.render(painter, *args)
        self._inner.render(painter, *args)
        vb = self.viewBoxF()
        if vb.isEmpty():
            vb = QRectF(QPointF(0, 0), QPointF(self.defaultSize().width(), self.defaultSize().height()))
        bounds = QRectF(args[0]) if args else QRectF(0, 0, vb.width(), vb.height())
        sx = bounds.width() / vb.width()
        sy = bounds.height() / vb.height()
        dx, dy = bounds.left(), bounds.top()
        if self.aspectRatioMode() == Qt.AspectRatioMode.KeepAspectRatio:
            s = min(sx, sy)
            dx += (bounds.width() - vb.width() * s) / 2.0
            dy += (bounds.height() - vb.height() * s) / 2.0
            sx = sy = s
        to_target = QTransform(sx, 0, 0, sy, dx - vb.left() * sx, dy - vb.top() * sy)
        device = painter.device()
        dpi = device.logicalDpiY() if device is not None and device.logicalDpiY() > 0 else 72
        world = painter.worldTransform()
        for text, x, y, st, t in self._texts:
            size = _f(st.get("font-size"), 10.0)
            if size <= 0:
                continue
            font = QFont(_family(st.get("font-family")))
            font.setPointSizeF(size * 72.0 / dpi)        # 1 SVG unit = 1 device pixel here
            weight = (st.get("font-weight") or "").lower()
            font.setBold(weight in ("bold", "bolder") or _f(weight, 400) >= 600)
            font.setItalic((st.get("font-style") or "").lower() in ("italic", "oblique"))
            opacity = _f(st.get("opacity"), 1.0) * _f(st.get("fill-opacity"), 1.0)
            anchor = st.get("text-anchor", "start")
            width = QFontMetricsF(font, device).horizontalAdvance(text) if anchor != "start" else 0.0
            shift = width / 2.0 if anchor == "middle" else width if anchor == "end" else 0.0
            painter.save()
            painter.setWorldTransform(t * to_target * world)
            painter.setFont(font)
            painter.setPen(_color(st.get("fill"), opacity))
            painter.drawText(QPointF(x - shift, y), text)
            painter.restore()


def make_text_renderer(svg_bytes, make_renderer=None):
    """A TextAsTextRenderer for *svg_bytes*, or None when it has no text."""
    if b"<text" not in bytes(svg_bytes):
        return None
    try:
        return TextAsTextRenderer(bytes(svg_bytes), make_renderer=make_renderer)
    except ET.ParseError:
        return None
