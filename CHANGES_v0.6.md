# Changes v0.6 – Reference Lines Feature

_Date: 2025-10-10_

## Overview

Added the ability to add multiple horizontal and vertical reference lines to plots. Reference lines are displayed as black dashed lines and are useful for marking thresholds, baselines, target values, or other important reference points.

---

## What's New

### 1. Reference Lines in Quick Plot Dialog

**File**: `plot_organizer/ui/dialogs.py`

Added a new "Reference Lines (optional)" section to the Quick Plot Dialog with:
- **Horizontal lines input**: Text field for entering y-values (comma-separated)
- **Vertical lines input**: Text field for entering x-values (comma-separated)
- Placeholder text showing example format: "e.g., 0, 50, 100"

**User Experience**:
```
Quick Plot Dialog:
  ...existing fields...
  
  Reference Lines (optional):
    Horizontal (y-values, comma-separated): [___________]
    Vertical (x-values, comma-separated):   [___________]
```

### 2. Number Parsing

**New Method**: `QuickPlotDialog._parse_numbers(text: str) -> list[float]`

Robust parsing of comma-separated numbers:
- Handles extra whitespace gracefully
- Skips invalid values silently (doesn't block plot creation)
- Returns empty list if no valid numbers found
- Supports both integers and floats

**Examples**:
```python
"1, 2, 3"           → [1.0, 2.0, 3.0]
"10.5, 20.7, 30.9"  → [10.5, 20.7, 30.9]
"  1 ,  2  , 3  "   → [1.0, 2.0, 3.0]  # Extra whitespace OK
"1, abc, 3"         → [1.0, 3.0]        # Skips invalid values
""                  → []                 # Empty = no lines
```

### 3. PlotTile Support

**File**: `plot_organizer/ui/grid_board.py`

- Added `_hlines` and `_vlines` instance variables to store reference line positions
- Updated `set_plot()` signature to accept `hlines` and `vlines` parameters
- Reference lines drawn using `ax.axhline()` and `ax.axvline()`
- Updated `clear_plot()` to reset reference lines

**Line Style**:
- Color: Black
- Style: Dashed (`--`)
- Width: 1 pixel
- Alpha: 0.7 (slightly transparent)
- Z-order: 1 (behind data, but visible)

### 4. Integration with Plotting

**File**: `plot_organizer/ui/main_window.py`

- Extracts `hlines` and `vlines` from dialog selection
- Passes reference lines to all plots in a group (shared across faceted plots)
- Reference lines appear on every plot when using group faceting

### 5. Export Support

**File**: `plot_organizer/services/export_service.py`

- Updated `_render_plot_to_ax()` to include reference lines in exports
- Reference lines preserved in PDF, SVG, EPS, and PNG exports
- Same visual style as on-screen display

---

## Technical Details

### Modified Files

1. **`plot_organizer/ui/dialogs.py`**
   - Added `QLineEdit` imports
   - Added reference lines UI section
   - Added `_parse_numbers()` helper method
   - Updated `selection()` to return `hlines` and `vlines`

2. **`plot_organizer/ui/grid_board.py`**
   - Added `_hlines` and `_vlines` instance variables
   - Updated `set_plot()` signature and implementation
   - Added reference line drawing code
   - Updated `clear_plot()` to reset lines

3. **`plot_organizer/ui/main_window.py`**
   - Extract reference lines from selection
   - Pass lines to `tile.set_plot()`

4. **`plot_organizer/services/export_service.py`**
   - Added reference line rendering to exports

### Data Flow

```
User enters "10, 20, 30" in horizontal lines field
    ↓
QuickPlotDialog._parse_numbers() converts to [10.0, 20.0, 30.0]
    ↓
selection() returns {"hlines": [10.0, 20.0, 30.0], ...}
    ↓
MainWindow extracts hlines and passes to all grouped plots
    ↓
PlotTile.set_plot() stores lines and draws them with ax.axhline()
    ↓
ExportService._render_plot_to_ax() replicates lines in exports
```

---

## Use Cases

### 1. Threshold Lines

Mark performance thresholds or target values:
```
Horizontal: 50, 100, 150  (target milestones)
```

### 2. Baseline Markers

Show baseline or zero reference:
```
Horizontal: 0  (baseline)
```

### 3. Time Period Markers

Mark important time points or intervals:
```
Vertical: 2020, 2021, 2022, 2023  (yearly markers)
```

### 4. Grid-like References

Create a reference grid:
```
Horizontal: 0, 25, 50, 75, 100
Vertical: 0, 10, 20, 30, 40
```

### 5. Statistical Markers

Mark statistical boundaries:
```
Horizontal: 2.5, 97.5  (95% confidence boundaries)
```

---

## Visual Examples

### Before (Without Reference Lines)
```
Plot showing data trend, no context for specific values
```

### After (With Reference Lines)
```
   100 ┬────────────────────  ← Target threshold (h-line)
       │     ╱╱╱╱
    50 ┼───────────────────  ← Baseline (h-line)
       │   ╱
     0 └─────│─────────────
           2020            ← Event marker (v-line)
```

---

## Testing

### New Test File: `test_reference_lines.py`

**9 comprehensive tests**:

1. **`test_horizontal_reference_lines`**
   - Verifies horizontal lines are stored and drawn

2. **`test_vertical_reference_lines`**
   - Verifies vertical lines are stored and drawn

3. **`test_both_reference_lines`**
   - Tests using both types simultaneously

4. **`test_no_reference_lines`**
   - Ensures backward compatibility (no lines = works normally)

5. **`test_clear_plot_resets_reference_lines`**
   - Confirms clearing a plot also clears reference lines

6. **`test_reference_lines_with_hue`**
   - Tests interaction with hue grouping

7. **`test_reference_lines_with_sem`**
   - Tests interaction with SEM column feature

8. **`test_parse_numbers_helper`**
   - Validates the number parsing logic

9. **`test_multiple_reference_lines`**
   - Tests many lines at once

**Test Coverage**: All 43 tests pass (34 existing + 9 new)

---

## User-Facing Changes

### Dialog Changes

- **Quick Plot Dialog** now has a "Reference Lines (optional)" section
- Two text input fields for horizontal and vertical line values
- Helpful placeholder text shows the expected format

### Visual Changes

- Plots can now show black dashed reference lines
- Lines appear at user-specified x or y values
- Lines are slightly transparent (70% opacity) to avoid obscuring data

### Shared Across Groups

When using faceting (groups), reference lines appear on **all generated plots**:
- Useful for comparing multiple plots against the same thresholds
- All plots get the same reference lines
- Lines maintain consistent style across all tiles

---

## Edge Cases Handled

1. **Empty input**: No lines drawn (plots work normally)
2. **Invalid values**: Skipped silently, valid values still used
3. **Extra whitespace**: Trimmed automatically
4. **Mixed valid/invalid**: Only valid numbers used
5. **Decimal values**: Supported (e.g., "10.5, 20.7")
6. **Single value**: Works fine (e.g., "100" creates one line)
7. **Many lines**: No limit on number of reference lines

---

## Backward Compatibility

✅ **Fully backward compatible**

- Reference lines are optional (default: none)
- Plots without reference lines work exactly as before
- All existing tests still pass
- No changes to existing plot behavior

---

## Performance

- **Minimal overhead**: Drawing lines with `axhline`/`axvline` is very fast
- **No impact on data processing**: Lines drawn after data processing
- **Export performance**: Negligible impact on export time

---

## Future Enhancements

Potential improvements for future versions:

1. **Custom line styles**: Allow users to choose color, style (solid, dashed, dotted)
2. **Line labels**: Add optional text labels to reference lines
3. **Line-specific styles**: Different style for each line
4. **Save/Load**: Persist reference lines in project files
5. **UI improvements**: Visual line builder or list view
6. **Smart suggestions**: Auto-suggest common thresholds based on data

---

## Examples

### Example 1: Performance Monitoring
```
Data: Server response time over days
Horizontal lines: 100, 500, 1000 (ms thresholds)
Result: Easy to see when performance exceeded targets
```

### Example 2: Time Series with Events
```
Data: Stock prices over time
Vertical lines: 2020-03-01, 2021-01-01 (major events)
Result: Visualize how events affected prices
```

### Example 3: Scientific Experiment
```
Data: Measurement values across conditions
Horizontal lines: 0 (baseline), -2, +2 (2 std devs)
Result: See which conditions are statistically significant
```

---

## Summary

v0.6 adds flexible reference line support to the Plot Organizer, enabling users to add visual markers for thresholds, baselines, time points, and other important reference values. The implementation is simple, robust, and integrates seamlessly with all existing features including hue grouping, SEM plotting, faceting, and export.

**Key Features**:
- Multiple horizontal and vertical reference lines
- Black dashed style with 70% opacity
- Simple comma-separated input format
- Robust parsing with error tolerance
- Export support (PDF/SVG/EPS/PNG)

**Key metric**: 43/43 tests passing ✅

