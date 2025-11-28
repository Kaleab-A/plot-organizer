# Bug Fix: Grid Dimensions Not Preserved

## Issue
When saving a project with a sparse grid (e.g., 2×3 grid with only 2 plots), loading it back would resize the grid to fit only the plots (e.g., 2×1 or 1×2) instead of preserving the original grid dimensions.

### Example
1. Create a 2×3 grid in GUI
2. Add plots only to cells (0,0) and (0,1)
3. Save the project
4. Load the project back
5. **Bug**: Grid is now 1×2 instead of 2×3

## Root Cause
The `save_workspace()` function was computing grid dimensions from plot positions instead of saving the actual grid size:

```python
# Old code - computes from plots
if grid_layout:
    rows = max((p["grid_position"]["row"] + p["grid_position"]["rowspan"] 
                for p in grid_layout), default=2)
    cols = max((p["grid_position"]["col"] + p["grid_position"]["colspan"] 
                for p in grid_layout), default=3)
```

This meant:
- A 2×3 grid with plots at (0,0) and (0,1) would compute to 1×2
- A 3×4 grid with plots at (0,0) and (2,3) would compute to 3×4 (correct by accident)
- Empty grids would get the default 2×3

## The Fix

### 1. Updated `save_workspace()` signature
Added explicit `grid_rows` and `grid_cols` parameters:

```python
def save_workspace(
    path: str,
    grid_layout: list[dict[str, Any]],
    data_sources: dict[str, dict[str, Any]],
    grid_rows: int,  # NEW
    grid_cols: int,  # NEW
) -> None:
```

### 2. Updated `MainWindow._save_to_path()`
Pass actual grid dimensions from GridBoard:

```python
save_workspace(
    path,
    grid_layout,
    datasource_info,
    grid_rows=self.grid_board._rows,  # Actual grid dimensions
    grid_cols=self.grid_board._cols
)
```

### 3. Added regression test
Created `test_sparse_grid_preserves_dimensions()` that:
- Creates a 3×4 grid with only 2 plots
- Saves and loads the project
- Verifies grid dimensions are preserved as 3×4

## Impact

✅ **Before fix**: Grid would shrink to fit only the plots
✅ **After fix**: Grid dimensions are preserved exactly as they were

This ensures that:
- Users can maintain their preferred grid layout
- Empty cells are preserved for future use
- Grid organization is not lost between save/load cycles

## Files Changed

- `plot_organizer/services/project_service.py` - Added grid dimension parameters
- `plot_organizer/ui/main_window.py` - Pass actual grid dimensions
- `plot_organizer/tests/test_project_save_load.py` - Updated all test calls, added regression test

## Test Coverage

✅ All 107 tests pass (106 existing + 1 new)
✅ New test specifically covers sparse grid scenario

## Status
✅ Fixed and tested

