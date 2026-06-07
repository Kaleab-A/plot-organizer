# Feature Reference

This document describes every major feature in quick-plot, including how to use it in the GUI and (where applicable) via the programmatic API.

---

## Table of Contents

1. [CSV Loading & Type Inference](#csv-loading--type-inference)
2. [Creating Plots](#creating-plots)
3. [Hue (Color Grouping)](#hue-color-grouping)
4. [Multi-Column Hue](#multi-column-hue)
5. [Group Faceting](#group-faceting)
6. [SEM — Standard Error of the Mean](#sem--standard-error-of-the-mean)
7. [Pre-computed SEM](#pre-computed-sem)
8. [Reference Lines](#reference-lines)
9. [Error Marker Annotations](#error-marker-annotations)
10. [Plot Style Customization](#plot-style-customization)
11. [Grid Management](#grid-management)
12. [Project Save / Load](#project-save--load)
13. [Export](#export)
14. [Programmatic API](#programmatic-api)
15. [CLI / Headless Export](#cli--headless-export)

---

## CSV Loading & Type Inference

**Access:** `Data → Add CSV…`

Load any CSV file as a data source. The app automatically infers a variable type for each column:

| Type | Description |
|------|-------------|
| `categorical` | String or low-cardinality columns |
| `continuous` | Numeric columns with many unique values |
| `ordinal` | Numeric columns treated as ordered categories |

Multiple CSV files can be loaded simultaneously; each becomes an independent data source selectable in the Create Plot dialog.

---

## Creating Plots

**Access:** `Plot → Quick Plot…`

Fill in the dialog:

| Field | Required | Description |
|-------|----------|-------------|
| Data Source | Yes | The loaded CSV to plot from |
| x | Yes | Column for the x-axis |
| y | Yes | Column for the y-axis |
| Hue columns | No | Columns to use for color grouping (see [Hue](#hue-color-grouping)) |
| SEM column | No | Column for error shading (see [SEM](#sem--standard-error-of-the-mean)) |
| Pre-computed SEM | No | Check if SEM column contains pre-computed values |
| Groups | No | Columns for faceting — creates one plot per combination |
| Plot Style | No | Line, Markers, or both |
| Reference Lines | No | Comma-separated x/y values for dashed reference lines |

Clicking OK places the plot(s) in the first available grid cell(s), expanding the grid as needed.

**Automatic aggregation:** If multiple rows share the same (x, hue) pair, their y-values are averaged before plotting — producing clean single lines instead of overlapping scatter.

---

## Hue (Color Grouping)

Select a single categorical column as hue. Each unique value in that column gets its own colored line and legend entry.

Works with: SEM, groups, reference lines, all export formats.

---

## Multi-Column Hue

Select two or more columns as hue. The app creates one line per unique *combination* of values across all selected columns.

**Legend format:** `species=setosa, gender=male`, `species=setosa, gender=female`, etc.

**Implementation:** A temporary `__composite_hue__` column is created in-memory using `Col1=val1, Col2=val2` formatting. The original dataframe is never modified.

**Example workflow:**
1. Open `Plot → Quick Plot…`
2. In the "Hue columns" multi-select list, hold Ctrl/Cmd and click multiple columns
3. The label shows "Selected 2 hue column(s). Will combine values for legend."
4. Click OK

Works with all features: SEM (computed and pre-computed), group faceting, reference lines, plot styles, shared limits, and export.

---

## Group Faceting

Select one or more columns under "Groups" to create one plot per unique combination of values (Cartesian product). All plots in the group automatically share the same x/y axis limits.

**Cap:** 200 combinations maximum. Exceeding this raises an error.

**Shared axis limits** are computed from the aggregated data across all subsets — not raw values — so the y-axis fits what is actually plotted, including any SEM bands.

**Titles:** Each plot is titled with its filter values, e.g., `Country=USA, Industry=Tech`.

**Example:**
- Groups: `Country` → creates one plot per country, all on the same y-scale.
- Groups: `Country`, `Industry` → one plot per (country, industry) pair.

---

## SEM — Standard Error of the Mean

**Access:** Create Plot dialog → "SEM column" dropdown

Select a column that identifies repeated measurements (e.g., subject ID, trial number, replicate ID). The app:

1. Groups data by the SEM column for each x-value
2. Computes the mean across groups
3. Computes SEM across groups
4. Plots the mean as a line with a translucent shaded region for ±1 SEM

**With hue:** Each hue category gets its own line and SEM region with a matching color.

**With groups:** SEM computation applies independently to each faceted plot. Shared axis limits account for the full mean ± SEM range, not raw values.

**Export:** SEM regions are preserved in PDF, SVG, EPS, and PNG exports.

**Typical use cases:**
- Multiple subjects measured over time → shows average trajectory with inter-subject variability
- Multiple trials per condition → shows condition mean with trial-to-trial variance
- Replicate sensor readings → shows average with measurement uncertainty

---

## Pre-computed SEM

**Access:** Create Plot dialog → "SEM column" + check "Pre-computed SEM"

If your data already contains computed SEM values in a column (e.g., exported from R/MATLAB/Excel), check this box to use them directly instead of computing from grouped data.

**Duplicate x-values:** If multiple rows exist for the same x-value, both y and SEM are averaged automatically; a warning is logged to the console.

**Modes at a glance:**

| Mode | When to use | How it works |
|------|------------|--------------|
| Computed (default) | Raw repeated measurements | Groups by SEM col, computes mean ± SEM |
| Pre-computed | Pre-aggregated data with SEM column | Reads SEM values directly from column |

Both modes produce visually identical plots.

---

## Reference Lines

**Access:** Create Plot dialog → "Reference Lines" section

Add horizontal and/or vertical dashed lines to mark thresholds, baselines, time points, or other reference values.

- **Horizontal lines:** Enter comma-separated y-values (e.g., `0, 50, 100`)
- **Vertical lines:** Enter comma-separated x-values (e.g., `2020, 2021, 2022`)

**Style:** Black, dashed, 70% opacity. Lines appear behind plot data.

**With groups:** Reference lines appear on every plot in the faceted group.

**Invalid entries** (non-numeric) are silently skipped; valid entries still render.

**Typical use cases:**
- `Horizontal: 0` — zero baseline
- `Horizontal: 50, 95` — target thresholds
- `Vertical: 2020` — event marker
- `Horizontal: 2.5, 97.5` — 95% confidence boundaries

---

## Error Marker Annotations

**Access:** Right-click any plot → `Manage Error Markers…`

Add annotated error bars at specific positions on a plot — useful for marking checkpoints, threshold ranges, or time periods with uncertainty.

Each marker has:

| Field | Description |
|-------|-------------|
| x | X-position (or `None` for auto) |
| y | Y-position (or `None` for auto) |
| xerr | Horizontal error bar half-width |
| yerr | Vertical error bar half-width |
| color | Marker color |
| label | Optional legend label |

**Auto-positioning:** When `x` or `y` is `None`, the position is computed from the plot's data range. Multiple markers stack automatically (0.08 × range offset) to avoid overlap.

- X error bars (horizontal) stack vertically from the top
- Y error bars (vertical) stack horizontally from the right

**Via API:**
```python
plot = create_plot(
    datasource_id,
    x="time", y="accuracy",
    error_markers=[
        {"x": 5.0, "xerr": 0.5, "color": "red", "label": "Checkpoint"},
        {"y": 0.8, "yerr": 0.1, "color": "blue", "label": "Target"},
    ]
)
```

Markers are serialized in `.ppo` project files and preserved across save/load cycles.

---

## Plot Style Customization

**Access:** Create Plot dialog → "Plot Style" section

| Option | Default | Description |
|--------|---------|-------------|
| Line | ✅ Checked | Traditional continuous line |
| Markers | ☐ Unchecked | Scatter-style marker at each data point |

**Combinations:**
- **Line only:** Clean trend visualization (default)
- **Markers only:** Good for sparse or discrete data
- **Both:** Line with markers — useful for presentations or emphasis

Style is applied uniformly across all hue categories and works with SEM shaded regions. Style settings are preserved in exports and `.ppo` project files.

---

## Grid Management

**Add rows/columns:** `Grid → + Row` / `Grid → + Col`

**Remove rows/columns:** `Grid → - Row…` / `Grid → - Col…` — only succeeds if the row/column contains no non-empty plots.

**Reset Grid:** `Grid → Reset Grid…` — clears all plots and restores the default 2×3 layout. Requires confirmation; cannot be undone.

**Plot Settings** (right-click any tile → `Plot Settings…`):
- Move a plot to a different position (swaps with the target cell; both plots must have the same span)
- Change a plot's row/column span (multi-cell plots)

Position and span changes are mutually exclusive in a single dialog open.

---

## Project Save / Load

**Save:** `File → Save Project` (Ctrl+S) or `File → Save Project As…` (Ctrl+Shift+S)

**Load:** `File → Load Project…` (Ctrl+O)

Projects are stored as human-readable JSON with the `.ppo` extension. All plot parameters are serialized:

```json
{
  "version": "0.9.0",
  "grid": { "rows": 2, "cols": 3 },
  "data_sources": [
    {
      "id": "uuid",
      "name": "Results",
      "path": "relative/path/to/data.csv",
      "schema": [...]
    }
  ],
  "plots": [
    {
      "id": "uuid",
      "grid_position": { "row": 0, "col": 0, "rowspan": 1, "colspan": 2 },
      "datasource_id": "uuid",
      "x": "time",
      "y": "accuracy",
      "hue": ["model", "dataset"],
      "sem_column": "fold",
      "sem_precomputed": false,
      "filter_query": { "experiment": "A" },
      "hlines": [0, 50],
      "vlines": [10],
      "style_line": true,
      "style_marker": false,
      "ylim": [0, 1],
      "title": "Experiment A"
    }
  ]
}
```

**Relative paths:** CSV file paths are stored relative to the `.ppo` file, making projects portable across machines.

**Missing files:** If a CSV is not found at load time, the app warns and skips the missing source while loading everything else.

---

## Export

**Access:** `Export → Export Grid…`

Export the entire grid layout to a file:

| Format | Type | Typical use |
|--------|------|-------------|
| PDF | Vector | Papers, reports, printing |
| SVG | Vector | Web, presentations |
| EPS | Vector | LaTeX, journals |
| PNG | Raster | Quick sharing, slides |

**Options:**
- Page size: A4, Letter, or custom (inches)
- DPI: 72–600 (PNG only; default 150)

**Rendering:** Plots are re-rendered from data (not screenshots), so exports are crisp at any zoom level. Spanning plots, shared axes, SEM regions, reference lines, and plot styles are all preserved.

---

## Programmatic API

```python
from plot_organizer.api import (
    create_datasource, create_plot, create_project,
    save_project_file, load_project_file,
    quick_project, create_grouped_plots, quick_grouped_project,
)
```

### Core functions

```python
# Create a datasource descriptor
ds = create_datasource("Experiment", "data/results.csv")

# Create a plot descriptor
plot = create_plot(
    ds["id"],
    x="time", y="accuracy",
    hue=["model", "dataset"],
    sem_column="fold",
    hlines=[0.5, 0.9],
    row=0, col=0,
)

# Assemble and save
project = create_project((2, 3), [ds], [plot])
save_project_file(project, "experiment.ppo")
```

### Grouped plots (replicates GUI faceting)

```python
# Creates one plot per group combination with auto-computed shared y-limits
plots = create_grouped_plots(
    datasource_id=ds["id"],
    dataframe_path="data/results.csv",
    x="time", y="accuracy",
    groups=["species", "treatment"],
    hue=["model"],
    layout="row",  # or "col"
)

project = create_project((2, 3), [ds], plots)
save_project_file(project, "grouped.ppo")
```

### Convenience one-liners

```python
# Single datasource, manually specified plots
project = quick_project("Results", "data.csv", plots)

# Single datasource, group faceting, everything auto
project = quick_grouped_project(
    "Results", "data.csv",
    x="time", y="accuracy",
    groups=["species"],
)
```

---

## CLI / Headless Export

```bash
# Start GUI (empty workspace)
quick-plot

# Start GUI and load a project
quick-plot my_project.ppo

# Export to PDF without showing the GUI
quick-plot my_project.ppo --no-gui --export output.pdf

# Full options
quick-plot project.ppo \
  --export figure.png \
  --format png \
  --width 16 \
  --height 9 \
  --dpi 300
```

| Argument | Default | Description |
|----------|---------|-------------|
| `project` | — | `.ppo` file to load |
| `--no-gui` | off | Headless mode (requires `--export`) |
| `--export OUTPUT` | — | Output file path |
| `--format` | `pdf` | `pdf`, `svg`, `eps`, or `png` |
| `--width` | `11.0` | Export width in inches |
| `--height` | `8.5` | Export height in inches |
| `--dpi` | `150` | DPI for PNG exports |
