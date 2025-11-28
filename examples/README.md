# PlotOrganizer Examples

This directory contains example scripts and project files demonstrating how to use PlotOrganizer programmatically.

## Creating Projects Programmatically

### Basic Example

```python
from plot_organizer.api import create_plot, quick_project, save_project_file

# Create plots
plots = [
    create_plot("", x="time", y="value", row=0, col=0),
    create_plot("", x="time", y="error", row=0, col=1),
]

# Create project
project = quick_project(
    datasource_name="Experiment Results",
    datasource_path="data/results.csv",
    plots=plots
)

# Save to file
save_project_file(project, "my_project.ppo")
```

### Grouped Plots (NEW!)

**The easiest way** to create multiple plots with shared y-axis limits:

```python
from plot_organizer.api import quick_grouped_project, save_project_file

# Create project with grouped plots
# This creates one plot per unique combination of group columns
# and automatically computes shared y-axis limits!
project = quick_grouped_project(
    datasource_name="Experiment",
    datasource_path="data/results.csv",
    x="time",
    y="accuracy",
    groups=["species", "treatment"],  # Creates plots for each combination
    hue=["model"],  # Optional: color by model
    layout="row",  # "row" (left-to-right) or "col" (top-to-bottom)
)

save_project_file(project, "grouped_experiment.ppo")

# If you have 3 species × 2 treatments, this creates 6 plots automatically!
# All 6 plots share the same auto-computed y-axis limits for easy comparison.
```

### Advanced Example with All Features

```python
from plot_organizer.api import create_plot, quick_project, save_project_file

plots = [
    # Multi-column hue with SEM
    create_plot(
        "",
        x="time",
        y="accuracy",
        hue=["model", "dataset"],  # Multi-column hue
        sem_column="fold",
        sem_precomputed=False,
        row=0,
        col=0,
        title="Model Comparison"
    ),
    
    # Reference lines and custom limits
    create_plot(
        "",
        x="time",
        y="loss",
        hlines=[0.5, 1.0],  # Horizontal reference lines
        vlines=[100, 200],  # Vertical reference lines
        ylim=(0, 2),  # Custom y-axis limits
        row=0,
        col=1,
        title="Training Loss"
    ),
    
    # Spanning plot with filter
    create_plot(
        "",
        x="epoch",
        y="metric",
        filter_query={"experiment": "A"},  # Filter data
        rowspan=2,  # Span 2 rows
        colspan=2,  # Span 2 columns
        style_line=True,
        style_marker=True,  # Both lines and markers
        row=1,
        col=0,
        title="Experiment A Results"
    ),
]

project = quick_project("ML Experiments", "data/results.csv", plots)
save_project_file(project, "ml_experiments.ppo")
```

### Advanced Grouped Plots

For more control over grouped plots:

```python
from plot_organizer.api import (
    create_datasource,
    create_grouped_plots,
    create_project,
    save_project_file
)

# Create datasource
ds = create_datasource("Experiment", "data/results.csv")

# Create grouped plots with full control
plots = create_grouped_plots(
    datasource_id=ds["id"],
    dataframe_path="data/results.csv",  # Needed to compute shared limits
    x="time",
    y="accuracy",
    groups=["species", "treatment", "dosage"],  # Multiple grouping columns
    start_row=0,
    start_col=0,
    layout="row",  # or "col" for vertical stacking
    hue=["model", "dataset"],  # Multi-column hue
    sem_column="trial",
    sem_precomputed=False,
    hlines=[0.5, 0.9],
    vlines=[10, 20],
    style_line=True,
    style_marker=True,
    # ylim=(0, 1),  # Optional: manual y-limits (otherwise auto-computed)
)

# Manually create more plots if needed
more_plots = [
    create_plot(ds["id"], x="time", y="loss", row=1, col=0),
]

# Combine all plots
all_plots = plots + more_plots

# Create project
project = create_project(
    grid_size=(2, len(plots)),
    datasources=[ds],
    plots=all_plots
)

save_project_file(project, "advanced_grouped.ppo")
```

## Running the Examples

### 1. Create the example project

```bash
python examples/create_example_project.py
```

This creates `examples/example_project.ppo`.

### 2. Open in GUI

```bash
python -m plot_organizer.app examples/example_project.ppo
```

### 3. Export without GUI (headless)

```bash
# Export to PDF
python -m plot_organizer.app examples/example_project.ppo \
  --export output.pdf --no-gui --format pdf

# Export to PNG with high DPI
python -m plot_organizer.app examples/example_project.ppo \
  --export output.png --no-gui --format png --dpi 300

# Custom size
python -m plot_organizer.app examples/example_project.ppo \
  --export output.svg --no-gui --format svg --width 14 --height 10
```

## CLI Options

### Loading Projects

```bash
# Open GUI with project loaded
python -m plot_organizer.app project.ppo

# Load and immediately export (no GUI)
python -m plot_organizer.app project.ppo --export output.pdf --no-gui
```

### Export Options

- `--export OUTPUT`: Output file path
- `--no-gui`: Run without showing GUI (requires --export)
- `--format {pdf,svg,eps,png}`: Output format (default: pdf)
- `--width INCHES`: Width in inches (default: 11.0)
- `--height INCHES`: Height in inches (default: 8.5)
- `--dpi DPI`: DPI for PNG exports (default: 150)

## Automation Workflow

Here's a typical workflow for automated plot generation:

```python
# 1. Generate or process your data
import pandas as pd
df = process_experimental_data()
df.to_csv("results.csv", index=False)

# 2. Create plots programmatically
from plot_organizer.api import *

plots = []
for condition in ["A", "B", "C"]:
    plot = create_plot(
        "",
        x="time",
        y="measurement",
        filter_query={"condition": condition},
        row=0,
        col=len(plots),
        title=f"Condition {condition}"
    )
    plots.append(plot)

project = quick_project("Experiment", "results.csv", plots)
save_project_file(project, "experiment.ppo")

# 3. Export without GUI
import subprocess
subprocess.run([
    "python", "-m", "plot_organizer.app",
    "experiment.ppo",
    "--export", "figure.pdf",
    "--no-gui",
    "--format", "pdf",
    "--width", "15",
    "--height", "5"
])
```

## Features Supported in Project Files

All PlotOrganizer features can be specified programmatically:

- ✅ Multiple data sources
- ✅ Grid layout with custom dimensions
- ✅ Plot positioning (row, col)
- ✅ Plot spanning (rowspan, colspan)
- ✅ X and Y axes
- ✅ Single or multi-column hue
- ✅ SEM columns (computed or pre-computed)
- ✅ Filter queries (for grouped data)
- ✅ Horizontal and vertical reference lines
- ✅ Plot styles (lines, markers, or both)
- ✅ Custom Y-axis limits
- ✅ Plot titles

## Project File Format

Project files (.ppo) are JSON with this structure:

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
      "name": "My Data",
      "path": "data/file.csv",
      "schema": [...]
    }
  ],
  "plots": [
    {
      "id": "uuid",
      "grid_position": {"row": 0, "col": 0, "rowspan": 1, "colspan": 1},
      "datasource_id": "uuid",
      "x": "time",
      "y": "value",
      "hue": ["column1", "column2"],
      "sem_column": null,
      "sem_precomputed": false,
      "filter_query": null,
      "hlines": [0, 50],
      "vlines": [10],
      "style_line": true,
      "style_marker": false,
      "ylim": [0, 100],
      "title": "My Plot"
    }
  ]
}
```

You can edit these files manually or generate them with the API!

