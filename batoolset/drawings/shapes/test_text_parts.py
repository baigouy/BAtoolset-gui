"""2026-11-20 (PyFigures user): a plot's title, axis labels, tick labels and legend can each
have their own size and font (publication_text_parts), over the whole plot's."""
import json

import batoolset.drawings.shapes.image2d as I


def test_parse_keeps_only_known_parts_and_values():
    raw = json.dumps({"title": {"pt": "12", "font": " Arial "}, "ticks": {"pt": 0}, "subtitle": {"pt": 9},
                      "legend": {"font": ""}})
    assert I.parse_text_parts(raw) == {"title": {"pt": 12.0, "font": "Arial"}}
    assert I.parse_text_parts(None) == {} and I.parse_text_parts("not json") == {}
    assert I.parse_text_parts({"legend": {"pt": 6}}) == {"legend": {"pt": 6.0}}


def test_each_text_is_given_its_part():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1], label="WT")
    ax.set_title("t")
    ax.set_xlabel("x")
    ax.legend()
    fig.canvas.draw()
    roles = I.text_parts(fig)
    assert roles[id(ax.title)] == "title" and roles[id(ax.xaxis.label)] == "axis_labels"
    assert roles[id(ax.get_xticklabels()[0])] == "ticks"
    assert roles[id(ax.get_legend().get_texts()[0])] == "legend"
    plt.close(fig)
