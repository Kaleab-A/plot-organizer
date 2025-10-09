# Python Plot Organizer – Design & Implementation Plan

_Last updated: 2025-10-09 (America/Chicago)_

---

## 1) Goals & Non‑Goals

**Goals (v1)**
- Desktop Python GUI that organizes multiple line plots into a moveable grid.
- Load multiple CSV files as data sources.
- Create plots from a **single** dataframe at a time.
- Plot spec fields: `x`, `y`, `hue` (categorical color), `group` (faceting columns → cross-product creates independent plot objects; capped at 50).
- Grid operations: add/remove rows/columns, drag plots between cells ("subgrid plots").
- Handle missing values at load time; infer variable types (categorical, continuous, ordinal) and confirm via GUI.
- Axis policy: when using `group` combinations, **share min/max** x & y across the generated plots.
- Export: vectorized **PDF/SVG/EPS** and raster **PNG** of the organized layout; also allow per-plot exports.

**Non-Goals (v1)**
- Multi‑Y axes (planned later).
- Undo/redo history.
- Deployment packaging (PyInstaller) — _run as Python code for now_.

---

## 2) Technical Choices

- **Python**: 3.11 recommended (works with 3.10+).
- **GUI Framework**: **PySide6** (Qt for Python, LGPL) for rich drag‑and‑drop, docking, dialogs, and mature Matplotlib embedding.
- **Plotting**: **Matplotlib** with `FigureCanvasQTAgg` and `NavigationToolbar2QT` for per‑plot interactivity (pan/zoom/save) inside the app.
- **Data**: **pandas** for CSV ingestion, typing inference, filtering, and slicing.
- **Export**: Matplotlib `Figure.savefig()` for PDF/SVG/EPS/PNG. Combined layout exports are re‑rendered from plot specs to a fresh export-only `Figure` grid for exact WYSIWYG with shared axes support.
- **Config/Persistence**: JSON project file (`.ppo.json`) that references CSV paths and stores layout + specs.

---

## 3) Architecture Overview

### 3.1 Layers
- **Model**: In‑memory state (data sources, plot specs, grid layout). No Qt dependencies; pure Python dataclasses.
- **Controller/Services**: Data loading, type inference, plot generation, export, project I/O.
- **View/UI**: Qt widgets: main window, data manager, plot wizard, grid canvas, dialogs.

### 3.2 Key Data Classes (Model)
```text
DataSource
  id: UUID
  name: str  # alias shown in UI
  path: Path
  dataframe: pandas.DataFrame
  schema: list[ColumnSchema]

ColumnSchema
  name: str
  dtype: str  # pandas dtype string
  var_type: Literal['categorical','continuous','ordinal']
  categories: Optional[list[str]]  # for categorical/ordinal
  notes: Optional[str]

PlotSpec
  id: UUID
  datasource_id: UUID
  x: str
  y: str
  hue: Optional[str]
  groups: list[str]  # faceting cols; cross product → multiple plots
  title: Optional[str]
  share_axes: bool  # derived: true for group-generated sets
  style_overrides: dict[str, Any]  # linewidth, markers, etc.

PlotInstance
  id: UUID
  spec_id: UUID
  filter_query: dict[str, Any]  # concrete equality filters for a single group combo
  empty: bool  # whether selection yields no rows

GridLayout
  rows: int
  cols: int
  cells: dict[tuple[int,int], PlotInstance | None]
```

### 3.3 Services
- **LoadService**: CSV import, missing-value handling workflow, type inference + confirmation.
- **PlotService**: Builds `PlotInstance` objects from `PlotSpec` + groups (caps at 50), computes shared axis limits when applicable.
- **RenderService**: Creates/updates Matplotlib `Figure` for a given `PlotInstance` inside a `PlotWidget`.
- **LayoutService**: Add/remove rows/cols; move plot between cells.
- **ExportService**: Export single plots or entire grid to PDF/SVG/EPS/PNG; resolves page size, DPI, and font embedding.
- **ProjectService**: Save/load `.ppo.json` (relative paths where possible).

---

## 4) CSV Load Workflow & Type Inference

### 4.1 Load Wizard (GUI)
1. **Select CSV** (multiple allowed). Options: delimiter (auto + manual), encoding (auto + manual), header row, NA strings.
2. **Missing Values Check**
   - Per‑column summary: count of NA, % NA.
   - Actions per column: **Drop rows with NA in this column**, **Drop entire column**, **Keep as is**.
   - Global quick actions: "Drop rows with any NA", "Drop columns with >X% NA".
3. **Variable Type Inference** (editable table):
   - Default heuristic:
     - `object`/`string` → **categorical** by default.
     - low cardinality numeric (≤20 unique, ≤5% of rows) → **categorical**.
     - ordered pandas `CategoricalDtype(ordered=True)` → **ordinal**.
     - else → **continuous**.
   - User can override per column; for categorical/ordinal, can preview categories and order.
4. **Confirm & Name Data Source**: Default alias = filename; user can edit.

### 4.2 Implementation Notes
- Use a non‑blocking worker thread for file IO to keep UI responsive.
- Store final `ColumnSchema` alongside the DataFrame.
- Preserve original data; apply transformations (drops) to a working copy tied to the DataSource.

---

## 5) Plot Creation & Group Expansion

### 5.1 Plot Wizard (GUI)
- **Select Data Source** (dropdown of aliases).
- **Select x** (dropdown of columns).
- **Select y** (single column for v1).
- **Hue** (optional categorical column). If numeric selected, prompt: "Hue requires categorical; convert to binned categories?" (v1: disallow; future: binning).
- **Groups** (multi-select of columns). Tooltip explains that cross‑product of unique values → independent plots.
- **Preview count**: show expected number of combinations; warn and cap at **50** (user must reduce).
- **Title & Style (optional)**: Title, line width, marker toggle.
- **Create**: Generates one `PlotInstance` per group combination, each with concrete equality filters.

### 5.2 Axis Sharing for Group Sets
- For a group-expanded set created in one action:
  - Compute global `x_min, x_max` and `y_min, y_max` across all instances using the filtered subsets.
  - Assign these limits to each plot for consistent comparison.

### 5.3 Empty Combinations
- If a combination yields zero rows, mark `empty=True` and render a **blank plot** with a faint "No data for selection" label.

---

## 6) Grid & Layout Behavior

### 6.1 Grid Canvas
- A central **GridBoard** widget managing an `r×c` matrix of **PlotTile** widgets.
- Each `PlotTile` contains: Matplotlib canvas, toolbar, local title bar with the instance label (e.g., group values), and a context menu.

### 6.2 Operations
- **Add Row/Column**: Appends blank tiles; UI buttons: "+ Row", "+ Col". Removing prompts if tiles contain plots.
- **Move Plot Between Cells**: Drag a tile’s header and drop onto another cell; swap if destination is occupied (confirm prompt optional).
- **Cell Menu**: Replace plot, duplicate plot (clone PlotInstance), clear cell, export this plot.
- **Optional** (v1.1): resize column widths/row heights; (v1) use uniform sizes.

---

## 7) Rendering Details (Matplotlib)

- Use a **per‑tile Figure** (not a giant shared figure) for snappy interaction; for export we re‑compose.
- Default styles: Matplotlib defaults; color cycle for hue categories.
- Legend: if `hue` present, show inside plot (loc="best"); toggle available per plot.
- Time x‑axis handling: detect datetime and format ticks with `AutoDateLocator`.
- Performance: enable `axes.autolimit_mode='round_numbers'`; consider `path.simplify=True` and a small `path.simplify_threshold`.

---

## 8) Export Pipeline

### 8.1 Whole‑Grid Export
- Create a new offscreen Matplotlib `Figure` sized per user input (inches) with an `r×c` **GridSpec**.
- For each occupied cell, **re-render** from its `PlotInstance` + `PlotSpec` into the corresponding subplot, applying shared axis limits if marked.
- Save via `savefig()` to selected format: **PDF**, **SVG**, **EPS**, **PNG**.
- Options dialog:
  - Page size: presets (A4, Letter) or custom width/height (inches/mm).
  - Margins & gutters.
  - DPI (for PNG) default 150.
  - Font embedding: enabled for vector formats.
  - Filename pattern.

### 8.2 Per‑Plot Export
- From a `PlotTile` menu, export the single figure at a chosen size and format.

---

## 9) Persistence (.ppo.json)

### 9.1 Structure (Example)
```json
{
  "version": 1,
  "data_sources": [
    {
      "id": "8a2c...",
      "name": "sales_2024",
      "path": "../data/sales_2024.csv",
      "schema": [
        {"name":"date","dtype":"datetime64[ns]","var_type":"continuous"},
        {"name":"region","dtype":"string","var_type":"categorical","categories":["N","S","E","W"]}
      ]
    }
  ],
  "plots": [
    {
      "id": "3f41...",
      "datasource_id": "8a2c...",
      "x": "date",
      "y": "revenue",
      "hue": "region",
      "groups": ["product"],
      "title": "Revenue by Region",
      "share_axes": true,
      "style_overrides": {"linewidth": 1.5}
    }
  ],
  "instances": [
    {
      "id": "i1",
      "spec_id": "3f41...",
      "filter_query": {"product":"A"},
      "empty": false
    }
  ],
  "grid": {
    "rows": 2,
    "cols": 3,
    "cells": {"(0,0)": "i1", "(0,1)": null, "(0,2)": null, "(1,0)": null, "(1,1)": null, "(1,2)": null}
  }
}
```

- Paths are stored relative to the project file when possible.
- On load, verify files exist; otherwise prompt to relink.

---

## 10) Error Handling & UX

- **Toasts** for transient successes (loaded, exported) and minor warnings.
- **Modals** for destructive actions (delete row/col with plots, cap exceeded).
- **Status bar** for long‑running operations with progress and cancel (CSV load, export).
- **Validation** in plot wizard (e.g., `x`/`y` required, hue type must be categorical).

---

## 11) Directory Layout

```text
plot_organizer/
  app.py                 # entrypoint (MainWindow)
  models/
    __init__.py
    dataspec.py          # DataSource, ColumnSchema, PlotSpec, PlotInstance, GridLayout
  services/
    __init__.py
    load_service.py      # CSV import, NA handling, typing wizard
    plot_service.py      # expand groups, axis ranges
    render_service.py    # Matplotlib figure creation/update
    layout_service.py    # grid ops
    export_service.py    # savefig orchestration
    project_service.py   # .ppo.json save/load
  ui/
    main_window.py       # menus, toolbars, dock widgets
    data_manager.py      # data sources panel
    plot_wizard.py       # create plot
    grid_board.py        # grid canvas & PlotTile (drag/drop)
    dialogs.py           # export, NA handling, type confirmation
  assets/
    icons/
  tests/
    test_inference.py
    test_group_expand.py
    test_export.py
  README.md
```

---

## 12) Key UI Flows (Text Wireframes)

**Main Window**
- Menu: File (New, Open, Save, Save As…), Data (Add CSV…), Plot (New Plot…), Grid (+Row, +Col, -Row, -Col), Export (Grid…, Selected Plot…).
- Left Dock: **Data Sources** list → right‑click (Reload, Rename, Remove).
- Right Dock: **Plots** list → select to edit spec; double‑click to open properties.
- Center: **GridBoard** with `r×c` cells. Drag PlotTile headers to rearrange.

**Add CSV** → opens Load Wizard (Sections 4.1–4.2).

**New Plot** → opens Plot Wizard (Section 5.1). After Create, instances appear in a temporary tray to be placed, or auto‑placed into first available blanks.

**Export Grid** → opens Export Dialog (Section 8.1).

---

## 13) Algorithms & Calculations

- **Group Expansion**: For groups `[g1, g2, ...]`, compute unique sets `U(g1), U(g2), ...`; form Cartesian product; if product size > 50, block and prompt to refine.
- **Shared Axes**: For instances in the group set, compute min/max on filtered data (omit NA) and assign `ax.set_xlim/ylim` consistently.
- **Missing Value Actions**: Apply user‑selected actions in order: drop specific columns, then drop rows by per‑column NA policy.
- **Type Inference**: Use heuristics + user overrides; store final `var_type` in schema for future validation and GUI hints.

---

## 14) Extensibility Points (Roadmap)

- **Multi‑Y** (dual axis): extend `PlotSpec` to allow `y2`, `twinx` rendering.
- **More plot types**: bar, scatter, area; attach `plot_kind` enum and per‑kind renderers.
- **Transforms**: computed columns (rolling mean, resample), saved as part of DataSource pipeline.
- **Filters**: quick filter builder per plot instance.
- **Theme**: global light/dark toggle; save in project.
- **Resizing/Spanning**: variable cell sizes and row/col spanning.
- **Packaging**: PyInstaller one‑file distribution.

---

## 15) Milestones & Estimates

**M1 – Skeleton & Data (3–4 days)**
- Project scaffolding, models, project save/load.
- CSV Load Wizard with NA handling + type confirmation.

**M2 – Plotting Core (3–4 days)**
- Plot wizard, group expansion with 50‑cap, `PlotTile` rendering, hue legend.

**M3 – Grid Board (2–3 days)**
- Add/remove rows/cols, drag‑and‑drop between cells, duplicate/clear.

**M4 – Export (2 days)**
- Whole‑grid export (PDF/SVG/EPS/PNG) and per‑plot export; size/DPI dialog.

**M5 – Polish (2 days)**
- Error handling, toasts, status bar, docs, tests (inference, grouping, export).

---

## 16) Minimal Code Sketches (Illustrative)

> _Note: These are conceptual and omit error checks for brevity._

### 16.1 Dataclasses
```python
@dataclass
class ColumnSchema:
    name: str
    dtype: str
    var_type: Literal['categorical','continuous','ordinal']
    categories: list[str] | None = None

@dataclass
class DataSource:
    id: str
    name: str
    path: str
    dataframe: pd.DataFrame
    schema: list[ColumnSchema]

@dataclass
class PlotSpec:
    id: str
    datasource_id: str
    x: str
    y: str
    hue: str | None
    groups: list[str]
    title: str | None = None
    share_axes: bool = False
    style_overrides: dict[str, Any] = field(default_factory=dict)
```

### 16.2 Group Expansion
```python
def expand_groups(df: pd.DataFrame, groups: list[str]) -> list[dict[str, Any]]:
    if not groups:
        return [{}]
    uniques = [sorted(df[g].dropna().unique().tolist()) for g in groups]
    combos = [dict(zip(groups, vals)) for vals in itertools.product(*uniques)]
    if len(combos) > 50:
        raise ValueError("Too many combinations (>50). Reduce groups or categories.")
    return combos
```

### 16.3 Shared Axis Compute
```python
def shared_limits(subsets: list[pd.DataFrame], x: str, y: str) -> tuple[tuple[float,float], tuple[float,float]]:
    xmins, xmaxs, ymins, ymaxs = [], [], [], []
    for sub in subsets:
        if sub.empty:
            continue
        xmins.append(pd.to_numeric(sub[x], errors='coerce').min())
        xmaxs.append(pd.to_numeric(sub[x], errors='coerce').max())
        ymins.append(pd.to_numeric(sub[y], errors='coerce').min())
        ymaxs.append(pd.to_numeric(sub[y], errors='coerce').max())
    return (min(xmins), max(xmaxs)), (min(ymins), max(ymaxs))
```

---

## 17) Testing Strategy
- **Unit**: type inference heuristics, group expansion cap, shared axis calculation, export file presence.
- **Integration**: load → create plot → place in grid → export.
- **Manual**: big CSVs, datetime axes, empty group combos, NA workflows.

---

## 18) Dependencies
- `pandas`, `numpy`, `matplotlib`, `PySide6`.
- Dev/test: `pytest`.

---

## 19) Risks & Mitigations
- **Large CSV performance** → Threaded loading; optional downsampling; show progress.
- **Axis sharing correctness** → compute after filters; ignore empty subsets.
- **User confusion on grouping** → Preview combo count & values before create.
- **File path portability** → store relative paths; relink dialog if missing.

---

## 20) Definition of Done (v1)
- Can load multiple CSVs with GUI NA & type confirmation.
- Can create line plots with (x, y, optional hue) from a single data source.
- Can facet by groups into ≤50 independent plots, placed in a grid.
- Can add/remove rows/cols, and drag plots between cells.
- Can export entire grid to PDF/SVG/EPS/PNG with correct shared axes and layout.
- Project save/load round‑trips state successfully.
