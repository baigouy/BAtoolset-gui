"""Draws the SVG that PyMuPDF writes for a PDF page, clipping included.

A PDF placed as a figure panel is converted to SVG (PyMuPDF
``page.get_svg_image``) and drawn as vectors. Qt 6.4's SVG renderer ignores
``clipPath``, so a plot curve leaving its axes would be drawn over the whole
figure, and Qt 6.4's SVG *writer* drops painter clipping as well.

``PdfSvgRenderer`` is a QSvgRenderer (Image2D and the exports only need
``render``, ``defaultSize`` and the aspect-ratio mode) whose ``render`` walks
the small SVG subset PyMuPDF produces itself: groups, paths, glyph ``use``
references, images and clip paths, with matrix transforms. Clipping is done by
the painter for PDF and raster output, and geometrically (path intersection,
strokes turned into outlines) when the painter writes SVG. Anything outside
that subset (gradients, masks, patterns...) falls back to QSvgRenderer.
"""
from __future__ import annotations

import base64
import re
import xml.etree.ElementTree as ET

from qtpy.QtCore import QByteArray, QPointF, QRectF, Qt
from qtpy.QtGui import (QBrush, QColor, QImage, QPaintEngine, QPainter, QPainterPath,
                        QPainterPathStroker, QPen, QTransform)
from qtpy.QtSvg import QSvgRenderer

_SVG = '{http://www.w3.org/2000/svg}'
_XLINK = '{http://www.w3.org/1999/xlink}href'
_SUPPORTED = {'svg', 'defs', 'g', 'path', 'use', 'clipPath', 'image', 'title', 'desc', 'metadata'}
_INHERITED = ('fill', 'fill-opacity', 'fill-rule', 'stroke', 'stroke-width', 'stroke-opacity',
              'stroke-linecap', 'stroke-linejoin', 'stroke-miterlimit', 'stroke-dasharray')
_NUM = re.compile(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')
_CMD = re.compile(r'[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')


def _tag(el):
    return el.tag.split('}', 1)[-1]


def parse_transform(text):
    """SVG transform list -> QTransform (matrix, translate, scale, rotate)."""
    t = QTransform()
    if not text:
        return t
    for name, args in re.findall(r'(\w+)\s*\(([^)]*)\)', text):
        v = [float(x) for x in _NUM.findall(args)]
        if name == 'matrix' and len(v) == 6:
            m = QTransform(v[0], v[1], v[2], v[3], v[4], v[5])
        elif name == 'translate' and v:
            m = QTransform.fromTranslate(v[0], v[1] if len(v) > 1 else 0.0)
        elif name == 'scale' and v:
            m = QTransform.fromScale(v[0], v[1] if len(v) > 1 else v[0])
        elif name == 'rotate' and v:
            m = QTransform()
            if len(v) == 3:
                m.translate(v[1], v[2])
            m.rotate(v[0])
            if len(v) == 3:
                m.translate(-v[1], -v[2])
        else:
            continue
        # in SVG the leftmost transform is applied last
        t = m * t
    return t


def parse_path(d):
    """SVG path data -> QPainterPath (arcs are drawn as straight segments)."""
    path = QPainterPath()
    tokens = _CMD.findall(d or '')
    i = 0
    cmd = None
    cur = QPointF(0, 0)
    start = QPointF(0, 0)
    last_ctrl = None
    last_cmd = ''

    def num():
        nonlocal i
        v = float(tokens[i])
        i += 1
        return v

    while i < len(tokens):
        if tokens[i].isalpha():
            cmd = tokens[i]
            i += 1
            if cmd in 'Zz':
                path.closeSubpath()
                cur = QPointF(start)
                last_cmd = cmd
                continue
        if cmd is None:
            break
        rel = cmd.islower()
        c = cmd.upper()
        base = cur if rel else QPointF(0, 0)
        try:
            if c == 'M':
                cur = QPointF(base.x() + num(), base.y() + num())
                path.moveTo(cur)
                start = QPointF(cur)
                cmd = 'l' if rel else 'L'      # further pairs are line-tos
            elif c == 'L':
                cur = QPointF(base.x() + num(), base.y() + num())
                path.lineTo(cur)
            elif c == 'H':
                cur = QPointF((cur.x() if rel else 0.0) + num(), cur.y())
                path.lineTo(cur)
            elif c == 'V':
                cur = QPointF(cur.x(), (cur.y() if rel else 0.0) + num())
                path.lineTo(cur)
            elif c == 'C':
                c1 = QPointF(base.x() + num(), base.y() + num())
                c2 = QPointF(base.x() + num(), base.y() + num())
                cur = QPointF(base.x() + num(), base.y() + num())
                path.cubicTo(c1, c2, cur)
                last_ctrl = c2
            elif c == 'S':
                c1 = (cur * 2 - last_ctrl) if last_ctrl is not None and last_cmd in 'CcSs' else QPointF(cur)
                c2 = QPointF(base.x() + num(), base.y() + num())
                cur = QPointF(base.x() + num(), base.y() + num())
                path.cubicTo(c1, c2, cur)
                last_ctrl = c2
            elif c == 'Q':
                c1 = QPointF(base.x() + num(), base.y() + num())
                cur = QPointF(base.x() + num(), base.y() + num())
                path.quadTo(c1, cur)
                last_ctrl = c1
            elif c == 'T':
                c1 = (cur * 2 - last_ctrl) if last_ctrl is not None and last_cmd in 'QqTt' else QPointF(cur)
                cur = QPointF(base.x() + num(), base.y() + num())
                path.quadTo(c1, cur)
                last_ctrl = c1
            elif c == 'A':
                for _ in range(5):
                    num()
                cur = QPointF(base.x() + num(), base.y() + num())
                path.lineTo(cur)
            else:
                break
        except (IndexError, ValueError):
            break
        last_cmd = cmd
    return path


def _color(value, opacity):
    if value is None or value == 'none':
        return None
    col = QColor(value)
    if not col.isValid():
        return None
    col.setAlphaF(max(0.0, min(1.0, opacity)))
    return col


def _float(value, default):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class PdfSvgRenderer(QSvgRenderer):
    """QSvgRenderer for PyMuPDF's SVG output, with working clip paths."""

    def __init__(self, svg_bytes):
        super().__init__(QByteArray(svg_bytes))
        root = ET.fromstring(svg_bytes)
        self._root = root
        self._ids = {el.get('id'): el for el in root.iter() if el.get('id')}
        vb = [float(x) for x in _NUM.findall(root.get('viewBox') or '')]
        if len(vb) == 4 and vb[2] > 0 and vb[3] > 0:
            self._view_box = QRectF(*vb)
        else:
            self._view_box = QRectF(0, 0, _float(root.get('width'), 100.0), _float(root.get('height'), 100.0))
        self._path_cache = {}
        self._image_cache = {}

    @staticmethod
    def supports(svg_bytes):
        """True if every element of the SVG is in the subset drawn here."""
        try:
            root = ET.fromstring(svg_bytes)
        except ET.ParseError:
            return False
        return all(_tag(el) in _SUPPORTED for el in root.iter())

    # -- QSvgRenderer API used by PyFigures ---------------------------------
    def render(self, painter, *args):
        if len(args) == 1 and isinstance(args[0], str):        # render(painter, elementId)
            return super().render(painter, *args)
        if len(args) >= 2:                                      # render(painter, elementId, bounds)
            return super().render(painter, *args)
        bounds = QRectF(args[0]) if args else QRectF(QPointF(0, 0), QSizeF_from(self.defaultSize()))
        vb = self._view_box
        sx = bounds.width() / vb.width()
        sy = bounds.height() / vb.height()
        dx, dy = bounds.left(), bounds.top()
        if self.aspectRatioMode() == Qt.AspectRatioMode.KeepAspectRatio:
            s = min(sx, sy)
            dx += (bounds.width() - vb.width() * s) / 2.0
            dy += (bounds.height() - vb.height() * s) / 2.0
            sx = sy = s
        to_bounds = QTransform(sx, 0, 0, sy, dx - vb.left() * sx, dy - vb.top() * sy)
        engine = painter.paintEngine()
        geometric = engine is not None and engine.type() == QPaintEngine.Type.SVG
        painter.save()
        try:
            base = painter.worldTransform()
            self._geometric = geometric
            self._base = base
            for child in self._root:
                self._draw(painter, child, to_bounds, {}, None, 1.0)
        finally:
            painter.restore()

    # -- drawing ---------------------------------------------------------------
    def _clip_path(self, ref, user_to_base):
        m = re.match(r'url\(#([^)]+)\)', ref or '')
        el = self._ids.get(m.group(1)) if m else None
        if el is None:
            return None
        out = QPainterPath()
        out.setFillRule(Qt.FillRule.WindingFill)
        for child in el:
            if _tag(child) != 'path':
                continue
            p = parse_path(child.get('d'))
            if child.get('clip-rule') == 'evenodd' or child.get('fill-rule') == 'evenodd':
                p.setFillRule(Qt.FillRule.OddEvenFill)
            t = parse_transform(child.get('transform')) * user_to_base
            out = out.united(t.map(p)) if not out.isEmpty() else t.map(p)
        nested = el.get('clip-path')
        if nested:
            inner = self._clip_path(nested, user_to_base)
            if inner is not None:
                out = out.intersected(inner)
        return out

    def _draw(self, painter, el, user_to_base, style, clip, opacity):
        tag = _tag(el)
        if tag in ('defs', 'clipPath', 'title', 'desc', 'metadata'):
            return
        style = dict(style)
        for key in _INHERITED:
            if el.get(key) is not None:
                style[key] = el.get(key)
        opacity *= _float(el.get('opacity'), 1.0)
        t = parse_transform(el.get('transform')) * user_to_base
        if el.get('clip-path'):
            new_clip = self._clip_path(el.get('clip-path'), t)
            if new_clip is not None:
                clip = new_clip if clip is None else clip.intersected(new_clip)
        if tag in ('g', 'svg'):
            for child in el:
                self._draw(painter, child, t, style, clip, opacity)
        elif tag == 'use':
            ref = (el.get(_XLINK) or el.get('href') or '').lstrip('#')
            target = self._ids.get(ref)
            if target is not None:
                shift = QTransform.fromTranslate(_float(el.get('x'), 0.0), _float(el.get('y'), 0.0))
                self._draw(painter, target, shift * t, style, clip, opacity)
        elif tag == 'path':
            d = el.get('d')
            path = self._path_cache.get(d)
            if path is None:
                path = parse_path(d)
                self._path_cache[d] = path
            if style.get('fill-rule') == 'evenodd':
                path = QPainterPath(path)
                path.setFillRule(Qt.FillRule.OddEvenFill)
            self._paint_path(painter, path, t, style, clip, opacity)
        elif tag == 'image':
            self._paint_image(painter, el, t, clip, opacity)

    def _pen(self, style, opacity):
        col = _color(style.get('stroke'), _float(style.get('stroke-opacity'), 1.0) * opacity)
        if col is None:
            return None
        pen = QPen(col)
        pen.setWidthF(_float(style.get('stroke-width'), 1.0))
        pen.setCapStyle({'round': Qt.PenCapStyle.RoundCap, 'square': Qt.PenCapStyle.SquareCap}
                        .get(style.get('stroke-linecap'), Qt.PenCapStyle.FlatCap))
        pen.setJoinStyle({'round': Qt.PenJoinStyle.RoundJoin, 'bevel': Qt.PenJoinStyle.BevelJoin}
                         .get(style.get('stroke-linejoin'), Qt.PenJoinStyle.SvgMiterJoin))
        pen.setMiterLimit(_float(style.get('stroke-miterlimit'), 4.0))
        dashes = [x for x in (_float(v, None) for v in _NUM.findall(style.get('stroke-dasharray') or ''))
                  if x is not None]
        if dashes and any(dashes) and pen.widthF() > 0:
            if len(dashes) % 2:
                dashes = dashes * 2
            pen.setDashPattern([max(1e-3, x / pen.widthF()) for x in dashes])
        return pen

    def _paint_path(self, painter, path, t, style, clip, opacity):
        fill = _color(style.get('fill', '#000000'), _float(style.get('fill-opacity'), 1.0) * opacity)
        pen = self._pen(style, opacity)
        if fill is None and pen is None:
            return
        if not self._geometric:
            painter.save()
            painter.setWorldTransform(self._base)
            if clip is not None:
                painter.setClipPath(clip, Qt.ClipOperation.IntersectClip)
            painter.setWorldTransform(t * self._base)
            painter.setBrush(QBrush(fill) if fill is not None else Qt.BrushStyle.NoBrush)
            painter.setPen(pen if pen is not None else Qt.PenStyle.NoPen)
            painter.drawPath(path)
            painter.restore()
            return
        # SVG output: Qt 6.4's SVG writer drops clipping, so clip the geometry
        painter.save()
        painter.setWorldTransform(self._base)
        painter.setPen(Qt.PenStyle.NoPen)
        if fill is not None:
            area = t.map(path)
            if clip is not None and not clip.contains(area.boundingRect()):
                area = area.intersected(clip)
            painter.setBrush(QBrush(fill))
            painter.drawPath(area)
        if pen is not None:
            if clip is None or clip.contains(t.map(path).boundingRect().adjusted(
                    -pen.widthF(), -pen.widthF(), pen.widthF(), pen.widthF())):
                painter.setWorldTransform(t * self._base)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(pen)
                painter.drawPath(path)
            else:
                stroker = QPainterPathStroker(pen)
                outline = t.map(stroker.createStroke(path)).intersected(clip)
                painter.setBrush(QBrush(pen.color()))
                painter.drawPath(outline)
        painter.restore()

    def _paint_image(self, painter, el, t, clip, opacity):
        href = el.get(_XLINK) or el.get('href') or ''
        img = self._image_cache.get(href)
        if img is None:
            m = re.match(r'data:image/[^;]+;base64,(.*)', href, re.S)
            if not m:
                return
            img = QImage.fromData(base64.b64decode(re.sub(r'\s', '', m.group(1))))
            self._image_cache[href] = img
        if img.isNull():
            return
        rect = QRectF(_float(el.get('x'), 0.0), _float(el.get('y'), 0.0),
                      _float(el.get('width'), img.width()), _float(el.get('height'), img.height()))
        painter.save()
        painter.setWorldTransform(self._base)
        if clip is not None:
            if self._geometric:
                # an SVG writer cannot clip an image: keep the clip's bounding box
                visible = t.mapRect(rect).intersected(clip.boundingRect())
                if visible.isEmpty():
                    painter.restore()
                    return
            else:
                painter.setClipPath(clip, Qt.ClipOperation.IntersectClip)
        painter.setWorldTransform(t * self._base)
        painter.setOpacity(painter.opacity() * opacity)
        painter.drawImage(rect, img, QRectF(img.rect()))
        painter.restore()


def QSizeF_from(size):
    from qtpy.QtCore import QSizeF
    return QSizeF(size.width(), size.height())


def make_pdf_svg_renderer(svg_bytes):
    """PdfSvgRenderer if the SVG is in the subset it draws, else QSvgRenderer."""
    if PdfSvgRenderer.supports(svg_bytes):
        return PdfSvgRenderer(svg_bytes)
    return QSvgRenderer(QByteArray(svg_bytes))
