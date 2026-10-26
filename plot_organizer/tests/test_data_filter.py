"""Tests for pre-plot data filtering (pandas query expressions)."""

import numpy as np
import pandas as pd
import pytest
from PySide6.QtWidgets import QApplication

from plot_organizer.services.filter_service import (
    FilterError,
    apply_data_filter,
    apply_filters,
    column_kind,
    filter_warnings,
)
from plot_organizer.services.plot_service import expand_groups, shared_limits


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def df():
    return pd.DataFrame({
        "time": [-1.0, -0.5, 0.0, 0.5, 1.0],
        "value": [10.0, 20.0, 30.0, 40.0, 50.0],
        "Country": ["USA", "Canada", "USA", None, "Mexico"],
        "Number of employees": [10, 5000, 7000, 20, 9000],
        "Dim": ["1", "2", "3", "All", "1"],
        "n_features": [22, 20, 22, 21, 22],
        "date": ["2023-12-30", "2024-01-01", "2024-02-15", None, "2025-03-01"],
        "usdate": ["12/30/2023", "1/1/2024", "2/15/2024", "3/3/2024", "3/1/2025"],
        "flag": [True, False, True, False, True],
        "loss_gain": ["-1.0_2.0", "0.5_1.0", "-1.0_2.0", "0.5_1.0", "-1.0_2.0"],
    })


# --- column kinds ---------------------------------------------------------

def test_column_kinds(df):
    assert column_kind(df["time"]) == "numeric"
    assert column_kind(df["n_features"]) == "numeric"
    assert column_kind(df["Country"]) == "text"
    assert column_kind(df["Dim"]) == "text"
    assert column_kind(df["date"]) == "datetime"
    assert column_kind(df["usdate"]) == "datetime"
    assert column_kind(df["flag"]) == "boolean"
    # Contains '-' but is not a date
    assert column_kind(df["loss_gain"]) == "text"
    # Plain years are numbers, not dates
    assert column_kind(pd.Series(["1988", "2018", "2000"])) == "text"


# --- applying filters -----------------------------------------------------

@pytest.mark.parametrize("expr, expected", [
    ("time >= 0", [2, 3, 4]),
    ('Country == "USA"', [0, 2]),
    ('Country in ["USA", "Mexico"]', [0, 2, 4]),
    ("`Number of employees` > 1000", [1, 2, 4]),
    ('(time >= 0 and Country == "USA") or not flag', [1, 2, 3]),
    ('Country.str.contains("an")', [1]),
    ('Country.str.contains("USA", case=False)', [0, 2]),
    ("Country.isna()", [3]),
    ("time.between(-0.5, 0.5)", [1, 2, 3]),
    ("abs(time) < 0.6", [1, 2, 3]),
    ('Dim == "1"', [0, 4]),
    ('loss_gain == "-1.0_2.0"', [0, 2, 4]),
    ("flag", [0, 2, 4]),
    ("time\n>= 0", [2, 3, 4]),
])
def test_apply_data_filter(df, expr, expected):
    assert list(apply_data_filter(df, expr).index) == expected


@pytest.mark.parametrize("expr, expected", [
    ('date >= "2024-01-01"', [1, 2, 4]),
    # Non-ISO dates compare chronologically, not as strings
    ('usdate >= "2024-01-01"', [1, 2, 3, 4]),
    ("usdate.dt.year == 2024", [1, 2, 3]),
])
def test_date_text_columns_compare_as_dates(df, expr, expected):
    out = apply_data_filter(df, expr)
    assert list(out.index) == expected
    # The stored column is left as text
    assert out["usdate"].dtype == object
    assert df["usdate"].dtype == object


def test_blank_filter_returns_same_dataframe(df):
    assert apply_data_filter(df, None) is df
    assert apply_data_filter(df, "   \n ") is df


def test_filter_preserves_dtypes(df):
    out = apply_data_filter(df, "time >= 0")
    assert (out.dtypes == df.dtypes).all()


def test_apply_filters_combines_data_filter_and_group_query(df):
    out = apply_filters(df, "time >= -0.5", {"Country": "USA"})
    assert list(out.index) == [2]


# --- errors ---------------------------------------------------------------

@pytest.mark.parametrize("expr, message", [
    ("Country == USA", 'put it in quotes: "USA"'),
    ('Contry == "USA"', "did you mean Country"),
    ("time + 1", "True/False for each row"),
    ("Country > 5", "Type mismatch"),
    ("Dim > 1", "Type mismatch"),
    ("Number of employees > 5", "wrap it in backticks"),
    ("(time > 0", "Syntax error"),
])
def test_invalid_filters_raise_friendly_errors(df, expr, message):
    with pytest.raises(FilterError, match=message.replace("(", r"\(")):
        apply_data_filter(df, expr)


@pytest.mark.parametrize("expr", [
    "@x > 1",
    "time.__class__",
    'time.to_csv("/tmp/should_not_exist.csv")',
    "lambda: 1",
    "[c for c in time]",
    "eval('1')",
])
def test_unsafe_expressions_rejected(df, expr, tmp_path):
    with pytest.raises(FilterError):
        apply_data_filter(df, expr)


def test_missing_column_raises(df):
    with pytest.raises(FilterError):
        apply_data_filter(df, "`Not a column` > 1")


# --- lint warnings --------------------------------------------------------

def test_warns_numeric_column_compared_with_text(df):
    warnings = filter_warnings(df, 'n_features == "22"')
    assert len(warnings) == 1 and "numeric" in warnings[0]
    assert apply_data_filter(df, 'n_features == "22"').empty


def test_warns_text_column_compared_with_number(df):
    warnings = filter_warnings(df, "Dim == 1")
    assert len(warnings) == 1 and '"1"' in warnings[0]


def test_warns_in_list_type_mismatch(df):
    assert filter_warnings(df, "n_features in [\"20\", \"22\"]")


def test_no_warnings_for_correct_types(df):
    assert filter_warnings(df, 'n_features == 22 and Dim == "1" and date >= "2024-01-01"') == []


# --- grouping and shared limits -------------------------------------------

def test_group_expansion_and_limits_use_filtered_rows(df):
    filtered = apply_data_filter(df, "time >= 0")
    combos = expand_groups(filtered, ["Country"])
    assert combos == [{"Country": "Mexico"}, {"Country": "USA"}]

    subsets = [apply_filters(filtered, filter_query=fq) for fq in combos]
    xlim, ylim = shared_limits(subsets, "time", "value")
    assert xlim == (0.0, 1.0)
    assert ylim == (30.0, 50.0)


# --- PlotTile -------------------------------------------------------------

def test_tile_plots_only_filtered_rows(qapp, df):
    from plot_organizer.ui.grid_board import PlotTile

    tile = PlotTile()
    tile.set_plot(df, "time", "value", data_filter="time >= 0")

    assert tile._df is df  # original frame kept for datasource lookup on save
    assert tile._data_filter == "time >= 0"
    assert "time >= 0" in tile.toolTip()
    line = tile.figure.axes[0].lines[0]
    assert list(line.get_xdata()) == [0.0, 0.5, 1.0]


def test_tile_filter_error_does_not_raise(qapp, df):
    from plot_organizer.ui.grid_board import PlotTile

    tile = PlotTile()
    tile.set_plot(df, "time", "value", data_filter="missing_column > 1")
    texts = [t.get_text() for t in tile.figure.axes[0].texts]
    assert any("Filter error" in t for t in texts)


def test_tile_clear_resets_filter(qapp, df):
    from plot_organizer.ui.grid_board import PlotTile

    tile = PlotTile()
    tile.set_plot(df, "time", "value", data_filter="time >= 0")
    tile.clear_plot()
    assert tile._data_filter is None
    assert tile.toolTip() == ""


def test_tile_serialization_round_trip(qapp, df, tmp_path):
    from plot_organizer.ui.grid_board import GridBoard
    from plot_organizer.services.project_service import save_workspace, load_workspace
    from plot_organizer.models import DataSource

    csv = tmp_path / "data.csv"
    df.to_csv(csv, index=False)
    ds = DataSource(id="ds1", name="data", path=str(csv), dataframe=df, schema=[])

    board = GridBoard(rows=1, cols=1)
    board.tile_at(0, 0).set_plot(
        df, "time", "value", data_filter='Country == "USA"', filter_query={"flag": True}
    )
    layout = board.serialize_layout({"ds1": ds})
    assert layout[0]["datasource_id"] == "ds1"
    assert layout[0]["data_filter"] == 'Country == "USA"'

    path = tmp_path / "project.ppo"
    save_workspace(str(path), layout, {"ds1": {"name": "data", "path": str(csv)}}, 1, 1)
    plot_data = load_workspace(str(path))["plots"][0]

    board2 = GridBoard(rows=1, cols=1)
    tile = board2.tile_at(0, 0)
    tile.set_plot_from_data(df, plot_data)
    assert tile._data_filter == 'Country == "USA"'
    assert list(tile.figure.axes[0].lines[0].get_xdata()) == [-1.0, 0.0]


def test_legacy_plot_data_without_filter_loads(qapp, df):
    from plot_organizer.ui.grid_board import PlotTile

    tile = PlotTile()
    tile.set_plot_from_data(df, {"x": "time", "y": "value"})
    assert tile._data_filter is None
    assert len(tile.figure.axes[0].lines[0].get_xdata()) == 5


def test_markers_rerender_keeps_filter_and_ticks(qapp, df, monkeypatch):
    from plot_organizer.ui import dialogs
    from plot_organizer.ui.grid_board import PlotTile

    class FakeManager:
        def __init__(self, *args, **kwargs):
            pass

        def exec(self):
            return 0

        def get_markers(self):
            return [{"x": None, "y": 30.0, "xerr": None, "yerr": 1.0, "color": "red"}]

    monkeypatch.setattr(dialogs, "ErrorMarkersManagerDialog", FakeManager)
    tile = PlotTile()
    tile.set_plot(df, "time", "value", data_filter="time >= 0", xticks=[0.0, 1.0])
    tile._open_markers_dialog()

    assert tile._data_filter == "time >= 0"
    assert tile._xticks == [0.0, 1.0]
    assert list(tile.figure.axes[0].lines[0].get_xdata()) == [0.0, 0.5, 1.0]


# --- export ---------------------------------------------------------------

def test_export_renders_filtered_rows(qapp, df):
    import matplotlib.pyplot as plt
    from plot_organizer.services.export_service import _render_plot_to_ax
    from plot_organizer.ui.grid_board import PlotTile

    tile = PlotTile()
    tile.set_plot(df, "time", "value", data_filter="time < 0")
    fig, ax = plt.subplots()
    _render_plot_to_ax(tile, ax)
    assert list(ax.lines[0].get_xdata()) == [-1.0, -0.5]
    plt.close(fig)


# --- dialog ---------------------------------------------------------------

def _make_dialog(df):
    from plot_organizer.ui.dialogs import QuickPlotDialog

    return QuickPlotDialog(
        ds_to_columns={"ds1": list(df.columns)},
        ds_names={"ds1": "data"},
        ds_to_df={"ds1": df},
    )


def test_dialog_selection_includes_filter(qapp, df):
    dlg = _make_dialog(df)
    dlg.filter_input.setPlainText("time >= 0")
    dlg._update_filter_status()
    assert "3 of 5 rows match" in dlg.filter_status_label.text()
    dlg.accept()
    assert dlg.selection()["data_filter"] == "time >= 0"


def test_dialog_without_filter_returns_none(qapp, df):
    dlg = _make_dialog(df)
    dlg.accept()
    assert dlg.selection()["data_filter"] is None


def test_dialog_invalid_filter_blocks_selection(qapp, df):
    dlg = _make_dialog(df)
    dlg.filter_input.setPlainText("Country == USA")
    dlg._update_filter_status()
    assert "quotes" in dlg.filter_status_label.text()
    dlg.accept()
    assert dlg.selection() is None


def test_dialog_shows_type_warning(qapp, df):
    dlg = _make_dialog(df)
    dlg.filter_input.setPlainText('n_features == "22"')
    dlg._update_filter_status()
    assert "⚠" in dlg.filter_status_label.text()


def test_dialog_insert_column_backticks_names(qapp, df):
    dlg = _make_dialog(df)
    index = dlg.filter_column_combo.findData("Number of employees")
    dlg._insert_filter_column(index)
    assert dlg.filter_input.toPlainText() == "`Number of employees`"
    assert "no quotes" in dlg.filter_hint_label.text()


# --- programmatic API -----------------------------------------------------

def test_api_create_plot_stores_filter():
    from plot_organizer.api import create_plot

    plot = create_plot("ds1", "time", "value", data_filter="time >= 0")
    assert plot["data_filter"] == "time >= 0"
    assert create_plot("ds1", "time", "value")["data_filter"] is None


def test_api_grouped_plots_respect_filter(df, tmp_path):
    from plot_organizer.api import create_grouped_plots

    csv = tmp_path / "data.csv"
    df.to_csv(csv, index=False)
    plots = create_grouped_plots(
        "ds1", str(csv), x="time", y="value", groups=["Country"], data_filter="time >= 0"
    )
    assert [p["filter_query"] for p in plots] == [{"Country": "Mexico"}, {"Country": "USA"}]
    assert all(p["data_filter"] == "time >= 0" for p in plots)
    # Auto limits (with 5% padding) come from filtered rows only: value 30..50
    ymin, ymax = plots[0]["ylim"]
    assert np.isclose(ymin, 29.0) and np.isclose(ymax, 51.0)


def test_api_grouped_plots_invalid_filter_raises(df, tmp_path):
    from plot_organizer.api import create_grouped_plots

    csv = tmp_path / "data.csv"
    df.to_csv(csv, index=False)
    with pytest.raises(FilterError):
        create_grouped_plots("ds1", str(csv), x="time", y="value", groups=["Country"],
                             data_filter="Country == USA")
