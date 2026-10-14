"""Clip paths for ordinary SVG files drawn with Qt (Qt 6.4-6.11 ignore them).

``ClippingSvgRenderer`` is a QSvgRenderer for SVG files that use
``clip-path`` (Inkscape, Illustrator and plotting libraries write them often):
it draws the document element by element in document order, with Qt's own
renderer for each element (``render(painter, id, bounds)`` keeps the parents'
styles and transforms), and sets the clip itself around every element that
references a ``<clipPath>``. Elements without clipping inside are drawn whole.

Output: PDF / raster painters clip natively, so everything stays vector.
Figure SVG exports do not draw panels through this renderer: they embed the
panel's SVG source as is (batoolset.drawings.svg_embed). Only when some other
code draws it to an SVG painter (Qt's SVG writer drops clipping) is each
clipped element drawn as an image (600 dpi at the drawn size), clipped;
everything else stays vector.

``make_svg_renderer(path_or_bytes)`` returns a plain QSvgRenderer for SVGs
without clip paths.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from qtpy.QtCore import QByteArray, QPointF, QRectF, Qt
from qtpy.QtGui import QColor, QImage, QPaintEngine, QPainter, QPainterPath, QPolygonF, QTransform
from qtpy.QtSvg import QSvgRenderer

from batoolset.drawings.pdf_svg_renderer import parse_path, parse_transform

_SVG_NS = "http://www.w3.org/2000/svg"
_NOT_DRAWN = {"defs", "clipPath", "mask", "title", "desc", "metadata", "style", "script",
              "linearGradient", "radialGradient", "pattern", "marker", "symbol", "filter",
              "font", "font-face", "namedview", "sodipodi:namedview"}
_URL = re.compile(r"url\(\s*#([^)\s]+)\s*\)")
_NUM = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
SVG_OUTPUT_DPI = 600     # more than any journal asks for
SVG_OUTPUT_MAX_PIXELS = 40_000_000      # per clipped element (an A4 page at 600 dpi is 35 MP)


def _tag(el):
    return el.tag.split("}", 1)[-1]


def _clip_ref(el):
    ref = el.get("clip-path")
    if ref is None:
        m = re.search(r"clip-path\s*:\s*([^;]+)", el.get("style") or "")
        ref = m.group(1) if m else None
    m = _URL.search(ref or "")
    return m.group(1) if m else None


def _f(v, d=0.0):
    try:
        return float(_NUM.match(str(v).strip()).group(0))
    except (AttributeError, TypeError, ValueError):
        return d


def _shape_path(el):
    """QPainterPath of a basic shape / path element, in its own user space."""
    tag = _tag(el)
    p = QPainterPath()
    if tag == "path":
        p = parse_path(el.get("d"))
    elif tag == "rect":
        rx, ry = _f(el.get("rx")), _f(el.get("ry"))
        r = QRectF(_f(el.get("x")), _f(el.get("y")), _f(el.get("width")), _f(el.get("height")))
        if rx or ry:
            p.addRoundedRect(r, rx or ry, ry or rx)
        else:
            p.addRect(r)
    elif tag == "circle":
        r = _f(el.get("r"))
        p.addEllipse(QPointF(_f(el.get("cx")), _f(el.get("cy"))), r, r)
    elif tag == "ellipse":
        p.addEllipse(QPointF(_f(el.get("cx")), _f(el.get("cy"))), _f(el.get("rx")), _f(el.get("ry")))
    elif tag in ("polygon", "polyline"):
        v = [float(x) for x in _NUM.findall(el.get("points") or "")]
        if len(v) >= 4:
            p.addPolygon(QPolygonF([QPointF(v[i], v[i + 1]) for i in range(0, len(v) - 1, 2)]))
            if tag == "polygon":
                p.closeSubpath()
    if (el.get("clip-rule") or el.get("fill-rule")) == "evenodd":
        p.setFillRule(Qt.FillRule.OddEvenFill)
    return p


class ClippingSvgRenderer(QSvgRenderer):
    """QSvgRenderer that honours clip-path (see the module docstring)."""

    def __init__(self, svg_bytes):
        root = ET.fromstring(svg_bytes)
        n = 0
        for el in root.iter():                    # every element needs an id to be drawn alone
            if el.get("id") is None and isinstance(el.tag, str):
                el.set("id", f"__pyf_el_{n}")
                n += 1
        ET.register_namespace("", _SVG_NS)
        ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
        data = ET.tostring(root)
        super().__init__(QByteArray(data))
        self._root = root
        self._ids = {el.get("id"): el for el in root.iter() if el.get("id")}
        self._clipped_below = {}
        self._mark(root)

    def _mark(self, el):
        """True if *el* or a descendant references a clip path. Memoised per
        element: whether a *descendant* (not *el* itself) does."""
        below = False
        for child in el:
            below = self._mark(child) or below
        self._clipped_below[el.get("id")] = below
        return below or _clip_ref(el) is not None

    @staticmethod
    def needed(svg_bytes) -> bool:
        return b"clip-path" in svg_bytes

    # -- geometry --------------------------------------------------------------
    def _doc_rect(self, el_id):
        """The element's bounds in document (viewBox) coordinates."""
        return self.transformForElement(el_id).mapRect(self.boundsOnElement(el_id))

    def _clip_in_doc(self, el):
        """The clip path *el* references, in document coordinates, or None."""
        cp = self._ids.get(_clip_ref(el))
        if cp is None:
            return None
        # userSpaceOnUse: the referencing element's user space = parents x own transform
        user = parse_transform(el.get("transform")) * self.transformForElement(el.get("id"))
        units_box = cp.get("clipPathUnits") == "objectBoundingBox"
        box = self.boundsOnElement(el.get("id")) if units_box else None
        out = QPainterPath()
        for child in cp:
            p = _shape_path(child)
            if p.isEmpty():
                continue
            t = parse_transform(child.get("transform"))
            if box is not None:
                t = t * QTransform(box.width(), 0, 0, box.height(), box.left(), box.top())
            out = out.united((t * user).map(p)) if not out.isEmpty() else (t * user).map(p)
        nested = self._ids.get(_clip_ref(cp)) if _clip_ref(cp) else None
        if nested is not None and not out.isEmpty():
            inner = self._clip_in_doc(cp)
            if inner is not None:
                out = out.intersected(inner)
        return out

    # -- drawing ----------------------------------------------------------------
    def render(self, painter, *args):
        if len(args) == 1 and isinstance(args[0], str):
            return super().render(painter, *args)
        if len(args) >= 2:
            return super().render(painter, *args)
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
        self._to_target = QTransform(sx, 0, 0, sy, dx - vb.left() * sx, dy - vb.top() * sy)
        engine = painter.paintEngine()
        self._svg_output = engine is not None and engine.type() == QPaintEngine.Type.SVG
        painter.save()
        try:
            for child in self._root:
                self._draw(painter, child, None)
        finally:
            painter.restore()

    def _draw(self, painter, el, clip):
        if not isinstance(el.tag, str) or _tag(el) in _NOT_DRAWN:
            return
        el_id = el.get("id")
        if _clip_ref(el) is not None:
            own = self._clip_in_doc(el)
            if own is not None:
                clip = own if clip is None else clip.intersected(own)
        if self._clipped_below.get(el_id) and len(el):
            # a clipped element deeper inside: draw the children one by one,
            # each inside this element's own clip (if any) and theirs
            for child in el:
                self._draw(painter, child, clip)
            return
        if not self.elementExists(el_id):
            return
        rect = self._doc_rect(el_id)
        if rect.isEmpty() and rect.width() == 0 and rect.height() == 0:
            return
        target = self._to_target.mapRect(rect)
        if clip is None:
            super().render(painter, el_id, target)
        elif not self._svg_output:
            painter.save()
            painter.setClipPath(self._to_target.map(clip), Qt.ClipOperation.IntersectClip)
            super().render(painter, el_id, target)
            painter.restore()
        else:
            self._draw_as_image(painter, el_id, target, self._to_target.map(clip))

    def _draw_as_image(self, painter, el_id, target, clip):
        """SVG output: the clipped element as an image of its visible part."""
        visible = target.intersected(clip.boundingRect())
        if visible.isEmpty():
            return
        scale = SVG_OUTPUT_DPI / 72.0
        if visible.width() * visible.height() * scale * scale > SVG_OUTPUT_MAX_PIXELS:
            scale = (SVG_OUTPUT_MAX_PIXELS / (visible.width() * visible.height())) ** 0.5
        img = QImage(max(1, int(round(visible.width() * scale))), max(1, int(round(visible.height() * scale))),
                     QImage.Format.Format_ARGB32_Premultiplied)
        img.fill(QColor(0, 0, 0, 0))
        p = QPainter(img)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.scale(img.width() / visible.width(), img.height() / visible.height())
        p.translate(-visible.left(), -visible.top())
        p.setClipPath(clip)
        super().render(p, el_id, target)
        p.end()
        painter.drawImage(visible, img, QRectF(img.rect()))


def make_svg_renderer(source):
    """ClippingSvgRenderer for an SVG with clip paths, else QSvgRenderer.
    *source*: a file path or the SVG bytes."""
    data = source
    if isinstance(source, str):
        with open(source, "rb") as f:
            data = f.read()
    if isinstance(data, (bytes, bytearray)) and ClippingSvgRenderer.needed(bytes(data)):
        try:
            return ClippingSvgRenderer(bytes(data))
        except ET.ParseError:
            pass
    return QSvgRenderer(QByteArray(bytes(data)) if isinstance(data, (bytes, bytearray)) else source)
