# Contributing to quick-plot

Thank you for your interest in contributing! This guide covers everything you need to get started.

## Getting Started

### Prerequisites

- Python 3.10 or later
- Git

### Setup

```bash
git clone https://github.com/<your-username>/PlotOrganizer.git
cd PlotOrganizer

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
```

### Run the App

```bash
quick-plot
# or
python -m plot_organizer.app
```

### Run Tests

```bash
pytest
```

All 107+ tests should pass. Tests use an offscreen Qt backend so no display is required.

## How to Contribute

### Reporting Bugs

Open a GitHub Issue with:
- What you did
- What you expected
- What actually happened
- Your Python version and OS
- A minimal CSV or `.ppo` project file if relevant

### Suggesting Features

Open a GitHub Issue describing the feature and the use case it solves. Check `docs/roadmap.md` first — it may already be on the list.

### Submitting a Pull Request

1. Fork the repo and create a branch from `main`
2. Make your changes
3. Add tests for any new behavior (`plot_organizer/tests/`)
4. Run `pytest` and confirm all tests pass
5. Open a PR against `main` with a clear description of what changed and why

Keep PRs focused — one feature or bug fix per PR makes review much faster.

## Code Style

- Follow existing patterns in the codebase
- Use type hints where the existing code does
- Keep comments minimal — only when the *why* is non-obvious
- No trailing whitespace; no print statements left in production code

## Project Layout

```
plot_organizer/
├── models/       # Pure Python dataclasses (no Qt)
├── services/     # Business logic: load, plot, render, export, project I/O
├── ui/           # Qt widgets: main window, grid board, dialogs
├── tests/        # pytest test suite
├── app.py        # CLI entry point
└── api.py        # Programmatic API
docs/             # User and developer documentation
examples/         # Example scripts
```

## Running Tests in CI Mode

To run tests without a physical display (as CI does):

```bash
QT_QPA_PLATFORM=offscreen pytest
```
