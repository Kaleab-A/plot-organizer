# API Grouped Plots Feature

## Problem Statement

In the GUI, users can select "group" columns and the system automatically:
1. Creates multiple plots (one per unique combination of group values)
2. Computes shared y-axis limits across all plots
3. Places plots in the grid

**But the original API was missing this feature!** Users had to:
- Manually create each plot with `create_plot()`
- Manually specify `filter_query` for each combination
- Manually compute and specify `ylim` for all plots
- This was tedious and error-prone

## Solution

Added two new API functions that replicate the GUI's groups workflow:

### 1. `create_grouped_plots()` - Core Function

Creates multiple plots from group columns with auto-computed shared y-axis limits.

**Signature:**
```python
def create_grouped_plots(
    datasource_id: str,
    dataframe_path: str,  # Needed to compute limits
    x: str,
    y: str,
    groups: list[str],  # Group columns
    *,
    start_row: int = 0,
    start_col: int = 0,
    layout: str = "row",  # "row" or "col"
    hue: str | list[str] | None = None,
    sem_column: str | None = None,
    sem_precomputed: bool = False,
    hlines: list[float] | None = None,
    vlines: list[float] | None = None,
    style_line: bool = True,
    style_marker: bool = False,
    ylim: tuple[float, float] | list[float] | None = None,
) -> list[dict[str, Any]]
```

**What it does:**
1. Loads the CSV to access the data
2. Calls `expand_groups()` to get all filter query combinations
3. Computes shared xlim/ylim using `shared_limits()` or `shared_limits_with_sem()`
4. Creates one plot per combination with auto-positioning
5. All plots share the same computed ylim
6. Returns list of plot dicts ready for `create_project()`

**Example:**
```python
from plot_organizer.api import *

ds = create_datasource("Experiment", "data/results.csv")

# Create 6 plots (3 species × 2 treatments)
# All with shared y-axis limits
plots = create_grouped_plots(
    datasource_id=ds["id"],
    dataframe_path="data/results.csv",
    x="time",
    y="accuracy",
    groups=["species", "treatment"],
    hue=["model"],
    layout="row"
)

project = create_project((2, 3), [ds], plots)
save_project_file(project, "experiment.ppo")
```

### 2. `quick_grouped_project()` - Convenience Wrapper

One-liner to create a complete project with grouped plots.

**Signature:**
```python
def quick_grouped_project(
    datasource_name: str,
    datasource_path: str,
    x: str,
    y: str,
    groups: list[str],
    **kwargs  # Passed to create_grouped_plots()
) -> dict[str, Any]
```

**Example:**
```python
from plot_organizer.api import *

# Single function call!
project = quick_grouped_project(
    datasource_name="Experiment",
    datasource_path="data/results.csv",
    x="time",
    y="accuracy",
    groups=["species", "treatment"],
    hue=["model"],
)

save_project_file(project, "experiment.ppo")
```

## Key Features

### ✅ Auto-computed Shared Limits
- If `ylim` is not provided, automatically computes shared limits
- Uses `shared_limits()` for regular plots
- Uses `shared_limits_with_sem()` when SEM column is present
- Ensures all grouped plots have the same y-axis for easy comparison

### ✅ Auto-positioning
- `layout="row"`: Places plots left-to-right
- `layout="col"`: Places plots top-to-bottom
- Specify `start_row` and `start_col` to control where plots begin

### ✅ Auto-titles
- Titles are generated from filter queries
- Format: `"species=A, treatment=X"`
- Makes it easy to identify each plot

### ✅ Manual Override
- Can specify `ylim` manually to override auto-computation
- Useful when you want specific axis ranges

### ✅ Works with All Features
- Multi-column hue
- SEM (computed or pre-computed)
- Reference lines (hlines, vlines)
- Plot styles (line, markers, or both)
- Filter queries (automatically generated from groups)

## Implementation Details

### How Shared Limits Are Computed

1. **Load CSV** - Temporarily loads dataframe from path
2. **Expand groups** - Calls `expand_groups(df, groups)` to get filter queries
3. **Compute limits**:
   - If SEM column: Uses `shared_limits_with_sem()` which accounts for SEM bands
   - Otherwise: Uses `shared_limits()` on filtered subsets
4. **Create plots** - Each plot uses the same computed ylim
5. **Discard dataframe** - Only keeps the computed limits, not the data

### Why `dataframe_path` Parameter?

The function needs access to the actual data to compute limits, but:
- The API works with file paths (not in-memory DataFrames)
- Loading the CSV is necessary to compute statistics
- The dataframe is only used temporarily and discarded

This design keeps the API JSON-based while enabling smart limit computation.

## Comparison: Before vs After

### Before (Manual)

```python
# Had to manually:
# 1. Load data and compute combinations
# 2. Compute shared limits yourself
# 3. Create each plot manually

df = pd.read_csv("data.csv")
combos = [
    {"species": "A", "treatment": "X"},
    {"species": "A", "treatment": "Y"},
    {"species": "B", "treatment": "X"},
    {"species": "B", "treatment": "Y"},
]

# Manually compute shared ylim
subsets = [df[...] for combo in combos]
ylim = (min(...), max(...))  # Complex calculation

# Manually create plots
plots = [
    create_plot("", x="time", y="value", 
                filter_query=combos[0], ylim=ylim, row=0, col=0, title="..."),
    create_plot("", x="time", y="value",
                filter_query=combos[1], ylim=ylim, row=0, col=1, title="..."),
    create_plot("", x="time", y="value",
                filter_query=combos[2], ylim=ylim, row=0, col=2, title="..."),
    create_plot("", x="time", y="value",
                filter_query=combos[3], ylim=ylim, row=0, col=3, title="..."),
]
```

### After (Automatic)

```python
# One function call!
plots = create_grouped_plots(
    "ds123",
    "data.csv",
    x="time",
    y="value",
    groups=["species", "treatment"]
)

# Or even simpler:
project = quick_grouped_project(
    "Experiment",
    "data.csv",
    x="time",
    y="value",
    groups=["species", "treatment"]
)
```

## Testing

Added 4 comprehensive tests in `test_programmatic_api.py`:

1. **`test_create_grouped_plots`** - Basic functionality with shared limits
2. **`test_create_grouped_plots_column_layout`** - Column layout positioning
3. **`test_create_grouped_plots_with_manual_ylim`** - Manual ylim override
4. **`test_quick_grouped_project`** - Convenience wrapper

**All 111 tests pass** (107 existing + 4 new)

## Usage Examples

### Example 1: Simple Grouped Plots

```python
from plot_organizer.api import *

project = quick_grouped_project(
    datasource_name="Results",
    datasource_path="data/results.csv",
    x="time",
    y="accuracy",
    groups=["species"],  # One group column
)

save_project_file(project, "by_species.ppo")
```

### Example 2: Multi-Group with Hue

```python
project = quick_grouped_project(
    datasource_name="Results",
    datasource_path="data/results.csv",
    x="time",
    y="accuracy",
    groups=["species", "treatment"],  # 2 group columns
    hue=["model", "dataset"],  # Multi-column hue
)

save_project_file(project, "grouped_with_hue.ppo")
```

### Example 3: With SEM and Reference Lines

```python
project = quick_grouped_project(
    datasource_name="Results",
    datasource_path="data/results.csv",
    x="time",
    y="accuracy",
    groups=["species"],
    sem_column="trial",
    hlines=[0.5, 0.9],
    vlines=[10, 20],
    style_line=True,
    style_marker=True,
)

save_project_file(project, "with_sem.ppo")
```

### Example 4: Manual Control

```python
ds = create_datasource("Results", "data/results.csv")

# Create grouped plots with full control
plots = create_grouped_plots(
    datasource_id=ds["id"],
    dataframe_path="data/results.csv",
    x="time",
    y="accuracy",
    groups=["species", "treatment"],
    start_row=1,  # Start at row 1
    start_col=2,  # Start at column 2
    layout="col",  # Vertical stacking
    ylim=(0, 1),  # Manual y-limits
)

# Add more plots
more_plots = [
    create_plot(ds["id"], x="time", y="loss", row=0, col=0)
]

# Combine
project = create_project((5, 5), [ds], plots + more_plots)
save_project_file(project, "manual_control.ppo")
```

## Files Modified

1. **`plot_organizer/api.py`** - Added `create_grouped_plots()` and `quick_grouped_project()`
2. **`plot_organizer/tests/test_programmatic_api.py`** - Added 4 new tests
3. **`examples/README.md`** - Added documentation and examples

## Summary

The new grouped plots API feature:
- ✅ Replicates GUI's groups functionality
- ✅ Auto-computes shared y-axis limits
- ✅ Auto-positions plots in grid
- ✅ Auto-generates titles
- ✅ Works with all features (SEM, hue, reference lines, etc.)
- ✅ Simple one-liner for common use cases
- ✅ Full control when needed
- ✅ Comprehensive test coverage

This makes programmatic plot generation as powerful and convenient as the GUI!

