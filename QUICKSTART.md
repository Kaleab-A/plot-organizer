git # Quick Start Guide

## Installation

```bash
cd /Users/azezewka/Dropbox/PlotOrganizer
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the App

```bash
python -m plot_organizer.app
```

## Creating Your First Plot

1. **Load a CSV**:
   - Click **Data → Add CSV…** (or use the "Add CSV…" button in the Data Sources dock on the left)
   - Navigate to `plot_organizer/tests/test_csv/organizations-10000.csv` (or any CSV file)
   - The file will be loaded and appear in the Data Sources list

2. **Create a Plot**:
   - Click **Plot → Quick Plot…**
   - Select your data source from the dropdown
   - Choose columns for:
     - **x**: e.g., `Founded` (year)
     - **y**: e.g., `Number of employees`
     - **hue** (optional): e.g., `Country` (will color lines by category)
     - **SEM column** (optional): e.g., `subject` or `trial` (computes mean ± SEM with shaded region)
     - **Groups** (optional): Multi-select columns to create faceted plots (one plot per unique combination)
   - **Reference Lines** (optional):
     - **Horizontal**: Enter y-values separated by commas (e.g., `0, 50, 100`)
     - **Vertical**: Enter x-values separated by commas (e.g., `2020, 2021, 2022`)
     - These create black dashed lines for marking thresholds, baselines, etc.
   - Click **OK**
   - The plot(s) will appear in the grid tiles

3. **Interact with Plots**:
   - Plots now take maximum space with clean minimal UI
   - Each tile has its own independent Matplotlib canvas

4. **Grow the Grid**:
   - Click **Grid → + Row** or **Grid → + Col** to add more space for plots
   - Plots automatically place in the first empty tile

## Example with Test Data

Using `organizations-10000.csv`:

**Simple plot:**
- **x**: `Founded` → shows timeline
- **y**: `Number of employees` → shows company size
- **hue**: Leave blank for a single line

**Faceted plot (groups):**
- **x**: `Index`
- **y**: `Number of employees`
- **Groups**: Select `Country` (will create one plot per country, up to 50)
- All plots will share the same axis ranges for easy comparison

## What's Implemented

✅ CSV loading with automatic type inference  
✅ Plot dialog with x, y, hue, SEM column, groups, and reference lines  
✅ **Reference Lines**: Horizontal and vertical dashed lines for thresholds/markers  
✅ **SEM (Standard Error of the Mean)**: Shaded regions showing mean ± SEM  
✅ Group faceting (multi-select columns, cross-product expansion)  
✅ Shared axes across grouped plots (automatic, SEM-aware)  
✅ **Automatic aggregation**: Duplicate (x, hue) values are averaged for clean plots  
✅ **Plot settings**: Right-click plots to configure position and spanning (multi-cell plots)  
✅ **Context menu**: Right-click for settings, clear plot  
✅ **Remove rows/cols**: Grid → - Row/Col (only if empty)  
✅ **Export**: Whole-grid export to PDF/SVG/EPS/PNG with configurable size and DPI  
✅ Clean UI with maximized plot space  
✅ Dynamic grid growth  

## Coming Soon

- Drag-and-drop to rearrange plots
- Project save/load
- Advanced NA handling wizard
- Type confirmation dialog

