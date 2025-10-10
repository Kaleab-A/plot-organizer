# Changes in v0.2

## Summary

Implemented group faceting feature and cleaned up the UI for maximum plot space.

## Features Added

### 1. Group Faceting (✅ Complete)
- Multi-select group columns in the Create Plot dialog
- Automatically expands groups using cross-product of unique values
- Creates one plot per unique combination (capped at 50 to prevent performance issues)
- Each faceted plot shows its filter values in the title (e.g., "Country=USA, Industry=Tech")

### 2. Shared Axes (✅ Complete)
- When creating grouped plots, all plots automatically share the same x/y axis limits
- Makes it easy to compare values across different facets
- Uses `shared_limits()` from `plot_service.py` to compute global min/max

### 3. UI Cleanup (✅ Complete)
- **Removed navigation toolbar** (pan/zoom/save buttons) from each plot tile
- **Removed header text** above each plot
- **Minimized margins** (2px) to maximize plot space
- Plots now use `tight_layout=True` for better space utilization
- Title (if present) is now rendered inside the plot using Matplotlib's `ax.set_title()`

## Files Modified

### `plot_organizer/ui/grid_board.py`
- Removed `NavigationToolbar` widget from `PlotTile`
- Removed header `QLabel` widget
- Added `tight_layout=True` to Figure
- Reduced margins to 2px with 0 spacing
- Added `filter_query`, `xlim`, `ylim` parameters to `set_plot()`
- Filter is applied before plotting (subset dataframe by group values)
- Empty plots show "No data" message

### `plot_organizer/ui/dialogs.py`
- Renamed dialog from "Quick Plot" to "Create Plot"
- Added multi-select `QListWidget` for group columns
- Added combo count label to show how many group columns are selected
- Updated `selection()` to return `groups` list
- Added `_update_combo_count()` to provide user feedback

### `plot_organizer/ui/main_window.py`
- Imported `expand_groups` and `shared_limits` from `plot_service`
- Updated `_action_quick_plot()` to handle groups:
  - Call `expand_groups()` to get filter queries
  - Catch `ValueError` if > 50 combinations and show warning
  - Compute shared limits if multiple plots are generated
  - Loop through filter queries and create one plot per combination
  - Build title from filter query (e.g., "Country=USA")
  - Pass `filter_query`, `xlim`, `ylim` to each tile

### Documentation
- Updated `IMPLEMENTATION_PROGRESS.md` to v0.2 with group faceting features
- Updated `QUICKSTART.md` with group usage examples
- Created `CHANGES_v0.2.md` (this file)

### Tests
- Created `plot_organizer/tests/test_integration.py` with 6 tests:
  - No groups (returns single empty dict)
  - Single group column
  - Two group columns (cartesian product)
  - Exceeds 50 limit (raises ValueError)
  - Shared limits computation
  - Shared limits with empty dataframes

## How to Use

1. **Simple plot** (no groups):
   - Plot → Create Plot…
   - Select x, y, optional hue
   - Click OK → single plot

2. **Faceted plot** (with groups):
   - Plot → Create Plot…
   - Select x, y, optional hue
   - Multi-select one or more columns in the Groups list
   - Click OK → multiple plots (one per unique combination)
   - All plots share same axis ranges

## Example

Using `organizations-10000.csv`:
- x: `Index`
- y: `Number of employees`
- Groups: Select `Industry` (creates one plot per industry)
- Result: Multiple plots, all with same y-axis scale for comparison

## Technical Notes

- Group expansion uses `itertools.product()` for Cartesian product
- Shared limits computed by finding min/max across all filtered subsets
- Filter queries are dictionaries like `{"Country": "USA", "Industry": "Tech"}`
- Empty combinations (no matching rows) show "No data" placeholder
- Plots automatically place in first empty grid cell; new rows added as needed

## What's Next

- Drag-and-drop to rearrange plots
- Whole-grid export to PDF/SVG/PNG
- Project save/load
- Advanced CSV loading wizard (NA handling, type confirmation)

