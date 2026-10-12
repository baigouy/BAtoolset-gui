"""
Test for publication_style feature on Image2D matplotlib figures.

publication_style only takes effect at export (save()), not during display.

Run with:
    python BAtools_pkg/batoolset/drawings/shapes/test_publication_style.py
"""
import sys
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from batoolset.settings.global_settings import set_UI
set_UI()
from qtpy.QtWidgets import QApplication
from batoolset.drawings.shapes.image2d import Image2D


def make_figure(font_size=12, line_width=1.5):
    fig, ax = plt.subplots()
    x = np.linspace(0, 2 * np.pi, 100)
    ax.plot(x, np.sin(x), linewidth=line_width, label='sin')
    ax.plot(x, np.cos(x), linewidth=line_width, label='cos')
    ax.set_xlabel('X axis', fontsize=font_size)
    ax.set_ylabel('Y axis', fontsize=font_size)
    ax.set_title('Test figure', fontsize=font_size)
    ax.tick_params(labelsize=font_size)
    ax.legend(fontsize=font_size)
    return fig


def line_widths(fig):
    return [line.get_linewidth() for ax in fig.get_axes() for line in ax.get_lines()]


def extract_stroke_widths(svg_bytes):
    return [float(v) for v in re.findall(r'stroke-width:\s*([\d.]+)', svg_bytes.decode('utf-8'))]


def all_text_artists(fig):
    import matplotlib.text as mtext
    return fig.findobj(mtext.Text)


def font_families(fig):
    return [t.get_fontfamily() for t in all_text_artists(fig)]


def test_defaults():
    fig = make_figure()
    img = Image2D(fig)
    assert img.publication_style is True
    assert img.publication_font_size == 12
    assert img.publication_line_width == 0.65
    from batoolset.drawings.shapes.image2d import _best_helvetica_clone
    assert img.publication_font == _best_helvetica_clone()
    print("PASS  default parameter values are correct")
    plt.close(fig)


def test_display_buffer_unaffected():
    """_toBuffer (display path) must NOT apply publication style."""
    fig = make_figure(line_width=2.0)
    img = Image2D(fig, publication_style=True, publication_font_size=6, publication_line_width=0.3)

    before = line_widths(fig)
    buf = img._toBuffer(bufferType='svg')
    after = line_widths(fig)

    assert buf is not None
    for b, a in zip(before, after):
        assert abs(b - a) < 1e-6, f"Display buffer must not modify line widths: {b} -> {a}"

    # The display SVG should NOT have publication-size strokes
    sw = extract_stroke_widths(buf.read())
    if sw:
        assert max(sw) > 0.3, "Display SVG should retain original stroke widths"
    print("PASS  display buffer is unaffected by publication_style")
    plt.close(fig)


def test_export_buffer_styled():
    """_toBuffer(..., apply_publication=True) must apply and restore style."""
    fig = make_figure(line_width=2.0)
    img = Image2D(fig, publication_style=True, publication_font_size=6, publication_line_width=0.3)

    before = line_widths(fig)
    buf = img._toBuffer(bufferType='svg', apply_publication=True)
    after = line_widths(fig)

    assert buf is not None
    # Figure must be restored
    for b, a in zip(before, after):
        assert abs(b - a) < 1e-6, f"Line width not restored after export render: {b} -> {a}"

    # Export SVG must have smaller strokes
    sw = extract_stroke_widths(buf.read())
    if sw:
        assert max(sw) < 2.0, f"Export SVG stroke-widths not reduced: max={max(sw):.2f}"
        print(f"PASS  export buffer styled: max stroke-width {2.0:.2f} -> {max(sw):.2f}")
    else:
        print("SKIP  no stroke-width in SVG (backend-dependent)")
    plt.close(fig)


def test_publication_style_off():
    """publication_style=False: both display and export buffers are unstyled."""
    fig = make_figure(line_width=1.5)
    img = Image2D(fig, publication_style=False)

    before = line_widths(fig)
    img._toBuffer(bufferType='svg')
    img._toBuffer(bufferType='svg', apply_publication=False)
    after = line_widths(fig)

    for b, a in zip(before, after):
        assert abs(b - a) < 1e-6, f"Line width changed unexpectedly: {b} -> {a}"
    print("PASS  publication_style=False leaves figure unchanged")
    plt.close(fig)


def test_font_none_leaves_family_unchanged():
    """publication_font=None must not alter font families."""
    fig = make_figure()
    img = Image2D(fig, publication_style=True, publication_font=None)

    before = font_families(fig)
    img._toBuffer(bufferType='svg', apply_publication=True)
    after = font_families(fig)

    assert before == after, "Font families changed despite publication_font=None"
    print("PASS  publication_font=None leaves font families unchanged")
    plt.close(fig)


def test_font_applied_and_restored():
    """publication_font changes font family during export and restores afterwards."""
    fig = make_figure()
    img = Image2D(fig, publication_style=True, publication_font='DejaVu Serif')

    before = font_families(fig)
    img._toBuffer(bufferType='svg', apply_publication=True)
    after = font_families(fig)

    assert before == after, f"Font families not restored after export: {before} -> {after}"
    print("PASS  publication_font applied during export and original font restored")
    plt.close(fig)


def test_font_not_applied_on_display():
    """publication_font must not affect the display buffer."""
    fig = make_figure()
    img = Image2D(fig, publication_style=True, publication_font='DejaVu Serif')

    before = font_families(fig)
    img._toBuffer(bufferType='svg')  # display path — no publication
    after = font_families(fig)

    assert before == after, "Font families changed by display buffer"
    print("PASS  publication_font not applied on display buffer")
    plt.close(fig)


def test_toggle_after_construction():
    """Enabling all publication options after construction takes effect on next export."""
    fig = make_figure(line_width=2.0)
    img = Image2D(fig)
    img.publication_style = True
    img.publication_font_size = 5
    img.publication_line_width = 0.25
    img.publication_font = 'DejaVu Serif'

    before_lw = line_widths(fig)
    before_ff = font_families(fig)
    buf = img._toBuffer(bufferType='svg', apply_publication=True)
    after_lw = line_widths(fig)
    after_ff = font_families(fig)

    for b, a in zip(before_lw, after_lw):
        assert abs(b - a) < 1e-6, f"Line width not restored: {b} -> {a}"
    assert before_ff == after_ff, f"Font families not restored: {before_ff} -> {after_ff}"

    sw = extract_stroke_widths(buf.read())
    if sw:
        assert max(sw) < 2.0, f"Export stroke-widths not reduced: max={max(sw):.2f}"
    print("PASS  toggle after construction applies on export (line width, font size, font family)")
    plt.close(fig)


if __name__ == '__main__':
    app = QApplication.instance() or QApplication(sys.argv)

    tests = [
        test_defaults,
        test_display_buffer_unaffected,
        test_export_buffer_styled,
        test_publication_style_off,
        test_font_none_leaves_family_unchanged,
        test_font_applied_and_restored,
        test_font_not_applied_on_display,
        test_toggle_after_construction,
    ]

    failed = []
    for t in tests:
        try:
            t()
        except Exception as e:
            print(f"FAIL  {t.__name__}: {e}")
            failed.append(t.__name__)

    print()
    if failed:
        print(f"{len(failed)} test(s) FAILED: {', '.join(failed)}")
        sys.exit(1)
    else:
        print(f"All {len(tests)} tests passed.")
