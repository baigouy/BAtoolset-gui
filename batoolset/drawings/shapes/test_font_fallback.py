"""2026-11-20, PyFigures CI on macOS: the plot's font (the label font, or the Helvetica
clone) was one matplotlib could not draw ("failed to load glyph"); fitting the plot to its
panel failed and 3 % of the panel was left empty. Such a font is replaced."""
import batoolset.drawings.shapes.image2d as I


class _Plot:
    _publication_family = I.Image2D._publication_family

    def __init__(self, family):
        self.publication_font = family
        self.img = None


def test_a_font_matplotlib_cannot_draw_falls_back(monkeypatch):
    monkeypatch.setattr(I, "_FONT_DRAWS", {"Broken Sans": False, "Arial": True})
    monkeypatch.setattr(I, "_best_helvetica_clone", lambda: "Arial")
    assert _Plot("Broken Sans")._publication_family() == "Arial"
    assert _Plot("Arial")._publication_family() == "Arial"


def test_the_label_font_is_checked_too(monkeypatch):
    monkeypatch.setattr(I, "_FONT_DRAWS", {"Helvetica": False, "Arial": True})
    monkeypatch.setattr(I, "_best_helvetica_clone", lambda: "Arial")
    monkeypatch.setattr(I, "label_text_style_source", lambda: {"family": "Helvetica", "size": 7})
    assert _Plot(I.FOLLOW_LABELS)._publication_family() == "Arial"
