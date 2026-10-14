"""SVG export of vector panels without Qt's SVG writer losing anything.

Qt draws an SVG panel (an SVG file, a PDF page, a Matplotlib plot) into an SVG
export through QSvgRenderer -> QSvgGenerator: text becomes outlines and clip
paths are lost (clipped elements had to be rasterised). Instead, while a
figure is exported to SVG inside ``collecting()``, each vector panel draws a
placeholder rectangle in a unique colour (``place``); once Qt has written the
file, ``embed(svg_text)`` replaces every placeholder by the panel's own SVG
source: its elements, clip paths and <text> unchanged, under the placeholder's
transform, fitted like QSvgRenderer fits it, clipped to the panel by an SVG
clipPath, with ids prefixed so nothing clashes.
"""
from __future__ import annotations

import contextlib
import re
import xml.etree.ElementTree as ET

from qtpy.QtCore import QRectF
from qtpy.QtGui import QColor, QPaintEngine, QPolygonF

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
_ACTIVE = []
_SKIP = {"title", "desc", "metadata", "script"}
_ROOT_ONLY = {"width", "height", "viewBox", "x", "y", "id", "version", "baseProfile",
              "preserveAspectRatio", "zoomAndPan", "contentScriptType", "contentStyleType"}


def active():
    """The collector of the SVG export in progress, or None."""
    return _ACTIVE[-1] if _ACTIVE else None


def wants(painter):
    """True if *painter* writes SVG for an export that embeds vector panels."""
    try:
        return active() is not None and painter.paintEngine().type() == QPaintEngine.Type.SVG
    except Exception:
        return False


@contextlib.contextmanager
def collecting():
    """While active, vector panels drawn to an SVG painter become placeholders
    (see module docstring). Yields the collector; call collector.embed(text)."""
    collector = SvgEmbedCollector()
    _ACTIVE.append(collector)
    try:
        yield collector
    finally:
        _ACTIVE.remove(collector)


def _xml_attr(value):
    return (str(value).replace("&", "&amp;").replace('"', "&quot;")
            .replace("<", "&lt;").replace(">", "&gt;"))


def _tag(el):
    return el.tag.rsplit("}", 1)[-1]


def _prefixed_svg(svg_bytes, prefix):
    """(view box (x, y, w, h), serialized children of the root) with every id
    and reference to it prefixed."""
    ET.register_namespace("", SVG_NS)
    ET.register_namespace("xlink", XLINK_NS)
    root = ET.fromstring(svg_bytes)
    vb = root.get("viewBox")
    if vb:
        x, y, w, h = (float(v) for v in vb.replace(",", " ").split())
    else:
        def num(v, default):
            m = re.match(r"\s*([-+]?[\d.]+(?:[eE][-+]?\d+)?)", v or "")
            return float(m.group(1)) if m else default
        x, y, w, h = 0.0, 0.0, num(root.get("width"), 100.0), num(root.get("height"), 100.0)
    ids = {el.get("id") for el in root.iter() if el.get("id")}

    def fix_refs(value):
        value = re.sub(r"url\(\s*#([^)\s]+)\s*\)",
                       lambda m: f"url(#{prefix}{m.group(1)})" if m.group(1) in ids else m.group(0), value)
        return value

    for el in root.iter():
        for k, v in list(el.attrib.items()):
            if k == "id":
                el.set(k, prefix + v)
            elif k in ("href", f"{{{XLINK_NS}}}href") and v.startswith("#") and v[1:] in ids:
                el.set(k, "#" + prefix + v[1:])
            elif "url(" in v:
                el.set(k, fix_refs(v))
        if _tag(el) == "style" and el.text:
            if re.search(r"(^|[}\s])\*\s*\{", el.text):
                el.text = ""                   # a universal rule would restyle the whole document
            else:
                el.text = fix_refs(el.text)
    parts = [ET.tostring(child, encoding="unicode") for child in root if _tag(child) not in _SKIP]
    # the root's own presentation attributes (fill, font, style...) still apply
    root_attrs = {k: v for k, v in root.attrib.items()
                  if "}" not in k and k not in _ROOT_ONLY}
    return (x, y, w, h), "".join(parts), root_attrs


class SvgEmbedCollector:
    def __init__(self):
        self.items = []              # (marker, svg bytes, placements)
        self._by_source = {}

    def place(self, painter, target, svg_bytes, clip=None, keep_aspect=True):
        """Draw a placeholder for *svg_bytes* fitted into *target* (current
        painter coordinates), visible inside *clip* (a QRectF or QPolygonF,
        same coordinates; default *target*)."""
        key = id(svg_bytes), len(svg_bytes)
        if key not in self._by_source:
            index = len(self.items)
            marker = "#fd%02x%02x" % (1 + index // 250, 1 + index % 250)
            self._by_source[key] = index
            self.items.append((marker, bytes(svg_bytes), []))
        marker, _, placements = self.items[self._by_source[key]]
        poly = QPolygonF(QRectF(clip if isinstance(clip, QRectF) else target)) \
            if not isinstance(clip, QPolygonF) else QPolygonF(clip)
        placements.append((QRectF(target), poly, keep_aspect, painter.opacity()))
        painter.save()
        painter.setOpacity(1.0)
        painter.fillRect(QRectF(target), QColor(marker))
        painter.restore()

    def embed(self, svg_text):
        """Replace the placeholders in the written SVG *svg_text*."""
        n = 0
        for k, (marker, source, placements) in enumerate(self.items):
            if not placements:
                continue
            (vx, vy, vw, vh), inner, root_attrs = _prefixed_svg(source, f"pyfp{k}_")
            attrs = {"fill": "#000000", "stroke": "none", **root_attrs}
            attr_text = "".join(f' {a}="{_xml_attr(v)}"' for a, v in attrs.items())
            pattern = re.compile(r'(<g fill="' + re.escape(marker) + r'"[^>]*>\s*)<rect [^>]*/>', re.I)

            def swap(m):
                nonlocal n
                if not placements:
                    return m.group(0)
                target, poly, keep_aspect, opacity = placements.pop(0)
                n += 1
                sx = target.width() / vw
                sy = target.height() / vh
                dx, dy = target.x(), target.y()
                if keep_aspect:
                    s = min(sx, sy)
                    dx += (target.width() - vw * s) / 2.0
                    dy += (target.height() - vh * s) / 2.0
                    sx = sy = s
                pts = " ".join(f"{p.x():g},{p.y():g}" for p in poly)
                cid = f"pyfpclip{n}"
                group = re.sub(r'fill="' + re.escape(marker) + '"', 'fill="none"', m.group(1), flags=re.I)
                op = f' opacity="{opacity:g}"' if opacity < 1 else ""
                return (group
                        + f'<defs><clipPath id="{cid}"><polygon points="{pts}"/></clipPath></defs>'
                        + f'<g clip-path="url(#{cid})"{op}><g{attr_text} '
                          f'transform="matrix({sx:g},0,0,{sy:g},{dx - vx * sx:g},{dy - vy * sy:g})">'
                        + inner + "</g></g>")

            svg_text = pattern.sub(swap, svg_text)
        return svg_text
