# Changes v0.5 – SEM (Standard Error of the Mean) Feature

_Date: 2025-10-10_

## Overview

Added comprehensive support for plotting Standard Error of the Mean (SEM) with shaded regions around mean lines. This feature allows users to visualize variability in their data by grouping observations before computing statistics.

---

## What's New

### 1. SEM Column Selection in Quick Plot Dialog

**File**: `plot_organizer/ui/dialogs.py`

- Added `sem_combo` QComboBox to the Quick Plot Dialog
- Placed after hue selection with "(none)" as default
- Added informative label explaining SEM functionality
- Validation ensures SEM column doesn't conflict with x, y, hue, or group columns
- Clear error message if user tries to select a conflicting column

**User Experience**:
```
Quick Plot Dialog:
  Data Source: [dropdown]
  x: [dropdown]
  y: [dropdown]
  hue (optional): [dropdown]
  SEM column (optional): [dropdown]  ← NEW!
  Groups (faceting): [multi-select list]
```

### 2. SEM Computation Algorithm

**Files**: 
- `plot_organizer/ui/grid_board.py` (PlotTile class)
- `plot_organizer/services/export_service.py`

**Algorithm**:
1. **Group by SEM column first**: Groups all data points by the SEM column (e.g., subject ID, trial number)
2. **Compute within-group means**: For each (SEM group, x-value) pair, compute the mean of y
3. **Aggregate across SEM groups**: For each x-value, compute:
   - Overall mean across all SEM groups
   - Standard Error of the Mean (SEM) across groups using pandas `.agg(['mean', 'sem'])`
4. **Plot with shaded region**: 
   - Plot mean as a line
   - Fill between (mean - SEM) and (mean + SEM) with 20% opacity
   - Use matching color for hue-based plots

**Example**:
```python
# Data with multiple observations per x-value from different subjects
data = {
    'x': [1, 1, 1, 2, 2, 2],
    'y': [10, 12, 14, 20, 22, 24],
    'subject': ['s1', 's2', 's3', 's1', 's2', 's3']
}

# With sem_column='subject':
# x=1: subjects have means [11, 13, 15] → overall mean=13, SEM computed
# x=2: subjects have means [21, 23, 25] → overall mean=23, SEM computed
```

### 3. Integration with Existing Features

**Works with Hue**:
- When hue is specified, each hue category gets its own line + SEM shaded region
- Shaded regions use matching colors with transparency
- Legend shows hue categories (not SEM)

**Works with Groups**:
- SEM computation applies to each faceted plot independently
- Shaded regions appear in all group-generated plots

**Preserved during Export**:
- `export_service.py` updated to render SEM regions correctly
- PDF/SVG/EPS exports include shaded regions
- PNG exports include shaded regions with proper anti-aliasing

### 4. New Helper Method: `_plot_with_sem`

**File**: `plot_organizer/ui/grid_board.py`

```python
def _plot_with_sem(ax, df, x, y, sem_column, label=None):
    """Plot data with optional SEM shaded region.
    
    If sem_column is provided:
    1. Group by sem_column first
    2. Compute mean within each group
    3. Then aggregate across sem_column groups to get overall mean and SEM
    """
```

**Features**:
- Automatically falls back to simple mean if `sem_column` is None
- Handles missing SEM values gracefully (checks for NaN)
- Extracts line color for matching shaded region
- Uses `ax.fill_between()` for smooth, professional-looking regions

---

## Technical Details

### Modified Files

1. **`plot_organizer/ui/dialogs.py`**
   - Added `sem_combo` widget
   - Updated column population logic
   - Added validation in `selection()` method

2. **`plot_organizer/ui/grid_board.py`**
   - Added `_sem_column` instance variable to PlotTile
   - Modified `set_plot()` signature to accept `sem_column` parameter
   - Created `_plot_with_sem()` helper method
   - Updated `clear_plot()` to reset `_sem_column`

3. **`plot_organizer/ui/main_window.py`**
   - Extracted `sem_column` from dialog selection
   - Passed `sem_column` to `tile.set_plot()`

4. **`plot_organizer/services/export_service.py`**
   - Updated `_render_plot_to_ax()` to handle SEM column
   - Duplicated SEM computation logic for export consistency

### Data Flow

```
User selects SEM column
    ↓
QuickPlotDialog.selection() validates and returns sem_column
    ↓
MainWindow passes sem_column to PlotTile.set_plot()
    ↓
PlotTile._plot_with_sem() computes and renders mean ± SEM
    ↓
ExportService._render_plot_to_ax() replicates rendering for export
```

---

## Testing

### New Test File: `test_sem_plotting.py`

**5 comprehensive tests**:

1. **`test_sem_column_grouping_and_aggregation`**
   - Verifies SEM column groups data correctly
   - Checks that shaded region is rendered (via `ax.collections`)

2. **`test_sem_with_hue`**
   - Tests SEM computation with hue grouping
   - Verifies multiple lines and legend

3. **`test_no_sem_column`**
   - Ensures backward compatibility when `sem_column=None`
   - Confirms no shaded regions appear

4. **`test_sem_computation_correctness`**
   - Validates numerical accuracy of mean computation
   - Tests a case where SEM should be zero

5. **`test_sem_with_varying_values`**
   - Tests actual variance across SEM groups
   - Verifies mean and shaded region with real variability

**Test Coverage**: All 29 tests pass (24 existing + 5 new)

---

## User-Facing Changes

### Visual Changes

- **Before**: Line plots showed only means
- **After**: Line plots can show mean with ±1 SEM as a translucent shaded region

### Dialog Changes

- **Quick Plot Dialog** now has 4th row: "SEM column (optional)"
- Helpful hint text: "SEM column: Groups data before averaging, then shows mean ± SEM as shaded region"

### Validation

- Error message if SEM column conflicts with x, y, hue, or groups:
  ```
  "SEM column 'subject' is already used as x, y, hue, or group.
   Please select a different column."
  ```

---

## Examples of Use Cases

### 1. Experimental Data with Subjects

```
CSV columns: time, accuracy, subject_id
- x: time
- y: accuracy
- sem_column: subject_id
→ Shows average accuracy over time with variability across subjects
```

### 2. Multiple Trials per Condition

```
CSV columns: dose, response, trial, condition
- x: dose
- y: response
- hue: condition
- sem_column: trial
→ Multiple lines (one per condition) each with SEM shaded region
```

### 3. Time Series with Replicates

```
CSV columns: timestamp, measurement, replicate_id
- x: timestamp
- y: measurement
- sem_column: replicate_id
→ Shows temporal trend with measurement variability
```

---

## Known Limitations

1. **Only supports mean ± SEM**: 
   - No support for other error measures (SD, CI) in v0.5
   - Future: could add dropdown to choose error type

2. **Assumes equal weighting**:
   - All SEM groups are weighted equally
   - Future: could support weighted means

3. **No customization of shaded region**:
   - Opacity fixed at 20%
   - Color always matches line color
   - Future: could add style controls in plot settings

---

## Backward Compatibility

✅ **Fully backward compatible**

- `sem_column` is optional (defaults to `None`)
- Existing code that doesn't use SEM continues to work
- All previous tests still pass
- Export functionality preserves old behavior when `sem_column=None`

---

## Performance Notes

- **Groupby operations**: Two-level grouping (SEM column + x) is efficient for typical datasets
- **Rendering**: `fill_between()` is optimized in Matplotlib
- **Export**: SEM regions add minimal overhead to export time

---

## Documentation Updates

1. **IMPLEMENTATION_PROGRESS.md**: Added v0.5 section
2. **QUICKSTART.md**: 
   - Added SEM column to plot creation steps
   - Updated "What's Implemented" checklist
3. **This file**: Comprehensive changelog

---

## Future Enhancements

Potential improvements for future versions:

1. **Error type selection**: Dropdown to choose SEM, SD, or 95% CI
2. **Asymmetric errors**: Support for different upper/lower bounds
3. **Custom opacity**: Let users control shaded region transparency
4. **Error bars instead of regions**: Option for traditional error bars
5. **Bootstrapped confidence intervals**: Statistical alternative to SEM

---

## Summary

v0.5 adds professional error visualization to Plot Organizer, enabling users to show measurement uncertainty and variability in their line plots. The implementation is robust, well-tested, and integrates seamlessly with existing features like hue grouping, faceting, and export.

**Key metric**: 29/29 tests passing ✅

