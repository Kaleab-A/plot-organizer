# Reference Lines Feature - Quick Summary

## What It Does

Adds **horizontal and vertical reference lines** to your plots. These are black dashed lines that mark important values like thresholds, baselines, or time points.

## How to Use

1. Open **Plot → Quick Plot...**
2. Fill in your x, y, hue, etc. as usual
3. In the **Reference Lines (optional)** section:
   - **Horizontal**: Enter y-values separated by commas
     - Example: `0, 50, 100`
   - **Vertical**: Enter x-values separated by commas
     - Example: `2020, 2021, 2022, 2023`
4. Click **OK**

Your plots will show black dashed lines at those positions!

## Examples

### Example 1: Threshold Lines
```
You want to mark performance thresholds at 50, 75, and 100:
Horizontal: 50, 75, 100

Result: Three horizontal dashed lines across your plot
```

### Example 2: Time Markers
```
You want to mark important years in your time series:
Vertical: 2020, 2021, 2022

Result: Three vertical dashed lines marking those years
```

### Example 3: Baseline
```
You want to show the zero baseline:
Horizontal: 0

Result: One horizontal line at y=0
```

### Example 4: Grid Reference
```
Create a reference grid:
Horizontal: 0, 25, 50, 75, 100
Vertical: 0, 10, 20, 30, 40

Result: Grid of intersecting reference lines
```

## Visual Style

- **Color**: Black
- **Style**: Dashed (`--`)
- **Width**: 1 pixel
- **Transparency**: 70% opaque (30% transparent)
- **Position**: Behind data (won't obscure your plots)

## Features

✅ **Multiple lines**: Add as many as you want  
✅ **Both types**: Use horizontal, vertical, or both  
✅ **Decimal values**: Supports floats (e.g., `10.5, 20.7`)  
✅ **Shared across groups**: When faceting, lines appear on all plots  
✅ **Exported**: Lines preserved in PDF/SVG/EPS/PNG exports  
✅ **Optional**: Leave blank if you don't need them  
✅ **Error tolerant**: Invalid values are skipped silently  

## Input Format

**Valid inputs**:
- `10, 20, 30` → Three lines
- `0` → One line
- `10.5, 20.7, 30.9` → Decimal values OK
- `  1 ,  2  , 3  ` → Extra spaces ignored
- (empty) → No lines

**Invalid values skipped**:
- `10, abc, 30` → Creates lines at 10 and 30 (skips "abc")
- `invalid text` → No lines (but plot still works!)

## Use Cases

1. **Performance monitoring**: Mark SLA thresholds
2. **Scientific data**: Show baseline or control values
3. **Time series**: Mark important events or dates
4. **Comparisons**: Show target values or benchmarks
5. **Statistical bounds**: Mark confidence intervals

## Works With

- ✅ Hue grouping
- ✅ SEM column (shaded regions)
- ✅ Group faceting (lines on all plots)
- ✅ Shared axes
- ✅ All export formats

## Notes

- Reference lines are **shared** across all plots when using groups (faceting)
- All plots in a faceted set get the same reference lines
- Lines are drawn **after** data, so they won't be hidden
- Lines use `zorder=1` to stay behind data points but visible

---

**Version**: v0.6  
**Tests**: 43/43 passing ✅  
**Status**: Production ready

