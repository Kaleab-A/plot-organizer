# Changes in v0.3 - Plot Settings & Grid Management

## Summary

Major new features for controlling plot positioning, spanning, and grid management. Users can now configure each plot's location and size, and remove unused rows/columns.

## New Features

### 1. Plot Settings Dialog ✨
**Access:** Right-click on any plot tile → "Plot Settings..."

Configure individual plots with:
- **Starting Position:** Choose which row and column the plot starts at
- **Spanning:** Make plots span multiple rows and/or columns (up to 10x10)
- Automatic grid expansion: If the target area doesn't fit, new rows/cols are added automatically
- Other plots are shifted automatically when needed

**Example Use Cases:**
- Make an important plot larger by spanning 2x2 cells
- Move a plot to a specific position in the grid
- Create asymmetric layouts (e.g., one large plot + several small ones)

### 2. Context Menu on Plot Tiles 🖱️
Right-click on any plot tile to access:
- **Plot Settings...** - Opens the settings dialog
- **Clear Plot** - Removes the plot data (with confirmation)

### 3. Remove Rows/Columns ✂️
**Access:** Grid menu → "- Row..." or "- Col..."

- Remove empty rows or columns from the grid
- Safety check: Won't remove if the row/column contains non-empty plots
- Remaining plots are automatically shifted to fill the gap
- Interactive dialogs prompt for which row/column to remove

### 4. Clear Plot Feature 🗑️
- Right-click on a plot → "Clear Plot"
- Confirmation dialog prevents accidental deletion
- Plot tile returns to empty state
- Grid cell remains (can be reused for another plot)

## Technical Details

### Files Modified/Created

**plot_organizer/ui/dialogs.py**
- Added `PlotSettingsDialog` class with position and span controls
- Uses `QSpinBox` for numeric input
- Grouped UI with "Position" and "Span" sections

**plot_organizer/ui/grid_board.py**
- Added `PlotTile` signals: `settings_requested`, `clear_requested`
- Implemented `contextMenuEvent` for right-click menu
- Added `clear_plot()` method to reset tile state
- Added `remove_row(row)` and `remove_col(col)` methods
  - Check for non-empty plots before removing
  - Shift remaining widgets after removal
- Added `move_plot(from_row, from_col, to_row, to_col, rowspan, colspan)`
  - Supports multi-cell spanning
  - Auto-expands grid if target doesn't fit
  - Clears target empty cells before placement
- Added `find_tile_position(tile)` to get current position and span

**plot_organizer/ui/main_window.py**
- Added Grid menu items: "- Row..." and "- Col..."
- Connected tile signals to handlers:
  - `_on_tile_settings(tile)` - Opens settings dialog and applies changes
  - `_on_tile_clear(tile)` - Confirms and clears plot
- Added actions:
  - `_action_remove_row()` - Prompts for row number and removes
  - `_action_remove_col()` - Prompts for column number and removes
- Added `_connect_tile_signals()` to wire up all tile events

### Tests
Created `test_grid_operations.py` with 11 comprehensive tests:
- ✅ Add row/column
- ✅ Remove empty row/column
- ✅ Prevent removal of row/column with plots
- ✅ Check if tile is empty
- ✅ Find tile position
- ✅ Move plot to new location
- ✅ Move plot with spanning
- ✅ First empty coordinate finder

**All 22 tests pass** (11 new + 11 existing)

## Usage Examples

### Example 1: Make a Plot Span 2x2 Cells
1. Create a plot (it starts at 1x1)
2. Right-click on the plot → "Plot Settings..."
3. Set "Rows to span: 2" and "Columns to span: 2"
4. Click OK
5. The plot now occupies 4 cells (2x2)

### Example 2: Move Plot to Different Location
1. Right-click on a plot → "Plot Settings..."
2. Change "Start Row" and "Start Column"
3. Click OK
4. Plot moves to new position; other plots may shift

### Example 3: Remove Empty Rows
1. Grid → "- Row..."
2. Enter row number (e.g., 2)
3. If row is empty → Success message, row removed
4. If row has plots → Warning message, row kept

### Example 4: Clear and Reuse a Cell
1. Right-click on a plot → "Clear Plot"
2. Confirm deletion
3. Cell is now empty and ready for a new plot

## Behavior Notes

- **Auto-expansion:** If you move/span a plot beyond the current grid size, new rows/cols are added automatically
- **Safety checks:** Cannot remove rows/columns that contain non-empty plots
- **Confirmation dialogs:** Clearing a plot requires confirmation to prevent accidents
- **Shift behavior:** When removing a row/col, all subsequent rows/cols shift to fill the gap
- **Signal connections:** Tile signals are reconnected after moves to ensure context menus work

## Breaking Changes

None - all existing functionality preserved.

## Known Limitations

- No drag-and-drop (use Plot Settings dialog instead)
- Cannot resize existing grid (add/remove only)
- Span limited to 10x10 (should be sufficient for most cases)
- No undo for grid operations

## What's Next

With plot settings and grid management complete, the next priorities are:
1. Whole-grid export to PDF/SVG/PNG
2. Project save/load
3. Advanced CSV loading wizard

