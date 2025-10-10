# Changes in v0.4 - Export Feature & Dialog Fix

## Summary

Added comprehensive grid export functionality (PDF/SVG/EPS/PNG) and fixed the Plot Settings dialog closing issue.

## Bug Fixes

### Plot Settings Dialog Not Closing ✅
**Problem:** Dialog required multiple clicks on OK/Cancel buttons to close.

**Solution:** 
- Added `_updating` flag to prevent recursive signal triggers
- Used `Qt.QueuedConnection` for signal connections
- Prevents event loop issues when enabling/disabling controls

## New Features

### 1. Whole-Grid Export 📤
**Access:** Export menu → "Export Grid..."

Export your entire grid layout to professional formats:
- **PDF** - Vector format, perfect for papers/reports
- **SVG** - Vector format, web-friendly
- **EPS** - Vector format, for LaTeX/scientific publishing
- **PNG** - Raster format, for presentations

**Features:**
- Preserves grid layout with proper spacing
- Handles multi-cell spanning plots correctly
- Re-renders all plots from data (not screenshots)
- Configurable page size (A4, Letter, Custom)
- Adjustable DPI for PNG exports (72-600)
- Uses Matplotlib's GridSpec for precise layout control

### 2. Export Dialog 🎨
Comprehensive configuration dialog with:

**Format Selection:**
- Radio buttons for PDF/SVG/EPS/PNG
- Clear indication of vector vs raster

**Page Size:**
- Presets: A4 (8.27×11.69"), Letter (8.5×11")
- Custom dimensions (1-100 inches)
- Width and height controls

**Resolution (PNG only):**
- DPI control (72-600)
- Automatically enables/disables based on format
- Default: 150 DPI (good quality)

### 3. Export Service
New comprehensive export engine:
- `export_grid()` - Whole-grid export with spanning support
- `_render_plot_to_ax()` - Re-renders plot data to matplotlib axis
- Handles filters, aggregation, titles automatically
- Uses non-interactive Agg backend for clean output

## Technical Details

### Files Modified/Created

**plot_organizer/ui/dialogs.py**
- Fixed `PlotSettingsDialog` signal connections
- Added `_updating` flag to prevent recursion
- Added `ExportDialog` class with format/size/DPI controls

**plot_organizer/services/export_service.py**
- Complete rewrite with `export_grid()` function
- Uses `matplotlib.gridspec.GridSpec` for layout
- Handles spanning plots correctly
- Tracks processed cells to avoid duplicate rendering
- Re-applies aggregation and filters

**plot_organizer/ui/main_window.py**
- Added Export menu with "Export Grid..." action
- Added `_action_export_grid()` handler
- Validates that plots exist before showing dialog
- Shows file save dialog with format-specific filters
- Displays success/error messages

**plot_organizer/ui/__init__.py**
- Exported `ExportDialog`

### Export Algorithm

1. **Create Figure:** New matplotlib figure with specified dimensions
2. **Create GridSpec:** Match the grid layout (rows × cols)
3. **Track Processed Cells:** Prevent duplicate rendering of spanning plots
4. **Iterate Grid:**
   - For each non-empty tile
   - Get position and span
   - Create subplot with correct span
   - Re-render plot data
5. **Save:** Use `savefig()` with format, DPI, bbox_inches='tight'

### Spanning Plot Handling
- Marks all cells occupied by a spanning plot as "processed"
- Only renders at the plot's starting position
- Uses `GridSpec` slicing: `gs[row:row+rowspan, col:col+colspan]`
- Preserves multi-cell layout in export

## Usage Examples

### Example 1: Export to PDF
1. Create and organize your plots
2. Export → "Export Grid..."
3. Select "PDF (vector)"
4. Choose page size (e.g., Letter)
5. Click OK
6. Choose save location
7. ✅ High-quality PDF created!

### Example 2: High-Resolution PNG for Presentation
1. Export → "Export Grid..."
2. Select "PNG (raster)"
3. Set DPI to 300 (high quality)
4. Choose Custom size: 16×9 inches (widescreen)
5. Click OK, save
6. ✅ Presentation-ready image!

### Example 3: SVG for Web
1. Export → "Export Grid..."
2. Select "SVG (vector)"
3. Default settings
4. Click OK, save
5. ✅ Scalable web graphic!

## Format Comparison

| Format | Type   | Use Case                          | Pros                          |
|--------|--------|-----------------------------------|-------------------------------|
| PDF    | Vector | Papers, reports, printing         | Crisp at any zoom, embedded   |
| SVG    | Vector | Web, presentations                | Scalable, small file size     |
| EPS    | Vector | LaTeX, scientific publications    | Standard for journals         |
| PNG    | Raster | Quick sharing, presentations      | Universal support             |

## Behavior Notes

- **Empty grid check:** Won't export if no plots exist
- **Automatic aggregation:** Same as on-screen (duplicate x-values averaged)
- **Title preservation:** Copies titles from on-screen plots
- **Filter application:** Re-applies group filters during export
- **Tight layout:** Uses `bbox_inches='tight'` to minimize whitespace
- **Non-interactive backend:** Uses Agg backend for clean, reproducible output

## File Size Guidelines

**Vector formats (PDF/SVG/EPS):**
- Independent of dimensions
- Scales infinitely
- Typically 50-500 KB depending on data complexity

**Raster format (PNG):**
- Depends on dimensions × DPI
- Example: 11×8.5" @ 150 DPI ≈ 500 KB
- Example: 11×8.5" @ 300 DPI ≈ 2 MB

## Known Limitations

- No per-plot export yet (whole grid only)
- Cannot adjust spacing/margins (uses defaults)
- No font embedding options (uses system defaults)
- No export preview
- No batch export

## What's Next

With export complete, the remaining high-priority features are:
1. ✅ Whole-grid export (DONE!)
2. ❌ Project save/load (.ppo.json)
3. ❌ Advanced CSV wizard (NA handling, type confirmation)
4. ❌ Per-plot export (from context menu)

## Testing

All 24 tests pass ✅

Tested manually:
- ✅ Export to PDF
- ✅ Export to SVG
- ✅ Export to PNG with various DPI
- ✅ Spanning plots render correctly
- ✅ Empty grid handled gracefully
- ✅ Dialog closes properly on first click

