# Quick Start Guide

## Installation

### From PyPI (recommended)

```bash
pip install quick-plot
```

### From Source

```bash
git clone https://github.com/<owner>/PlotOrganizer.git
cd PlotOrganizer
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

## Running the App

```bash
quick-plot
```

Or without installing:

```bash
python -m plot_organizer.app
```

## Creating Your First Plot

### 1. Load a CSV

Click **Data → Add CSV…** (or use the "Add CSV…" button in the Data Sources dock on the left).

Navigate to any CSV file. The file is loaded and appears in the Data Sources list with auto-inferred column types.

Sample data is available in `plot_organizer/tests/test_csv/organizations-10000.csv`.

### 2. Create a Plot

Click **Plot → Quick Plot…** and fill in the dialog:

- **x**: the column for the x-axis (e.g., `Founded`)
- **y**: the column for the y-axis (e.g., `Number of employees`)
- **Hue columns** (optional): one or more categorical columns — each unique value (or combination) gets its own colored line
- **SEM column** (optional): a column identifying repeated measurements — the app computes mean ± SEM and draws a shaded region
  - Check **Pre-computed SEM** if the column already contains SEM values
- **Groups** (optional): one or more columns for faceting — creates one plot per unique combination
- **Plot Style**: Line (default), Markers, or both
- **Reference Lines** (optional): comma-separated y-values for horizontal lines, comma-separated x-values for vertical lines

Click **OK**. The plot(s) appear in the grid.

### 3. Interact with Plots

- **Right-click** any tile → `Plot Settings…` to change position or span (multi-cell plots)
- **Right-click** any tile → `Clear Plot` to reset a tile
- **Right-click** any tile → `Manage Error Markers…` to add annotated error bars

### 4. Manage the Grid

- `Grid → + Row` / `Grid → + Col` — add rows/columns
- `Grid → - Row…` / `Grid → - Col…` — remove empty rows/columns
- `Grid → Reset Grid…` — clear all plots and reset to default 2×3 layout

### 5. Save Your Work

`File → Save Project` (Ctrl+S) — saves a `.ppo` JSON file with all plot configurations and data source references.

`File → Load Project…` (Ctrl+O) — restores a saved workspace.

### 6. Export

`Export → Export Grid…` — export the full grid to PDF, SVG, EPS, or PNG with configurable size and DPI.

---

## Example: Faceted Plot

Using `organizations-10000.csv`:

1. **x**: `Founded`
2. **y**: `Number of employees`
3. **Groups**: `Country` (hold Ctrl/Cmd to select multiple)
4. Click OK → one plot per country, all with the same y-scale

---

## Headless Export (CLI)

```bash
# Export a project to PDF without opening the GUI
quick-plot my_project.ppo --no-gui --export output.pdf

# Export as PNG with custom dimensions
quick-plot my_project.ppo --no-gui --export figure.png \
  --format png --width 16 --height 9 --dpi 300
```

---

## Programmatic API

```python
from plot_organizer.api import quick_project, create_plot, save_project_file

plots = [
    create_plot("", x="time", y="accuracy", hue=["model"], row=0, col=0),
    create_plot("", x="time", y="loss", row=0, col=1),
]

project = quick_project("Experiment", "data/results.csv", plots)
save_project_file(project, "experiment.ppo")
```

See `examples/` and `docs/features.md` for more.

---

## NumPy 2 Note

This project requires NumPy ≥ 2.0. If you see NumPy import errors after installing, reinstall the affected packages:

```bash
pip uninstall -y pandas matplotlib pyarrow
pip install --no-cache-dir quick-plot
```
