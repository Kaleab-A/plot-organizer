# Roadmap

This document tracks planned features and known gaps. If you'd like to work on any of these, open a GitHub Issue first to discuss approach.

---

## High Priority

### Drag-and-Drop Plot Rearrangement
Drag a tile's header and drop it onto another cell to swap or move plots. Currently, plots can only be repositioned through the right-click → Plot Settings dialog.

### Full CSV Load Wizard
The current CSV loader auto-detects settings. A full wizard would add:
- Delimiter and encoding options (auto + manual override)
- Header row selection
- Custom NA strings
- Per-column missing value handling (drop rows, drop column, keep as-is, fill)
- Type confirmation dialog with editable column types and category ordering for ordinal columns

---

## Medium Priority

### Threaded CSV Loading
Large CSV files currently block the UI while loading. Background loading with a progress bar would improve responsiveness for files >100 MB.

### Per-Plot Export
Export a single plot directly from the right-click context menu, at a user-specified size and format.

### DateTime Axis Formatting
Automatically detect datetime columns and format tick labels using Matplotlib's `AutoDateLocator` and `AutoDateFormatter`.

---

## Low Priority / Future

### Additional Error Measures
Currently only mean ± SEM is supported. Future: standard deviation, 95% confidence intervals, bootstrapped CIs.

### Error Bar Style Options
Currently error markers use a fixed triangle marker (size 10, capsize 5). Future: configurable marker shape, size, and capsize.

### Style Overrides Per-Plot
Fine-grained per-plot customization: line width, custom colors, legend toggle, marker size.

### Variable Cell Sizes
Non-uniform grid cell widths and heights. Currently all cells share the same dimensions.

### Auto-Save / Recent Projects
Periodic auto-save and a `File → Open Recent` submenu.

### Undo / Redo
Undo grid operations, plot clears, and settings changes.

---

## Completed (v0.2 – v0.8)

| Feature | Version |
|---------|---------|
| Group faceting with shared axes | 0.2 |
| Automatic aggregation of duplicate values | 0.2.1 |
| Plot settings (position, spanning) | 0.3 |
| Remove rows/columns | 0.3 |
| Tile context menu | 0.3 |
| Whole-grid export (PDF/SVG/EPS/PNG) | 0.4 |
| SEM with shaded regions | 0.5 |
| SEM-aware shared axis limits | 0.5.1 |
| Reference lines (horizontal & vertical) | 0.6 |
| Pre-computed SEM support | 0.7 |
| Plot style customization (line/markers) | 0.8 |
| Grid reset | 0.8 |
| Multi-column hue | post-0.8 |
| Project save/load (.ppo) | post-0.8 |
| CLI / headless export | post-0.8 |
| Programmatic API | post-0.8 |
| Error marker annotations | post-0.8 |
