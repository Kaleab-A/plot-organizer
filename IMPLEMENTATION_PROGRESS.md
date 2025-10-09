# Plot Organizer – Implementation Progress

_Last updated: 2025-10-09_

## Implemented (v1 groundwork)

- Project scaffold under `plot_organizer/` with packages for `models`, `services`, and `ui`.
- Models (`models/dataspec.py`): `ColumnSchema`, `DataSource`, `PlotSpec`, `PlotInstance`, `GridLayout`.
- Services:
  - `plot_service.py`: `expand_groups`, `shared_limits`.
  - `load_service.py`: heuristics for variable type inference and `build_schema`.
  - `layout_service.py`: create grid, add row/col, move/place plot.
  - `render_service.py`: simple line plot renderer (matplotlib), supports hue and shared limits.
  - `export_service.py`: single-plot export via `savefig()`.
  - `project_service.py`: save project (`.ppo.json`-style structure) with relative paths when possible.
- UI:
  - `ui/main_window.py`: base `MainWindow` with File/Grid menus and actions.
  - `ui/grid_board.py`: `GridBoard` with uniform `PlotTile`s, +Row/+Col operations.
- Tests (`plot_organizer/tests/`):
  - `test_group_expand.py` for group combinations.
  - `test_shared_limits.py` for shared axis calculation.
- Tooling:
  - `requirements.txt` with runtime and test dependencies.

## What’s next (per design.md)

- CSV Load Wizard (threaded IO, NA handling, type confirmation UI).
- Plot Wizard (select datasource/x/y/hue/groups, preview combo count, cap at 50).
- Embed Matplotlib canvases (`FigureCanvasQTAgg`) in `PlotTile` with toolbar.
- Drag-and-drop to move plots between cells; duplicate/clear via context menu.
- Whole-grid export (compose new `Figure` with `GridSpec`) and per-plot export dialog.
- Project load flow and relinking missing files.
- Additional tests: inference edge cases, export outputs, basic UI integration.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m plot_organizer.app
```
