# Error Marker Annotations Feature

## Summary

Added support for error bar marker annotations to plots. This feature allows users to mark significant events, thresholds, or time periods on plots with customizable error bars (horizontal and/or vertical).

## Features

### Data Structure
Each error marker is a dictionary with the following fields:
- `x`, `y`: Position values (at least one can be `None` for auto-computation)
- `xerr`, `yerr`: Error bar widths (at least one required)
- `color`: Marker color (required, customizable)
- `label`: Optional label for legend
- Fixed appearance: Triangle marker (v), size=10, capsize=5

### Auto-Positioning and Stacking
- When `x` or `y` is `None`, the position is auto-computed based on plot data range
- Multiple markers are automatically stacked with 0.08 * range offset
- X error bars (horizontal) stack vertically from the top
- Y error bars (vertical) stack horizontally from the right

### Usage

#### 1. Programmatic API

```python
from plot_organizer.api import create_plot

plot = create_plot(
    datasource_id,
    x="time",
    y="accuracy",
    error_markers=[
        {
            "x": 5.0,           # Position on x-axis
            "xerr": 0.5,        # ±0.5 error bar width
            "color": "red",
            "label": "Checkpoint Saved"
        },
        {
            "y": 0.8,           # Position on y-axis (x auto-computed)
            "yerr": 0.1,        # ±0.1 error bar width
            "color": "blue",
            "label": "Target Threshold"
        }
    ]
)
```

#### 2. UI Interface

Users can manage error markers through the GUI:
1. Right-click on any plot
2. Select "Manage Error Markers..."
3. Add, edit, or delete markers interactively
4. Changes are reflected immediately in the plot

### Example Use Cases

1. **Time-based events** (horizontal error bars):
   - Mark when checkpoints were saved
   - Indicate when hyperparameters changed
   - Show onset of statistical significance with time uncertainty

2. **Value thresholds** (vertical error bars):
   - Mark target performance levels
   - Show acceptable tolerance ranges
   - Indicate critical values or boundaries

3. **Mixed annotations**:
   - Combine multiple markers with different orientations
   - Auto-stack for clear visibility
   - Customize colors to distinguish marker types

## Implementation Details

### Files Modified

1. **plot_organizer/ui/grid_board.py**
   - Added `_error_markers` attribute to `PlotTile`
   - Implemented `_render_error_markers()` method with auto-positioning logic
   - Added `_open_markers_dialog()` for UI integration
   - Updated `set_plot()`, `clear_plot()`, `get_plot_data()`, `set_plot_from_data()`
   - Added context menu option "Manage Error Markers..."

2. **plot_organizer/api.py**
   - Added `error_markers` parameter to `create_plot()`
   - Added `error_markers` parameter to `create_grouped_plots()`
   - Updated docstrings with examples

3. **plot_organizer/ui/dialogs.py**
   - Created `ErrorMarkerDialog` for adding/editing single markers
   - Created `ErrorMarkersManagerDialog` for managing all markers
   - Includes color picker, validation, and user-friendly interface

4. **plot_organizer/tests/test_error_markers.py**
   - 7 comprehensive tests covering API, save/load, rendering, stacking, etc.
   - All tests pass ✓

### Files Created

1. **examples/example_error_markers.py**
   - Complete example demonstrating all marker types
   - Creates a project with 3 plots showing different use cases

## Testing

All 118 tests pass, including:
- ✓ API creation and serialization
- ✓ Save/load round-trip persistence
- ✓ Mixed marker configurations
- ✓ UI rendering integration
- ✓ Auto-positioning and stacking
- ✓ Compatibility with grouped plots

## Running the Example

```bash
# Create the example project
python examples/example_error_markers.py

# Open in GUI to see markers
python -m plot_organizer error_markers_example.ppo
```

## Backward Compatibility

- Fully backward compatible - existing projects without error markers work unchanged
- Default value is empty list `[]`
- Optional parameter in all APIs

## Technical Notes

### Rendering Order
Error markers are rendered with `zorder=10` to ensure they appear on top of plot data.

### Auto-Positioning Algorithm
- X error bars: `y = y_max - (0.05 + index * 0.08) * y_range`
- Y error bars: `x = x_max - (0.05 + index * 0.08) * x_range`

This ensures markers stack visibly without overlapping the main plot data.

### JSON Serialization
Error markers are stored as-is in the `.ppo` project files, with `None` values preserved for auto-positioned coordinates.

## Future Enhancements (Optional)

- Support for custom marker shapes beyond triangle
- Adjustable marker size and capsize
- Batch import of markers from CSV
- Marker templates/presets

