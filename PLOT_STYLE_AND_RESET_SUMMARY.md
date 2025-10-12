# Plot Style Customization + Grid Reset (v0.8)

Quick summary of the two new features added in version 0.8.

---

## 1. Plot Style Customization

### What It Does
Lets you choose how data is displayed: line, markers, or both.

### Where to Find It
**Plot → Quick Plot... dialog**, in the "Plot Style" section:
- ☑ **Line** (default: checked) - Traditional line plot
- ☐ **Markers** (default: unchecked) - Scatter-style markers

### Examples
- **Line only** (default): Clean continuous lines
- **Markers only**: Emphasize individual data points (good for sparse data)
- **Both**: Line with markers for extra visibility (good for presentations)

### Key Points
✅ Works with hue (different colors keep their style)  
✅ Works with SEM (shaded regions unaffected)  
✅ Works with grouped plots (style applied to all)  
✅ Preserved in exports (PDF/SVG/EPS/PNG)  
✅ Can be mixed across different plots in the grid  

### Code
```python
# In PlotTile
tile.set_plot(
    df=df, x='x', y='y',
    style_line=True,   # Show lines
    style_marker=True  # Show markers
)
```

---

## 2. Grid Reset

### What It Does
Clears all plots and resets grid to default 2×3 size in one action.

### Where to Find It
**Grid → Reset Grid...** menu option

### What Happens
1. Confirmation dialog appears (are you sure?)
2. All plots cleared from all tiles
3. Grid resized to 2 rows × 3 columns
4. Fresh empty tiles created
5. Success message shown

### When to Use It
- Starting a new analysis session
- Grid accidentally grew too large (10×10, etc.)
- Want to clear everything quickly
- Testing/development workflows

### Safety
⚠️ Requires explicit confirmation (dialog defaults to "No")  
⚠️ Cannot be undone (all plot configurations lost)  
✅ Clear warning message explains what will happen  

### Code
```python
# In GridBoard
board.reset_to_size(2, 3)  # rows, cols
```

---

## Testing

Both features fully tested:
- **Plot Style**: 9 tests covering all style combinations, interaction with hue/SEM, clearing
- **Grid Reset**: 6 tests covering basic reset, plot clearing, size changes, widget cleanup

All 60 tests passing.

---

## Files Changed

### Plot Style
- `plot_organizer/ui/dialogs.py` - Added checkboxes
- `plot_organizer/ui/grid_board.py` - Style logic
- `plot_organizer/ui/main_window.py` - Pass parameters
- `plot_organizer/services/export_service.py` - Export with style
- `plot_organizer/tests/test_plot_style.py` - Tests

### Grid Reset
- `plot_organizer/ui/main_window.py` - Menu + action
- `plot_organizer/ui/grid_board.py` - Reset method
- `plot_organizer/tests/test_reset_grid.py` - Tests

### Documentation
- `IMPLEMENTATION_PROGRESS.md` - Updated to v0.8
- `QUICKSTART.md` - Usage instructions
- `README.md` - Feature list
- `CHANGES_v0.8.md` - Detailed changelog

---

## Quick Reference

| Feature | Default | Options | Preserved in Export? |
|---------|---------|---------|---------------------|
| **Line** | ✅ Checked | Line plot | Yes |
| **Markers** | ❌ Unchecked | Scatter markers | Yes |
| **Both** | - | Line + markers | Yes |

| Action | Location | Confirmation? | Undoable? |
|--------|----------|---------------|-----------|
| **Reset Grid** | Grid menu | Yes (required) | No |

---

## Version History

- **v0.1-0.4**: Core functionality (CSV, plotting, grid, export)
- **v0.5**: SEM column support
- **v0.5.1**: Fixed SEM y-axis scaling for grouped plots
- **v0.6**: Reference lines (horizontal/vertical)
- **v0.7**: Pre-computed SEM support
- **v0.8**: **Plot style customization + Grid reset** ← You are here

