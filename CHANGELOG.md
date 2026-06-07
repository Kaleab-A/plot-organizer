# Changelog

All notable changes to quick-plot are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [0.8.0] – 2025-10-12

### Added
- **Plot Style Customization**: Choose how data is displayed — line only (default), markers only, or line + markers. Option exposed in the Create Plot dialog.
- **Grid Reset**: `Grid → Reset Grid...` clears all plots and restores the default 2×3 layout. Requires confirmation; cannot be undone.

### Changed
- Export service updated to apply plot style settings (line/marker format) when rendering plots to file.

### Tests
- `test_plot_style.py` — 9 tests for all style combinations, interaction with hue/SEM, and clearing behavior.
- `test_reset_grid.py` — 6 tests for basic reset, plot clearing, size changes, and widget cleanup.

---

## [0.7.0] – 2025-10-12

### Added
- **Pre-computed SEM support**: Toggle between two SEM modes with the new "Pre-computed SEM" checkbox in the Create Plot dialog.
  - **Unchecked** (default): groups data by the SEM column and computes mean ± SEM across groups.
  - **Checked**: reads SEM values directly from the selected column (for pre-aggregated data).
- Automatic averaging with console warning when duplicate x-values exist in pre-computed mode.
- `_compute_precomputed_sem_stats()` helper in `plot_service.py` for shared-limit calculations.

### Tests
- `test_precomputed_sem.py` — 11 tests covering single-row, duplicate-x, hue, shared limits, NaN/zero values, and backward compatibility.

---

## [0.6.0] – 2025-10-10

### Added
- **Reference Lines**: Add horizontal and/or vertical dashed reference lines to any plot.
  - Entered as comma-separated numbers in the Create Plot dialog (e.g., `0, 50, 100`).
  - Style: black, dashed, 70% opacity.
  - Shared across all plots when using group faceting.
  - Preserved in PDF/SVG/EPS/PNG exports.

### Tests
- `test_reference_lines.py` — 9 tests covering horizontal, vertical, combined, cleared, and interaction with hue/SEM.

---

## [0.5.1] – 2025-10-10

### Fixed
- **SEM-aware shared axis limits**: Grouped plots with a SEM column previously used raw y-value range for shared limits, producing an axis much larger than the plotted data. Limits are now computed from the aggregated mean ± SEM values, matching what is actually rendered.
- Added `shared_limits_with_sem()` to `plot_service.py`; main window selects it automatically when a SEM column is present.

### Tests
- `test_sem_limits.py` — 5 tests verifying tighter limits vs raw data, hue handling, empty subsets, and backward compatibility.

---

## [0.5.0] – 2025-10-10

### Added
- **SEM (Standard Error of the Mean) plotting**: Select a "SEM column" in the Create Plot dialog to show mean ± SEM as a translucent shaded region around each line.
  - SEM column groups observations (e.g., by subject or trial), computes per-group means, then derives the SEM across groups.
  - Works with hue and group faceting.
  - Preserved in all export formats.

### Tests
- `test_sem_plotting.py` — 5 tests for grouping/aggregation, hue interaction, backward compatibility, and numerical accuracy.

---

## [0.4.0]

### Added
- **Whole-grid export** (`Export → Export Grid...`) to PDF, SVG, EPS, or PNG.
  - Configurable page size (A4, Letter, custom dimensions).
  - DPI control for PNG exports.
  - Plots are re-rendered from data (not screenshots); spanning plots handled correctly.
- `ExportDialog` for format, page size, and DPI configuration.
- `export_service.py` with `export_grid()` using Matplotlib `GridSpec` for precise layout.

### Fixed
- `PlotSettingsDialog` required multiple OK/Cancel clicks to close; fixed by adding `_updating` guard and using `Qt.QueuedConnection`.

---

## [0.3.1]

### Changed
- **Plot Settings dialog**: Position and span are now mutually exclusive — changing one locks the other.
- Changing a plot's position now **swaps** it with the plot at the target cell (rather than moving and leaving a blank).
- Span mismatch on swap shows a clear error message with instructions.

### Tests
- Added `test_swap_plots_success` and `test_swap_plots_span_mismatch` to `test_grid_operations.py`.

---

## [0.3.0]

### Added
- **Plot Settings dialog** (right-click any tile → `Plot Settings...`): configure starting position and row/column span per plot.
- **Tile context menu**: `Plot Settings...` and `Clear Plot` (with confirmation).
- **Remove rows/columns** (`Grid → - Row...` / `Grid → - Col...`): removes only if the row/column is empty.
- `move_plot()` method on `GridBoard` supporting multi-cell spanning and automatic grid expansion.

### Tests
- `test_grid_operations.py` — 11 tests covering add/remove, empty checks, tile position, and spanning.

---

## [0.2.1]

### Added
- **Automatic aggregation**: When a plot contains duplicate (x, hue) pairs, y-values are averaged before plotting. Produces clean single-line plots instead of overlapping points.

### Tests
- `test_aggregation.py` — 3 tests for mean calculation, no-duplicate pass-through, and all-duplicate case.

---

## [0.2.0]

### Added
- **Group faceting**: Multi-select group columns in the Create Plot dialog; the app creates one plot per unique combination (Cartesian product, capped at 50 combinations). Each plot title shows its filter values.
- **Shared axes**: All plots generated from a group share the same x/y axis limits for easy comparison.
- **UI cleanup**: Removed navigation toolbar and header text from each tile; minimized margins to maximize plot space; titles rendered inside Matplotlib canvas.

### Tests
- `test_integration.py` — 6 integration tests covering no-group, single-group, two-group, limit exceeded, and shared-limits cases.
