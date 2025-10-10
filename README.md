# Plot Organizer (Work in Progress)

A desktop Python GUI (PySide6) to organize multiple line plots into a moveable grid, with CSV loading, faceting by groups, shared axes, and export to PDF/SVG/EPS/PNG.

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

- Models, group expansion, shared limits implemented.
- Minimal UI with grid grow (+row/+col) implemented.
- Service stubs present for load/render/layout/export/project.

See `design.md` for the complete design plan.
