# quick-plot

[![Tests](https://github.com/<owner>/PlotOrganizer/actions/workflows/tests.yml/badge.svg)](https://github.com/<owner>/PlotOrganizer/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

A desktop Python GUI (PySide6) for organizing multiple line plots into a customizable grid — load a CSV, configure plots through dialogs, and export to PDF/SVG/EPS/PNG. No coding required.

## Features

- **CSV loading** with automatic type inference (categorical, continuous, ordinal)
- **Create plots** with x, y, hue, SEM, groups, plot style, and reference lines
- **Multi-column hue** — combine multiple categorical columns for richer legend groupings
- **Group faceting** — one plot per unique combination, all sharing the same axis scale
- **SEM plotting** — mean ± SEM as a translucent shaded region (computed or pre-computed)
- **Reference lines** — horizontal and vertical dashed lines for thresholds and markers
- **Error marker annotations** — annotated error bars at specific plot positions
- **Plot style** — choose line, markers, or both
- **Grid management** — add/remove rows and columns, multi-cell spanning, grid reset
- **Project save/load** — portable JSON `.ppo` files
- **Export** — whole-grid PDF/SVG/EPS/PNG with configurable size and DPI
- **Programmatic API** — create projects from Python scripts
- **CLI / headless export** — automate export pipelines without a GUI

## Installation

```bash
pip install quick-plot
```

Or from source:

```bash
git clone https://github.com/<owner>/PlotOrganizer.git
cd PlotOrganizer
pip install -e .
```

## Quick Start

```bash
# Launch the GUI
quick-plot

# Load a saved project
quick-plot my_project.ppo

# Headless export (no GUI)
quick-plot my_project.ppo --no-gui --export output.pdf
```

See [docs/quickstart.md](docs/quickstart.md) for a step-by-step walkthrough.

## Programmatic API

```python
from plot_organizer.api import quick_project, create_plot, save_project_file

plots = [
    create_plot("", x="time", y="accuracy", hue=["model", "dataset"], row=0, col=0),
    create_plot("", x="time", y="loss", hlines=[0.5], row=0, col=1),
]

project = quick_project("Experiment", "data/results.csv", plots)
save_project_file(project, "experiment.ppo")
```

See `examples/` for runnable scripts.

## Documentation

| Document | Description |
|----------|-------------|
| [docs/quickstart.md](docs/quickstart.md) | Installation and first-use guide |
| [docs/features.md](docs/features.md) | Complete feature reference |
| [docs/roadmap.md](docs/roadmap.md) | Planned features and known gaps |
| [docs/design.md](docs/design.md) | Architecture and design decisions |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |

## Running Tests

```bash
pytest
```

## Project Structure

```
plot_organizer/
├── models/     # Pure Python dataclasses (no Qt dependencies)
├── services/   # Business logic: CSV loading, plotting, export, project I/O
├── ui/         # Qt widgets: main window, grid board, dialogs
├── tests/      # pytest test suite (107+ tests)
├── app.py      # CLI entry point
└── api.py      # Programmatic API
examples/       # Runnable example scripts
docs/           # Documentation
```

## License

MIT — see [LICENSE](LICENSE).
