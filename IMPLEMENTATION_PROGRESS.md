# Plot Organizer – Implementation Progress

_Last updated: 2025-10-10_

## ✅ Now Working (v0.3.1)

**Full control over plot positioning, spanning, and grid management with smart swapping!**

- **CSV Loading**: Data → Add CSV… loads a file, infers column types, and adds it to the Data Sources dock.
- **Plot Creation**: Plot → Quick Plot… lets you pick a data source, x/y columns, optional hue, and groups for faceting.
- **Group Faceting**: Multi-select group columns to create multiple plots (one per unique combination), capped at 50 combinations.
- **Shared Axes**: When using groups, all generated plots share the same x/y axis limits for easy comparison.
- **Automatic Aggregation**: When multiple y-values exist for the same (x, hue) combination, they are automatically averaged. Clean, single-line plots!
- **Plot Settings**: Right-click any plot → configure position (swap) OR spanning (change one at a time).
- **Smart Swapping**: Position changes swap plots if spans match; validates and gives clear error messages if not.
- **Context Menu**: Right-click plots for settings and clear options.
- **Grid Management**: Add rows/cols via Grid menu; remove empty rows/cols with safety checks.
- **Clear Plots**: Remove plot data from cells (with confirmation).
- **Clean UI**: Plots now take maximum space with minimal margins.

## Implemented (v1 groundwork)

- Project scaffold under `plot_organizer/` with packages for `models`, `services`, and `ui`.
- Models (`models/dataspec.py`): `ColumnSchema`, `DataSource`, `PlotSpec`, `PlotInstance`, `GridLayout`.
- Services:
  - `plot_service.py`: `expand_groups`, `shared_limits`.
  - `load_service.py`: heuristics for variable type inference, `build_schema`, `load_csv_to_datasource`.
  - `layout_service.py`: create grid, add row/col, move/place plot.
  - `render_service.py`: simple line plot renderer (matplotlib), supports hue and shared limits.
  - `export_service.py`: single-plot export via `savefig()`.
  - `project_service.py`: save project (`.ppo.json`-style structure) with relative paths when possible.
- UI:
  - `ui/main_window.py`: `MainWindow` with Data/Plot/Grid menus, Data Manager dock, Quick Plot action.
  - `ui/grid_board.py`: `GridBoard` with `PlotTile`s embedding Matplotlib canvases, +Row/+Col operations.
  - `ui/data_manager.py`: Data Sources list with Add/Remove buttons.
  - `ui/dialogs.py`: `QuickPlotDialog` for selecting x/y/hue.
- Tests (`plot_organizer/tests/`):
  - `test_group_expand.py` for group combinations.
  - `test_shared_limits.py` for shared axis calculation.
- Tooling:
  - `requirements.txt` with runtime and test dependencies.

## What's next (per design.md)

- **CSV Load Wizard**: Advanced NA handling UI, type confirmation dialog (currently auto-inferred).
- **Full Plot Wizard**: Add groups (faceting), preview combo count, cap at 50, shared axes.
- **Drag-and-drop**: Move plots between cells; duplicate/clear via context menu.
- **Whole-grid export**: Compose new `Figure` with `GridSpec` for PDF/SVG/EPS/PNG export.
- **Project save/load**: Persist entire workspace state to `.ppo.json`.
- **Additional tests**: Inference edge cases, export outputs, basic UI integration.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m plot_organizer.app
```
