# Changes in v0.2.1

## Summary

Added automatic aggregation of duplicate (x, hue) values to produce cleaner plots with single lines instead of multiple overlapping points.

## Problem Solved

Previously, if your data had multiple y-values for the same x-value (and hue category), all points would be plotted, resulting in:
- Multiple overlapping markers/lines
- Cluttered, hard-to-read plots
- No clear trend line

## Solution

When plotting, the data is now automatically aggregated:
- **Without hue**: Groups by `x`, computes mean of `y`
- **With hue**: Groups by `(x, hue)`, computes mean of `y` for each combination

This produces clean, single-line plots showing the average trend.

## Technical Details

### File Modified: `plot_organizer/ui/grid_board.py`

In the `set_plot()` method:

```python
# Before (old code):
if hue:
    for key, sub in plot_df.groupby(hue):
        ax.plot(sub[x], sub[y], label=str(key))
else:
    ax.plot(plot_df[x], plot_df[y])

# After (new code):
if hue:
    for key, sub in plot_df.groupby(hue):
        # Aggregate: compute mean of y for each unique x value
        agg_sub = sub.groupby(x, as_index=False)[y].mean()
        ax.plot(agg_sub[x], agg_sub[y], label=str(key))
else:
    # No hue: aggregate duplicate x values
    agg_df = plot_df.groupby(x, as_index=False)[y].mean()
    ax.plot(agg_df[x], agg_df[y])
```

### Tests Added: `plot_organizer/tests/test_aggregation.py`

Three comprehensive tests:
1. **test_aggregation_logic**: Verifies mean calculation for duplicate (x, hue) pairs
2. **test_no_duplicates**: Ensures data without duplicates remains unchanged
3. **test_all_duplicates**: Tests when all x values are identical

All tests pass ✅

## Example

**Before aggregation:**
```
x=1, y=10, hue=A
x=1, y=20, hue=A
x=1, y=30, hue=A
→ 3 overlapping points at x=1
```

**After aggregation:**
```
x=1, y=20, hue=A  (mean of 10, 20, 30)
→ Single clean point at x=1
```

## Use Cases

This is particularly useful for:
- Time series data with multiple measurements per timestamp
- Survey data with multiple responses for the same category
- Sensor data with high-frequency sampling
- Any dataset where you want to see the average trend rather than individual points

## Behavior

- **Aggregation function**: Mean (average)
- **Applied automatically**: No user configuration needed
- **Preserves structure**: Works with both hue and non-hue plots
- **Compatible with groups**: Aggregation happens after filtering by group values

## What's Next

Future enhancements could include:
- User-selectable aggregation functions (median, min, max, sum)
- Option to show confidence intervals or error bars
- Toggle between aggregated and raw data views

