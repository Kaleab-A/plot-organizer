# Changes v0.7 – Pre-computed SEM Support

_Date: 2025-10-12_

## Overview

Added support for using pre-computed SEM (Standard Error of the Mean) values directly from a data column. Users can now toggle between two modes: computing SEM from grouped data or using pre-computed SEM values that are already present in their dataset.

---

## What's New

### 1. Pre-computed SEM Checkbox

**File**: `plot_organizer/ui/dialogs.py`

Added a "Pre-computed SEM" checkbox in the Quick Plot Dialog, placed right after the SEM column dropdown.

**Behavior**:
- **Unchecked** (default): Computed SEM mode - groups data by SEM column, then computes mean and SEM across groups
- **Checked**: Pre-computed SEM mode - uses SEM values directly from the selected column

**UI Changes**:
- Info label updates dynamically based on checkbox state
- Unchecked: "SEM column: Groups data before averaging, then computes mean ± SEM as shaded region"
- Checked: "SEM column: Uses pre-computed SEM values from selected column"

### 2. Automatic Aggregation with Warnings

**File**: `plot_organizer/ui/grid_board.py`

When using pre-computed SEM mode, if multiple rows exist for the same x-value:
- Automatically averages both y-values and SEM values
- Logs a warning to inform the user:
  ```
  WARNING: Multiple rows found for some x-values. 
  Averaged y-values and SEM values for plotting. 
  Consider pre-aggregating your data.
  ```

This ensures the tool can handle both:
- **Ideal case**: One row per (x, hue, groups) combination with pre-computed SEM
- **General case**: Multiple rows that need averaging

### 3. New Plotting Method

**File**: `plot_organizer/ui/grid_board.py`

Added `_plot_with_precomputed_sem()` method:
```python
def _plot_with_precomputed_sem(self, ax, df, x, y, sem_column, label=None):
    """Plot data with pre-computed SEM values from a column.
    
    If multiple rows exist for same x-value:
    - Average y-values
    - Average SEM values
    - Show warning to user
    """
```

**Features**:
- Aggregates by x using mean for both y and SEM columns
- Detects duplicates and logs warnings
- Plots mean line with SEM shaded region
- Uses same visual style as computed SEM (20% opacity, matching color)

### 4. Updated `_plot_with_sem` Method

Modified the existing `_plot_with_sem()` method to branch based on mode:
```python
if sem_column and sem_column in df.columns:
    if self._sem_precomputed:
        # Pre-computed mode
        self._plot_with_precomputed_sem(ax, df, x, y, sem_column, label)
    else:
        # Computed mode (existing logic)
        ...
```

### 5. Shared Limits Support

**File**: `plot_organizer/services/plot_service.py`

Updated `shared_limits_with_sem()` to handle pre-computed mode:
- Added `sem_precomputed` parameter
- Created `_compute_precomputed_sem_stats()` helper function
- Branches to appropriate stats computation based on mode

**New Helper Function**:
```python
def _compute_precomputed_sem_stats(df, x, y, sem_column):
    """Helper to compute mean ± pre-computed SEM values.
    
    Averages y and SEM values if multiple rows exist for same x.
    Returns (lower_bounds, upper_bounds) where lower = mean - SEM
    and upper = mean + SEM for each x value.
    """
```

### 6. Export Support

**File**: `plot_organizer/services/export_service.py`

Updated `_render_plot_to_ax()` to handle pre-computed SEM in exports:
- Accesses `tile._sem_precomputed` flag
- Branches export logic based on mode
- Ensures exported plots match on-screen display

### 7. Pipeline Integration

**File**: `plot_organizer/ui/main_window.py`

- Extracts `sem_precomputed` from dialog selection
- Passes flag through to all plotting and limit calculation functions
- Maintains full integration with grouped plots and faceting

---

## Technical Details

### Modified Files

1. **`plot_organizer/ui/dialogs.py`**
   - Added `QCheckBox` import
   - Added `precomputed_sem_check` widget
   - Added `_update_sem_info()` method
   - Updated `selection()` to return `sem_precomputed` flag

2. **`plot_organizer/ui/grid_board.py`**
   - Added `_sem_precomputed` instance variable
   - Updated `set_plot()` signature with `sem_precomputed` parameter
   - Modified `_plot_with_sem()` to branch by mode
   - Added `_plot_with_precomputed_sem()` method
   - Updated `clear_plot()` to reset flag

3. **`plot_organizer/ui/main_window.py`**
   - Extracts `sem_precomputed` from selection
   - Passes to `shared_limits_with_sem()`
   - Passes to `tile.set_plot()`

4. **`plot_organizer/services/plot_service.py`**
   - Added `sem_precomputed` parameter to `shared_limits_with_sem()`
   - Added `_compute_precomputed_sem_stats()` helper function
   - Conditional logic to use appropriate stats computation

5. **`plot_organizer/services/export_service.py`**
   - Accesses `tile._sem_precomputed`
   - Conditional rendering based on mode

### Data Flow

```
User checks "Pre-computed SEM" checkbox
    ↓
QuickPlotDialog.selection() returns {"sem_precomputed": True}
    ↓
MainWindow extracts flag and passes to:
    - shared_limits_with_sem(sem_precomputed=True)
    - tile.set_plot(sem_precomputed=True)
    ↓
PlotTile stores flag: self._sem_precomputed = True
    ↓
_plot_with_sem() branches to _plot_with_precomputed_sem()
    ↓
Aggregates data: groupby(x).agg({y: 'mean', sem: 'mean'})
    ↓
Logs warning if duplicates were averaged
    ↓
Plots mean line + SEM shaded region
```

---

## Use Cases

### Use Case 1: Pre-aggregated Scientific Data

You have data already aggregated with SEM computed:
```python
data = {
    'time': [0, 1, 2, 3, 4],
    'accuracy': [0.65, 0.72, 0.78, 0.82, 0.85],
    'sem': [0.03, 0.025, 0.02, 0.018, 0.015]
}
```

**Workflow**:
1. Select `time` as x, `accuracy` as y
2. Select `sem` as SEM column
3. **Check** "Pre-computed SEM"
4. Plot shows accuracy with ±SEM shaded region

### Use Case 2: Summary Statistics from External Tool

You computed statistics in R/MATLAB/Excel:
```python
data = {
    'dose': [10, 20, 30, 40, 50],
    'mean_response': [12.5, 18.2, 24.7, 29.1, 31.5],
    'standard_error': [1.2, 1.5, 1.8, 2.0, 2.1]
}
```

**Workflow**:
1. x: `dose`, y: `mean_response`
2. SEM column: `standard_error`
3. **Check** "Pre-computed SEM"
4. Creates dose-response curve with error bars

### Use Case 3: Mixed Data (needs averaging)

You have some duplicate x-values with pre-computed SEMs:
```python
data = {
    'x': [1, 1, 2, 3],  # Duplicate x=1
    'y': [10, 12, 20, 30],
    'sem': [1.0, 1.5, 2.0, 3.0]
}
```

**Behavior**:
- Automatically averages: x=1 → y=11, sem=1.25
- Logs warning about averaging
- Plots correctly with averaged values

---

## Testing

### New Test File: `test_precomputed_sem.py`

**11 comprehensive tests**:

1. **`test_precomputed_sem_single_row_per_x`**
   - Ideal case: one row per x-value
   - Verifies flag is set and plot is created

2. **`test_precomputed_sem_duplicate_x_values`**
   - Multiple rows per x-value
   - Verifies averaging occurs correctly

3. **`test_precomputed_sem_with_hue`**
   - Pre-computed SEM with hue grouping
   - Verifies multiple lines and SEM regions

4. **`test_precomputed_sem_vs_computed_sem`**
   - Compares both modes
   - Verifies they produce different results

5. **`test_precomputed_sem_clear_plot`**
   - Verifies flag is reset on clear

6. **`test_precomputed_sem_shared_limits`**
   - Tests limit calculation with pre-computed SEM

7. **`test_precomputed_sem_with_nan_values`**
   - Handles NaN SEM values gracefully

8. **`test_precomputed_sem_zero_values`**
   - Handles zero SEM values

9. **`test_backward_compatibility_default_computed`**
   - Verifies default is computed mode

10. **`test_precomputed_sem_checkbox_state`**
    - Tests checkbox state management

11. **`test_precomputed_sem_info_label_updates`**
    - Tests dynamic info label updates

**Test Coverage**: All 54 tests pass (43 existing + 11 new)

---

## User-Facing Changes

### Dialog Changes

**Before v0.7**:
```
SEM column (optional): [dropdown]
Info: Groups data before averaging...
```

**After v0.7**:
```
SEM column (optional): [dropdown]
☐ Pre-computed SEM
Info: (changes based on checkbox)
```

### Visual Changes

No visual differences in the plots themselves - both modes produce identical-looking plots with mean lines and SEM shaded regions. The difference is in how the data is processed.

### Warnings

Users now see warnings when pre-computed mode averages duplicate rows:
```
WARNING:root:Multiple rows found for some x-values. Averaged y-values and SEM values for plotting. Consider pre-aggregating your data.
```

---

## Backward Compatibility

✅ **Fully backward compatible**

- Checkbox unchecked by default (existing behavior)
- Computed SEM mode unchanged
- All existing plots and workflows work exactly as before
- New parameter optional everywhere (defaults to `False`)
- All 43 existing tests still pass

---

## Edge Cases Handled

1. **Duplicate x-values**: Automatically averaged with warning
2. **NaN SEM values**: Filled with 0, plot created successfully
3. **Zero SEM values**: Creates valid (but flat) shaded region
4. **Empty data**: Handled gracefully (no plot, no crash)
5. **Mixed with hue**: Each hue category gets its own SEM region
6. **Mixed with groups**: Pre-computed mode works with faceting
7. **Shared limits**: Correctly accounts for mean ± SEM bounds

---

## Design Decisions

1. **Checkbox over dropdown**: Simpler UX for binary choice
2. **Default unchecked**: Preserves existing behavior
3. **Average on duplicates**: Handles general case, warns user
4. **Python logging**: Standard warning mechanism, visible in console
5. **Same visual style**: Consistent look between both modes
6. **No validation**: If column has numbers, use them (flexible)

---

## Future Enhancements

Potential improvements:

1. **Choice of aggregation function**: Allow median instead of mean
2. **Confidence intervals**: Support for 95% CI instead of SEM
3. **Asymmetric errors**: Different upper/lower bounds
4. **Error bar style**: Option for bars instead of shaded regions
5. **Custom warning dialog**: GUI warning instead of console log
6. **Data validation**: Check if SEM values are reasonable

---

## Summary

v0.7 adds flexible pre-computed SEM support to the Plot Organizer, allowing users to bring their own pre-computed error estimates. The implementation gracefully handles both ideally pre-aggregated data and cases requiring additional averaging, with clear warnings to guide users toward best practices.

**Key Features**:
- Toggle between computed and pre-computed SEM modes
- Automatic averaging with warnings for duplicate x-values
- Full integration with hue, groups, and shared limits
- Export support for both modes
- Comprehensive test coverage

**Key Metrics**:
- 54/54 tests passing ✅
- 100% backward compatible
- 5 files modified
- 1 new helper function
- 11 new tests

