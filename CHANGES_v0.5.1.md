# Changes v0.5.1 – SEM-Aware Shared Limits Fix

_Date: 2025-10-10_

## Overview

Fixed a critical issue where grouped plots with SEM columns had incorrectly scaled y-axis limits. The y-limits were computed from raw data values instead of the aggregated means ± SEM that were actually plotted, resulting in overly large axis ranges.

---

## Problem

### Before Fix

When creating **grouped plots** (faceted plots) **with a SEM column**:

1. The `shared_limits()` function calculated y-limits from **raw y-values** in the data
2. But the plots displayed **aggregated means ± SEM** (after grouping by SEM column)
3. Result: **Y-axis was much too large**, showing mostly empty space

**Example:**
- Raw data: y-values range from 5 to 95 (outliers)
- After SEM aggregation: means range from ~15 to ~40, SEM regions from ~12 to ~43
- Old behavior: y-axis set to (5, 95) ← Too large! 
- Desired: y-axis set to (~12, ~43) ← Fits the actual plotted data

### Root Cause

The `shared_limits()` function had no awareness of:
- SEM column aggregation (grouping by SEM column, then computing means)
- The fact that plots show mean ± SEM, not raw values

---

## Solution

### New Function: `shared_limits_with_sem()`

**File**: `plot_organizer/services/plot_service.py`

Added a new function that:
1. **Replicates the SEM aggregation logic** used in plotting
2. **Computes limits based on mean ± SEM values** instead of raw data
3. **Handles hue grouping** correctly (each hue category gets its own aggregation)
4. **Falls back to aggregated means** when no SEM column is specified

**Algorithm:**
```python
For each group combination:
    Filter data → Apply group filter
    
    If SEM column exists:
        For each hue category (if hue present):
            1. Group by (sem_column, x) and compute mean(y)
            2. For each x, compute mean and SEM across sem_column groups
            3. Track (mean - SEM) as lower bound
            4. Track (mean + SEM) as upper bound
    Else:
        Use aggregated means (group by x, compute mean(y))
    
Return (min of all lower bounds, max of all upper bounds)
```

### Updated Main Window

**File**: `plot_organizer/ui/main_window.py`

Modified the limit calculation logic to:
- Use `shared_limits_with_sem()` when a SEM column is present
- Fall back to original `shared_limits()` when no SEM column

```python
if len(filter_queries) > 1:
    if sem_column:
        # Use SEM-aware limits calculation
        xlim, ylim = shared_limits_with_sem(df, filter_queries, x, y, sem_column, hue)
    else:
        # Use original limits calculation
        xlim, ylim = shared_limits(subsets, x, y)
```

---

## Technical Details

### New Functions

1. **`shared_limits_with_sem()`**
   - Parameters: `df`, `filter_queries`, `x`, `y`, `sem_column`, `hue` (optional)
   - Returns: `(xlim, ylim)` tuples based on aggregated data
   - Handles both hue and non-hue cases
   - Gracefully handles empty subsets

2. **`_compute_sem_stats()` (helper)**
   - Replicates the SEM aggregation from `PlotTile._plot_with_sem()`
   - Returns `(lower_bounds, upper_bounds)` lists
   - Fills NaN SEM values with 0 to avoid computation errors

### Modified Files

- `plot_organizer/services/plot_service.py` - Added 2 new functions (~70 lines)
- `plot_organizer/ui/main_window.py` - Updated limit calculation (~10 lines changed)

---

## Testing

### New Test File: `test_sem_limits.py`

Added 5 comprehensive tests:

1. **`test_sem_limits_vs_raw_limits`**
   - Verifies SEM-aware limits are tighter than raw data limits
   - Uses data with outliers that get smoothed by aggregation

2. **`test_sem_limits_with_hue`**
   - Tests that hue grouping is handled correctly
   - Ensures limits encompass all hue categories

3. **`test_sem_limits_no_sem_column`**
   - Verifies backward compatibility when `sem_column=None`
   - Should use aggregated means instead

4. **`test_sem_limits_empty_subset`**
   - Tests graceful handling of empty subsets
   - Should skip empty groups and use only valid data

5. **`test_sem_limits_single_group`**
   - Tests single-group case (no faceting, but still using function)
   - Verifies limits are computed correctly

**Test Coverage**: All 34 tests pass (29 existing + 5 new)

---

## User-Facing Changes

### Behavior Change

**Before:**
- Grouped plots with SEM: Y-axis often too large, showing mostly empty space
- Difficult to see actual data trends due to poor scaling

**After:**
- Grouped plots with SEM: Y-axis perfectly scaled to fit mean ± SEM regions
- Much better use of plot space
- Easier to compare trends across faceted plots

### Visual Impact

```
BEFORE (using raw data limits):
100 |                                    ← Wasted space
    |
 50 |  ──────────────  ← Tiny plot data
    |
  0 |________________________________

AFTER (using SEM-aware limits):
 45 |
    |  ░░░░░░░░░░░░
 40 |  ████████████  ← Plot fills space nicely
    |  ░░░░░░░░░░░░
 35 |________________________________
```

### No Breaking Changes

✅ **Fully backward compatible**
- Grouped plots **without** SEM column: Use original `shared_limits()` (unchanged behavior)
- Single plots (no grouping): Always use Matplotlib autoscaling (unchanged)
- Only grouped plots **with** SEM column use the new function

---

## Edge Cases Handled

1. **Empty subsets**: Skipped gracefully, limits computed from valid data only
2. **NaN SEM values**: Filled with 0 to prevent errors in limit calculation
3. **Mixed hue/no-hue**: Function handles both cases correctly
4. **Single group**: Works even when there's only one group (no actual sharing needed)
5. **No SEM column**: Falls back to aggregated means, not raw data

---

## Performance

- **Minimal overhead**: Only runs when creating grouped plots with SEM
- **Efficient**: Uses pandas groupby operations (same as plotting)
- **No duplicate work**: Computation is separate from plotting, but uses same logic

---

## Future Considerations

Potential enhancements:
1. **Padding**: Add optional padding percentage to limits (e.g., 5% margin)
2. **Manual override**: Allow users to manually set axis limits in plot settings
3. **Auto-detect aggregation**: Automatically use aggregated limits even without SEM when data is highly variable

---

## Summary

This fix ensures that grouped plots with SEM columns have appropriately scaled y-axes that match the aggregated data being displayed. The y-axis now fits the mean ± SEM regions tightly, providing much better use of plot space and easier visual comparison across faceted plots.

**Key Improvement**: Y-axis limits now match what's actually plotted, not the raw data values.

**Tests**: 34/34 passing ✅ (added 5 new tests)

