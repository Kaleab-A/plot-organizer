# Multi-Column Hue Feature Summary

## Overview
Added support for selecting multiple columns as hue, where each unique combination of values across selected columns becomes a separate line/hue in plots. This enables more sophisticated data visualization by combining multiple categorical variables.

## Implementation Date
November 27, 2025

## Changes Made

### 1. UI Dialog (`plot_organizer/ui/dialogs.py`)
- **Removed**: Single hue combo box
- **Added**: Multi-select list widget for hue columns (similar to groups)
- **Added**: Label showing selected hue column count with helpful message
- **Updated**: Column refresh logic to populate hue list
- **Updated**: Validation to prevent column conflicts between x, y, hue, groups, and SEM

**Key Features**:
- Users can select 0, 1, or multiple columns for hue
- Empty selection = no hue (same as before)
- Visual feedback showing number of selected columns
- Conflict detection prevents using same column for multiple purposes

### 2. Main Window (`plot_organizer/ui/main_window.py`)
- **Updated**: `_action_quick_plot()` to handle hue as list of columns
- Passes hue list directly to plot tiles and shared limits calculations
- Maintains backward compatibility with single string hue

### 3. Plot Tile (`plot_organizer/ui/grid_board.py`)
- **Updated**: `set_plot()` signature to accept `hue: str | list[str] | None`
- **Updated**: `_hue` attribute type to `str | list[str] | None`
- **Added**: Composite hue column creation logic:
  - When hue is a list, creates temporary `__composite_hue__` column
  - Format: `Column1=value1, Column2=value2`
  - Uses pandas `apply()` with lambda to generate labels
- **Updated**: Plot grouping to use composite hue column
- **Protection**: Works on copy of dataframe to avoid modifying original data

**Key Implementation Detail**:
```python
# Create composite column with format: Col1=val1, Col2=val2
composite_name = "__composite_hue__"
plot_df[composite_name] = plot_df.apply(
    lambda row: ", ".join(f"{col}={row[col]}" for col in hue),
    axis=1
)
```

### 4. Plot Service (`plot_organizer/services/plot_service.py`)
- **Updated**: `shared_limits_with_sem()` signature to accept `hue: str | list[str] | None`
- **Added**: Same composite hue column logic for limit calculations
- Ensures y-axis limits account for all hue combinations when computing SEM-based limits

## Features

### Legend Format
When multiple hue columns are selected, legend labels use explicit key-value format:
- Single column: `A`, `B`, `C`
- Two columns: `species=setosa, gender=male`, `species=setosa, gender=female`, etc.
- Three+ columns: `col1=A, col2=X, col3=P`, etc.

### Backward Compatibility
- Single string hue still works exactly as before
- `None` or empty list `[]` = no hue
- All existing tests pass without modification (77 tests)

### Works With
- ✅ SEM columns (both computed and pre-computed)
- ✅ Group faceting
- ✅ Reference lines (horizontal and vertical)
- ✅ Plot styles (lines, markers, both)
- ✅ Custom y-axis limits
- ✅ Filter queries
- ✅ Shared limits across multiple plots

### Validation
- Prevents using same column as both hue and x/y/group/SEM
- Clear error messages when conflicts detected
- Works correctly with all existing features

## Testing

Created comprehensive test suite in `test_multi_column_hue.py` with 9 tests:
1. ✅ Basic multi-column hue with 2 columns
2. ✅ Single column backward compatibility
3. ✅ No hue (None)
4. ✅ Empty hue list
5. ✅ Multi-column hue with SEM
6. ✅ Shared limits with multi-column hue
7. ✅ Three-column hue
8. ✅ Original dataframe preservation
9. ✅ Multi-column hue with filter queries

**Test Results**: All 86 tests pass (77 existing + 9 new)

## Usage Example

### UI Workflow
1. Open "Plot → Quick Plot..." dialog
2. Select x and y columns as usual
3. In "Hue columns (multi-select, optional)" section:
   - Click multiple columns while holding Ctrl/Cmd
   - Selected count shows: "Selected 2 hue column(s). Will combine values for legend."
4. Configure other options (groups, SEM, etc.)
5. Click OK to create plot

### Result
- One line per unique combination of hue column values
- Legend shows: `species=A, gender=male`, `species=A, gender=female`, etc.
- Works seamlessly with all existing features

## Technical Notes

### Performance
- Composite column creation uses pandas `apply()` with lambda
- Only creates composite column when needed (list with ≥1 column)
- Works on copy of filtered data, doesn't modify original dataframe

### Memory
- Temporary `__composite_hue__` column only exists during plotting
- Not stored persistently in tile or dataframe
- Minimal memory overhead

### Limitations
- None identified - works with all existing features
- No arbitrary limit on number of hue columns (though too many would make legend unreadable)

## Files Modified
1. `plot_organizer/ui/dialogs.py` - Dialog UI and validation
2. `plot_organizer/ui/main_window.py` - Quick plot action handling
3. `plot_organizer/ui/grid_board.py` - Plot tile rendering with composite hue
4. `plot_organizer/services/plot_service.py` - Shared limits calculation

## Files Added
1. `plot_organizer/tests/test_multi_column_hue.py` - Comprehensive test suite

## Future Enhancements (Optional)
- Could add separator customization (comma-space vs pipe vs underscore)
- Could add option to abbreviate long legend labels
- Could add smart legend positioning when many hue combinations exist

## Summary
The multi-column hue feature is fully implemented, tested, and integrated with all existing functionality. It maintains backward compatibility while providing powerful new visualization capabilities.

