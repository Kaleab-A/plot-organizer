# Changes in v0.3.1 - Improved Plot Settings UX

## Summary

Enhanced Plot Settings dialog to enforce one operation at a time (position OR span), and implemented proper plot swapping with span validation.

## Problem Solved

**Previous behavior (v0.3):**
- When changing position, the plot would move but leave the original cell blank
- Could change both position and span simultaneously, causing confusion
- No validation that plots have matching spans when swapping

**New behavior (v0.3.1):**
- Position changes now **swap** plots instead of moving them
- Can only change position OR span, not both at once
- Controls automatically lock when one is changed
- Validates that both plots have matching spans before swapping
- Clear error messages guide users to make plots 1×1 before swapping if needed

## New Features

### 1. Mutually Exclusive Position/Span Changes 🔒
- When you change position, span controls are **disabled**
- When you change span, position controls are **disabled**
- Visual indicator at top: "Change position OR span, not both at the same time"
- Validation prevents accepting if both are changed

### 2. Smart Plot Swapping ↔️
- Changing position now **swaps** the two plots
- Both plots must have matching spans (e.g., both 1×1 or both 2×2)
- Clear error message if spans don't match:
  ```
  Cannot swap: Span mismatch.
  
  Source: 1×1 span
  Target: 2×2 span
  
  Please make both plots 1×1 first, then swap.
  ```

### 3. Improved Dialog Layout
- Blue info label at top explains the constraint
- Position group labeled "(Swap with target cell)"
- Span group labeled "(Multi-cell)"
- Inline notes explain what will happen

## Technical Details

### Files Modified

**plot_organizer/ui/dialogs.py**
- Added `_initial_row`, `_initial_col`, `_initial_rowspan`, `_initial_colspan` tracking
- Added `_on_position_changed()` - locks span controls when position changes
- Added `_on_span_changed()` - locks position controls when span changes
- Added `_validate_and_accept()` - prevents accepting if both changed
- Modified `get_settings()` to return `position_changed` and `span_changed` flags

**plot_organizer/ui/grid_board.py**
- Added `swap_plots(tile1, tile2)` method
  - Validates matching spans
  - Returns `(success, message)` tuple
  - Performs actual swap by removing and re-adding widgets

**plot_organizer/ui/main_window.py**
- Updated `_on_tile_settings()` handler
  - Separate logic for position vs span changes
  - Position change → calls `swap_plots()`
  - Span change → calls `move_plot()` at same position
  - Shows appropriate success/error messages

### Tests
Added 2 new tests in `test_grid_operations.py`:
- ✅ `test_swap_plots_success()` - Verifies swapping with matching spans
- ✅ `test_swap_plots_span_mismatch()` - Verifies rejection of mismatched spans

**All 24 tests pass** (2 new + 22 existing)

## Usage Examples

### Example 1: Swap Two 1×1 Plots
1. Right-click plot at (0,0) → "Plot Settings..."
2. Change "Start Row: 1", "Start Column: 1"
3. Click OK
4. ✅ Success! Plots swapped

### Example 2: Try to Swap Plots with Different Spans
1. Create plot at (0,0) with 1×1 span
2. Create plot at (1,1) with 2×2 span
3. Right-click plot at (0,0) → "Plot Settings..."
4. Try to change position to (1,1)
5. ❌ Error: "Cannot swap: Span mismatch. Please make both plots 1×1 first."

### Example 3: Change Span (Not Position)
1. Right-click plot → "Plot Settings..."
2. Change "Rows to span: 2"
3. Position controls automatically disable
4. Click OK
5. ✅ Plot now spans 2 rows at same position

### Example 4: Workflow to Swap Plots with Different Spans
1. Plot A at (0,0) is 2×2
2. Plot B at (2,2) is 1×1
3. First, make Plot A 1×1:
   - Right-click Plot A → Settings
   - Change "Rows to span: 1", "Columns to span: 1"
   - OK
4. Now swap:
   - Right-click Plot A → Settings
   - Change position to (2,2)
   - OK
5. ✅ Plots swapped!

## Behavior Details

### Auto-Locking
- As soon as you change position spinbox, span spinboxes gray out
- As soon as you change span spinbox, position spinboxes gray out
- Reopen dialog to reset and change the other property

### Validation
- Cannot accept dialog if both position AND span were changed
- Warning dialog explains: "Reset one of them to proceed"
- Clear feedback before attempting operation

### Swap Logic
1. Check if target position is same as current → "No change" message
2. Get tile at target position
3. Check if both tiles have matching spans
4. If mismatch → Show detailed error with current spans
5. If match → Remove both, add back swapped → Success message

### Edge Cases Handled
- ✅ Target tile doesn't exist → Error
- ✅ Moving to same position → Info message
- ✅ Span mismatch → Detailed error with instructions
- ✅ Only one property changed → Works smoothly
- ✅ Neither property changed → Accepts (no-op)

## Breaking Changes

None - existing workflows still work, just with better validation and clearer feedback.

## Known Limitations

- Can't swap and change span in single operation (by design)
- Must manually make spans match before swapping
- No automatic span adjustment when swapping

## What's Next

The plot management system is now mature. Next priorities:
1. Whole-grid export to PDF/SVG/PNG
2. Project save/load
3. Advanced CSV loading wizard

