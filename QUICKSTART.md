# Quick Start Guide

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
   - Click **OK**
   - The plot will appear in the first empty grid tile

3. **Interact with Plots**:
   - Use the toolbar below each plot to pan, zoom, or save
   - Each tile has its own independent Matplotlib canvas

4. **Grow the Grid**:
   - Click **Grid → + Row** or **Grid → + Col** to add more space for plots

## Example with Test Data

Using `organizations-10000.csv`:
- **x**: `Founded` → shows timeline
- **y**: `Number of employees` → shows company size
- **hue**: Leave blank for a single line, or try `Industry` (note: many categories!)

## What's Implemented

✅ CSV loading with automatic type inference  
✅ Quick Plot dialog (x, y, hue)  
✅ Matplotlib canvas with toolbar in each tile  
✅ Dynamic grid growth  

## Coming Soon

- Group faceting (create multiple plots from one spec)
- Shared axes across grouped plots
- Drag-and-drop to rearrange plots
- Whole-grid export to PDF/SVG/PNG
- Project save/load

