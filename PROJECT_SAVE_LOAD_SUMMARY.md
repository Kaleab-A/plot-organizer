# Project Save/Load Feature Summary

## Overview
Added comprehensive save/load functionality with both GUI and CLI support, enabling users to save workspace state to JSON files and load them back. Also includes programmatic API for automated plot generation.

## Implementation Date
November 27, 2025

## Changes Made

### 1. Project Service (`plot_organizer/services/project_service.py`)
- **Added** `save_workspace()`: Serializes current UI state to JSON
- **Added** `load_workspace()`: Deserializes JSON back to UI state
- **Features**:
  - Relative path storage (paths stored relative to .ppo file)
  - Version checking (currently 0.9.0)
  - Graceful error handling for missing files
  - Preserves all plot parameters including multi-column hue

### 2. PlotTile Serialization (`plot_organizer/ui/grid_board.py`)
- **Added** `get_plot_data()`: Extracts all plot parameters for saving
- **Added** `set_plot_from_data()`: Reconstructs plot from saved data
- **Captures**:
  - Datasource reference
  - X, Y axes
  - Hue (single column, multi-column, or None)
  - SEM settings (column and precomputed flag)
  - Filter queries
  - Reference lines (hlines, vlines)
  - Plot style (line, markers)
  - Y-axis limits
  - Plot title

### 3. GridBoard Serialization (`plot_organizer/ui/grid_board.py`)
- **Added** `serialize_layout()`: Extracts all non-empty plots with positions
- **Returns**: List of plot descriptors with grid_position and plot data
- **Handles**:
  - Plot spanning (rowspan, colspan)
  - Multiple plots in grid
  - Empty cells

### 4. MainWindow Save/Load (`plot_organizer/ui/main_window.py`)
- **Added** File menu actions:
  - Save Project (Ctrl+S)
  - Save Project As... (Ctrl+Shift+S)
  - Load Project... (Ctrl+O)
- **Added** `load_project_from_file()`: Public method for loading projects (used by CLI)
- **Added** `_clear_workspace()`: Clears all current state before loading
- **Features**:
  - Tracks current project path
  - Shows project name in window title
  - Validates data sources on load
  - Warns about missing CSV files
  - Reconnects plot signals after loading

### 5. CLI Support (`plot_organizer/app.py`)
- **Complete rewrite** of `run()` function with argparse
- **CLI Modes**:
  
  **a) GUI with optional project load:**
  ```bash
  python -m plot_organizer.app                    # Empty workspace
  python -m plot_organizer.app project.ppo        # Load project
  ```
  
  **b) GUI with load and immediate export:**
  ```bash
  python -m plot_organizer.app project.ppo --export output.pdf
  ```
  
  **c) Headless mode (no GUI):**
  ```bash
  python -m plot_organizer.app project.ppo --export output.pdf --no-gui
  ```

- **Arguments**:
  - `project`: Optional .ppo file to load
  - `--no-gui`: Run without showing GUI (requires --export)
  - `--export OUTPUT`: Export grid to file
  - `--format {pdf,svg,eps,png}`: Export format (default: pdf)
  - `--width INCHES`: Export width (default: 11.0)
  - `--height INCHES`: Export height (default: 8.5)
  - `--dpi DPI`: DPI for PNG (default: 150)

- **Validation**: Prevents --no-gui without --export

### 6. Programmatic API (`plot_organizer/api.py`)
New module for creating projects programmatically!

**Functions**:
- `create_datasource(name, path, schema=None)`: Create datasource descriptor
- `create_plot(ds_id, x, y, ...)`: Create plot with all parameters
- `create_project(grid_size, datasources, plots)`: Assemble complete project
- `save_project_file(project, path)`: Save to .ppo file
- `load_project_file(path)`: Load from .ppo file
- `quick_project(ds_name, ds_path, plots)`: Convenience function for single-datasource projects

**Example**:
```python
from plot_organizer.api import *

# Create plots
plots = [
    create_plot("", x="time", y="value", 
                hue=["model", "dataset"],
                row=0, col=0),
    create_plot("", x="time", y="error",
                hlines=[0.5, 1.0],
                row=0, col=1),
]

# Create and save project
project = quick_project("Results", "data.csv", plots)
save_project_file(project, "experiment.ppo")
```

## Project File Format (.ppo)

JSON structure with the following schema:

```json
{
  "version": "0.9.0",
  "grid": {
    "rows": 2,
    "cols": 3
  },
  "data_sources": [
    {
      "id": "uuid",
      "name": "Display Name",
      "path": "relative/path/to/data.csv",
      "schema": [
        {
          "name": "column",
          "dtype": "float64",
          "var_type": "continuous",
          "categories": null,
          "notes": null
        }
      ]
    }
  ],
  "plots": [
    {
      "id": "uuid",
      "grid_position": {
        "row": 0,
        "col": 0,
        "rowspan": 1,
        "colspan": 2
      },
      "datasource_id": "uuid",
      "x": "time",
      "y": "accuracy",
      "hue": ["model", "dataset"],
      "sem_column": "fold",
      "sem_precomputed": false,
      "filter_query": {"experiment": "A"},
      "hlines": [0, 50, 100],
      "vlines": [10, 20],
      "style_line": true,
      "style_marker": true,
      "ylim": [0, 1],
      "title": "Experiment A Results"
    }
  ]
}
```

## Features Supported

All PlotOrganizer features are fully serializable:

- ✅ Multiple data sources with schemas
- ✅ Grid dimensions (rows, cols)
- ✅ Plot positions (row, col)
- ✅ Plot spanning (rowspan, colspan)
- ✅ X and Y axes
- ✅ **Multi-column hue** (list of columns)
- ✅ Single-column hue (backward compatible)
- ✅ SEM columns (computed or pre-computed)
- ✅ Filter queries for grouped data
- ✅ Horizontal and vertical reference lines
- ✅ Plot styles (line/markers/both)
- ✅ Custom Y-axis limits
- ✅ Plot titles

## Usage Examples

### 1. GUI Workflow

**Save:**
1. Create plots in GUI
2. File → Save Project (Ctrl+S)
3. Choose location and filename (.ppo extension)

**Load:**
1. File → Load Project... (Ctrl+O)
2. Select .ppo file
3. Workspace reconstructed with all plots

### 2. CLI Headless Export

Perfect for automated workflows:

```bash
# Create project programmatically
python create_plots.py  # Generates experiment.ppo

# Export without GUI
python -m plot_organizer.app experiment.ppo \
  --export figure.pdf \
  --no-gui \
  --format pdf \
  --width 15 \
  --height 5 \
  --dpi 300
```

### 3. Automation Workflow

Complete pipeline example:

```python
# 1. Process data
import pandas as pd
df = analyze_experiment()
df.to_csv("results.csv")

# 2. Create plots
from plot_organizer.api import *

plots = []
for i, condition in enumerate(["A", "B", "C"]):
    plots.append(create_plot(
        "",
        x="time",
        y="metric",
        filter_query={"condition": condition},
        row=0, col=i,
        title=f"Condition {condition}"
    ))

project = quick_project("Experiment", "results.csv", plots)
save_project_file(project, "experiment.ppo")

# 3. Export
import subprocess
subprocess.run([
    "python", "-m", "plot_organizer.app",
    "experiment.ppo",
    "--export", "results.pdf",
    "--no-gui"
])
```

## Testing

Created comprehensive test suites:

**`test_project_save_load.py`** (6 tests):
- ✅ Save/load round-trip
- ✅ Multi-column hue serialization
- ✅ Relative path handling
- ✅ Version compatibility checking
- ✅ Empty project handling
- ✅ Plot spanning preservation

**`test_programmatic_api.py`** (13 tests):
- ✅ Datasource creation
- ✅ Plot creation with all parameters
- ✅ Multi-column hue
- ✅ SEM settings
- ✅ Reference lines
- ✅ Spanning plots
- ✅ Project assembly
- ✅ File I/O
- ✅ Quick project convenience function
- ✅ JSON serialization

**All 105 tests pass** (86 existing + 19 new)

## Error Handling

Robust error handling throughout:

- **Missing CSV files**: Lists missing files, loads others, continues
- **Version incompatibility**: Checks version, rejects incompatible
- **Corrupt JSON**: Catches parsing errors with helpful messages
- **Invalid plot parameters**: Logs warnings, skips problematic plots
- **Schema mismatches**: Could warn user (future enhancement)
- **CLI validation**: Prevents invalid argument combinations

## Files Added

1. `plot_organizer/api.py` - Programmatic API
2. `plot_organizer/tests/test_project_save_load.py` - Save/load tests
3. `plot_organizer/tests/test_programmatic_api.py` - API tests
4. `examples/create_example_project.py` - Example script
5. `examples/README.md` - Examples documentation

## Files Modified

1. `plot_organizer/services/project_service.py` - Save/load functions
2. `plot_organizer/ui/grid_board.py` - Serialization methods
3. `plot_organizer/ui/main_window.py` - Save/load actions
4. `plot_organizer/ui/data_manager.py` - clear_all() method
5. `plot_organizer/app.py` - CLI argument parsing

## Benefits

✅ **Reproducibility**: Save and reload exact workspace state  
✅ **Version Control**: JSON files work with git  
✅ **Automation**: Generate plots programmatically  
✅ **Batch Processing**: Headless export for CI/CD pipelines  
✅ **Human-Readable**: JSON format, easy to inspect/edit  
✅ **Portable**: Relative paths allow moving projects  
✅ **Complete**: All features supported

## Future Enhancements

- Auto-save functionality
- Recent projects menu
- Project templates
- Batch export (export each plot separately)
- Schema validation on load
- Migration tools for format updates

## Summary

The project save/load system is fully implemented with both GUI and CLI support. Users can save complete workspace state, load it back, and programmatically generate plots for automated workflows. The system is robust, well-tested, and supports all PlotOrganizer features including the newly added multi-column hue.

