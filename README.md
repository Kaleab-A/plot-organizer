# Plot Organizer (Work in Progress)

<!-- <img width="3584" height="2240" alt="image" src="https://github.com/user-attachments/assets/b4cf363e-43cf-464a-ab9e-629f869931cc" /> -->


A desktop Python GUI (PySide6) to organize multiple line plots into a moveable grid, with CSV loading, customizable plot styles (line/markers), faceting by groups, shared axes, SEM (Standard Error of the Mean) plotting with shaded regions, reference lines for thresholds/markers, and export to PDF/SVG/EPS/PNG.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m plot_organizer.app
```

**NumPy 2 Compatibility:** This project requires NumPy >= 2.0. If you encounter NumPy import errors, reinstall dependencies to get NumPy 2-compatible wheels:
```bash
pip uninstall -y pandas matplotlib pyarrow
pip install --no-cache-dir -r requirements.txt
```

## Structure

- `plot_organizer/app.py`: Entrypoint launching the Qt `MainWindow` and `GridBoard`.
- `plot_organizer/models/`: Dataclasses for data sources, plot specs, instances, and grid layout.
- `plot_organizer/services/`: Core logic: group expansion, shared limits, loading/type inference, rendering, layout ops, export, project save.
- `plot_organizer/ui/`: Minimal UI: `MainWindow` with a center `GridBoard` to hold tiles.

## Tests

```bash
pytest
```

## Status

- ✅ CSV loading with automatic type inference
- ✅ Plot creation with x, y, hue, SEM column, groups, plot style, and reference lines
- ✅ Plot style customization (line, markers, or both)
- ✅ Reference lines (horizontal & vertical dashed lines)
- ✅ SEM (Standard Error of the Mean) with shaded regions
- ✅ Pre-computed SEM support (use SEM values directly from data)
- ✅ Group faceting (multi-select columns, up to 50 combinations)
- ✅ SEM-aware shared axes across grouped plots
- ✅ Automatic aggregation of duplicate values
- ✅ Plot settings for position and spanning
- ✅ Grid management (add/remove rows/cols, reset to default)
- ✅ Whole-grid export to PDF/SVG/EPS/PNG

See `design.md` for the complete design plan and `QUICKSTART.md` for usage guide.
