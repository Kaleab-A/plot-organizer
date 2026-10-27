"""Tests for a single legend and consistent hue colours across grouped plots (issue #1)."""

import matplotlib.pyplot as plt
import pandas as pd
import pytest
from matplotlib.colors import to_rgba
from PySide6.QtWidgets import QApplication, QDialog

from plot_organizer.services.plot_service import add_hue_column, hue_color_map, hue_labels

CYCLE = plt.rcParams["axes.prop_cycle"].by_key()["color"]


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def df():
    """Group A has hue categories p, q, r; group B lacks q."""
    rows = []
    for group, hues in (("A", ["p", "q", "r"]), ("B", ["p", "r"])):
        for hue in hues:
            for subject in (1, 2):
                for x in (0, 1, 2):
                    rows.append({
                        "G": group, "H": hue, "S": subject, "x": x,
                        "y": x + ord(hue) + subject * 0.1,
                    })
    return pd.DataFrame(rows)


def _line_colors(ax):
    return {line.get_label(): line.get_color() for line in ax.lines}


def _legend_labels(ax):
    legend = ax.get_legend()
    return None if legend is None else [t.get_text() for t in legend.get_texts()]


def _make_set(df, **kwargs):
    """Create tiles for groups A and B the way MainWindow does."""
    from plot_organizer.ui.grid_board import PlotTile

    colors = hue_color_map(hue_labels(df, kwargs.get("hue", "H")))
    tiles = []
    for i, group in enumerate(["A", "B"]):
        tile = PlotTile()
        tile.set_plot(df, "x", "y", **{"hue": "H", **kwargs},
                      filter_query={"G": group}, show_legend=(i == 0), hue_colors=colors)
        tiles.append(tile)
    return tiles, colors


# --- helpers --------------------------------------------------------------

def test_hue_labels_union_sorted_as_strings(df):
    assert hue_labels(df, "H") == ["p", "q", "r"]
    assert hue_labels(df, None) == []


def test_hue_labels_numeric_sort_numerically():
    numeric = pd.DataFrame({"h": [10, 2, 1, 2]})
    assert hue_labels(numeric, "h") == ["1", "2", "10"]


def test_hue_labels_composite(df):
    labels = hue_labels(df, ["H", "G"])
    assert labels[0] == "H=p, G=A"
    assert "H=q, G=B" not in labels


def test_add_hue_column_does_not_modify_input(df):
    out, name = add_hue_column(df, ["H", "G"])
    assert name == "__composite_hue__"
    assert "__composite_hue__" not in df.columns
    assert add_hue_column(df, "H") == (df, "H")
    assert add_hue_column(df, []) == (df, None)


def test_hue_color_map_uses_cycle_in_order():
    colors = hue_color_map(["a", "b", "c"])
    assert list(colors.values()) == CYCLE[:3]


# --- tiles ----------------------------------------------------------------

def test_only_first_plot_has_legend_with_all_categories(qapp, df):
    (tile_a, tile_b), _ = _make_set(df)
    ax_a, ax_b = tile_a.figure.axes[0], tile_b.figure.axes[0]
    assert _legend_labels(ax_a) == ["p", "q", "r"]
    assert ax_b.get_legend() is None


def test_legend_lists_categories_missing_from_its_own_plot(qapp, df):
    from plot_organizer.ui.grid_board import PlotTile

    colors = hue_color_map(hue_labels(df, "H"))
    tile = PlotTile()
    tile.set_plot(df, "x", "y", hue="H", filter_query={"G": "B"}, hue_colors=colors)
    assert set(_line_colors(tile.figure.axes[0])) == {"p", "r"}
    assert _legend_labels(tile.figure.axes[0]) == ["p", "q", "r"]


def test_colours_consistent_across_set(qapp, df):
    (tile_a, tile_b), colors = _make_set(df)
    a = _line_colors(tile_a.figure.axes[0])
    b = _line_colors(tile_b.figure.axes[0])
    assert a == colors
    # 'r' keeps its colour in B even though 'q' is missing there
    assert b == {"p": colors["p"], "r": colors["r"]}
    assert b["r"] == CYCLE[2]


def test_without_colour_map_behaviour_is_unchanged(qapp, df):
    from plot_organizer.ui.grid_board import PlotTile

    tile = PlotTile()
    tile.set_plot(df, "x", "y", hue="H", filter_query={"G": "B"})
    ax = tile.figure.axes[0]
    assert _line_colors(ax) == {"p": CYCLE[0], "r": CYCLE[1]}
    assert _legend_labels(ax) == ["p", "r"]


def test_sem_fill_uses_shared_colours(qapp, df):
    (_, tile_b), colors = _make_set(df, sem_column="S")
    ax = tile_b.figure.axes[0]
    fills = [tuple(c.get_facecolor()[0]) for c in ax.collections]
    assert fills == [to_rgba(colors["p"], 0.2), to_rgba(colors["r"], 0.2)]


@pytest.mark.parametrize("precomputed", [False, True])
def test_error_bar_mode_uses_shared_colours(qapp, df, precomputed):
    (_, tile_b), colors = _make_set(
        df, sem_column="S", sem_precomputed=precomputed, style_line=False, style_marker=True
    )
    ax = tile_b.figure.axes[0]
    container_colors = {c.get_label(): c.lines[0].get_color() for c in ax.containers}
    assert container_colors == {"p": colors["p"], "r": colors["r"]}


def test_toggle_legend_keeps_other_settings(qapp, df):
    (_, tile_b), colors = _make_set(df)
    tile_b._data_filter = "x >= 1"
    tile_b._xticks = [1.0, 2.0]

    tile_b._set_show_legend(True)
    ax = tile_b.figure.axes[0]
    assert _legend_labels(ax) == ["p", "q", "r"]
    assert list(ax.get_xticks()) == [1.0, 2.0]
    assert list(ax.lines[0].get_xdata()) == [1, 2]
    assert tile_b._hue_colors == colors

    tile_b._set_show_legend(False)
    assert tile_b.figure.axes[0].get_legend() is None


def test_clear_resets_legend_state(qapp, df):
    (tile_a, _), _ = _make_set(df)
    tile_a.clear_plot()
    assert tile_a._show_legend is True
    assert tile_a._hue_colors is None


def test_serialization_round_trip(qapp, df):
    from plot_organizer.ui.grid_board import PlotTile

    (_, tile_b), colors = _make_set(df)
    data = tile_b.get_plot_data("ds1")
    assert data["show_legend"] is False
    assert data["hue_colors"] == colors

    restored = PlotTile()
    restored.set_plot_from_data(df, data)
    assert restored.figure.axes[0].get_legend() is None
    assert _line_colors(restored.figure.axes[0])["r"] == colors["r"]


def test_legacy_plot_data_keeps_legend(qapp, df):
    from plot_organizer.ui.grid_board import PlotTile

    tile = PlotTile()
    tile.set_plot_from_data(df, {"x": "x", "y": "y", "hue": "H", "filter_query": {"G": "A"}})
    assert _legend_labels(tile.figure.axes[0]) == ["p", "q", "r"]


# --- export ---------------------------------------------------------------

def test_export_respects_legend_and_colours(qapp, df):
    from plot_organizer.services.export_service import _render_plot_to_ax

    (tile_a, tile_b), colors = _make_set(df)
    fig, (ax_a, ax_b) = plt.subplots(1, 2)
    _render_plot_to_ax(tile_a, ax_a)
    _render_plot_to_ax(tile_b, ax_b)
    assert _legend_labels(ax_a) == ["p", "q", "r"]
    assert ax_b.get_legend() is None
    assert _line_colors(ax_b) == {"p": colors["p"], "r": colors["r"]}
    plt.close(fig)


def test_export_multi_column_hue_labels_match_app(qapp, df):
    from plot_organizer.services.export_service import _render_plot_to_ax
    from plot_organizer.ui.grid_board import PlotTile

    tile = PlotTile()
    tile.set_plot(df, "x", "y", hue=["H", "G"])
    fig, ax = plt.subplots()
    _render_plot_to_ax(tile, ax)
    assert _legend_labels(ax) == _legend_labels(tile.figure.axes[0])
    assert _legend_labels(ax)[0] == "H=p, G=A"
    plt.close(fig)


# --- plot creation flow ---------------------------------------------------

def _run_quick_plot(monkeypatch, df, tmp_path, selection):
    from plot_organizer.ui import main_window as mw
    from plot_organizer.services.load_service import load_csv_to_datasource

    csv = tmp_path / "data.csv"
    df.to_csv(csv, index=False)
    window = mw.MainWindow()
    ds = load_csv_to_datasource(str(csv))
    window._datasources[ds.id] = ds
    window._ds_names[ds.id] = ds.name
    window._ds_columns[ds.id] = list(ds.dataframe.columns)

    class FakeDialog:
        def __init__(self, *args, **kwargs):
            pass

        def exec(self):
            return QDialog.Accepted

        def selection(self):
            return {"datasource_id": ds.id, "x": "x", "y": "y", "sem_column": None, **selection}

    monkeypatch.setattr(mw, "QuickPlotDialog", FakeDialog)
    window._action_quick_plot()
    board = window.grid_board
    tiles = [board.tile_at(r, c) for r in range(board._rows) for c in range(board._cols)]
    return [t for t in tiles if t and not t.is_empty()]


def test_grouped_hue_plots_get_one_legend(qapp, df, tmp_path, monkeypatch):
    tiles = _run_quick_plot(monkeypatch, df, tmp_path, {"hue": ["H"], "groups": ["G"]})
    assert len(tiles) == 2
    legends = [_legend_labels(t.figure.axes[0]) for t in tiles]
    assert legends == [["H=p", "H=q", "H=r"], None]
    assert _line_colors(tiles[1].figure.axes[0])["H=r"] == CYCLE[2]


def test_single_hue_plot_keeps_legend(qapp, df, tmp_path, monkeypatch):
    tiles = _run_quick_plot(monkeypatch, df, tmp_path, {"hue": ["H"], "groups": []})
    assert len(tiles) == 1
    assert tiles[0]._hue_colors is None
    assert _legend_labels(tiles[0].figure.axes[0]) == ["H=p", "H=q", "H=r"]


def test_grouped_plots_without_hue_have_no_legend(qapp, df, tmp_path, monkeypatch):
    tiles = _run_quick_plot(monkeypatch, df, tmp_path, {"hue": None, "groups": ["G"]})
    assert len(tiles) == 2
    assert all(t.figure.axes[0].get_legend() is None for t in tiles)


# --- programmatic API -----------------------------------------------------

def test_api_grouped_plots_single_legend(df, tmp_path):
    from plot_organizer.api import create_grouped_plots

    csv = tmp_path / "data.csv"
    df.to_csv(csv, index=False)
    plots = create_grouped_plots("ds1", str(csv), x="x", y="y", groups=["G"], hue="H")
    assert [p["show_legend"] for p in plots] == [True, False]
    assert plots[0]["hue_colors"] == plots[1]["hue_colors"] == hue_color_map(["p", "q", "r"])


def test_api_defaults(df, tmp_path):
    from plot_organizer.api import create_grouped_plots, create_plot

    plot = create_plot("ds1", "x", "y", hue="H")
    assert plot["show_legend"] is True and plot["hue_colors"] is None

    csv = tmp_path / "data.csv"
    df.to_csv(csv, index=False)
    plots = create_grouped_plots("ds1", str(csv), x="x", y="y", groups=["G"])
    assert all(p["show_legend"] and p["hue_colors"] is None for p in plots)
