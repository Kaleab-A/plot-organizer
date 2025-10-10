# SEM Limits Fix - Quick Summary

## The Problem You Reported

When creating **grouped plots with a SEM column**, the y-axis limits were **too large** and didn't match the actual data being displayed.

## Why It Happened

The old code calculated y-axis limits using **raw data values**:
```
Raw data: [5, 10, 15, 85, 90, 95]
Y-axis: (5, 95)  ← Too large!
```

But with SEM aggregation, the plot actually shows:
```
After grouping by SEM column:
  - Subject 1: mean = 10
  - Subject 2: mean = 12.5
  - Subject 3: mean = 90

Overall mean ± SEM across subjects:
  - Mean: ~37.5
  - SEM: ~25
  - Plot range: ~12 to ~63

Y-axis should be: (~12, ~63)  ← Much smaller!
```

## The Fix

### New Function: `shared_limits_with_sem()`

This function:
1. **Replicates the SEM aggregation** that happens during plotting
2. **Computes limits from mean ± SEM values** instead of raw data
3. **Works with hue grouping** (each hue category gets proper treatment)
4. **Falls back gracefully** when no SEM column is used

### Smart Detection

The code now automatically chooses the right method:
- **Grouped plots WITH SEM**: Use `shared_limits_with_sem()` ✅
- **Grouped plots WITHOUT SEM**: Use original `shared_limits()` (aggregated means)
- **Single plots**: Use Matplotlib autoscaling (no change)

## Result

**Before Fix:**
```
Y-axis: 0 to 100
Plot data: tiny line around 40-50
Result: 80% wasted space ❌
```

**After Fix:**
```
Y-axis: 35 to 65
Plot data: fills the space nicely
Result: Perfect scaling ✅
```

## Testing

Added 5 new tests specifically for this fix:
- Verifies SEM-aware limits are tighter than raw limits
- Tests with hue grouping
- Tests backward compatibility
- Tests edge cases (empty subsets, single groups)

**All 34 tests passing** ✅

## Files Changed

1. `plot_organizer/services/plot_service.py`
   - Added `shared_limits_with_sem()` function
   - Added `_compute_sem_stats()` helper

2. `plot_organizer/ui/main_window.py`
   - Updated to use new function when SEM column present

3. `plot_organizer/tests/test_sem_limits.py`
   - New test file with 5 comprehensive tests

## No Breaking Changes

- Existing plots without SEM: Work exactly as before
- Single plots: No change in behavior
- Only grouped plots with SEM: Now have correct y-axis scaling

## Summary

The y-axis limits for grouped plots with SEM now match the actual data being plotted (aggregated means ± SEM) instead of the raw data values. This gives you much better use of plot space and makes trends easier to see!

---

**Version**: v0.5.1  
**Tests**: 34/34 passing ✅  
**Issue**: Resolved

