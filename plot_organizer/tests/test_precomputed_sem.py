"""Tests for pre-computed SEM (Standard Error of the Mean) functionality."""

import pandas as pd
import numpy as np
from PySide6.QtWidgets import QApplication
from plot_organizer.ui.grid_board import PlotTile
from plot_organizer.services.plot_service import shared_limits_with_sem


def test_precomputed_sem_single_row_per_x():
    """Test pre-computed SEM with one row per x-value (ideal case)."""
    data = {
        'x': [1, 2, 3],
        'y': [10, 20, 30],
        'sem': [1.0, 2.0, 3.0]
    }
    df = pd.DataFrame(data)
    
    app = QApplication.instance() or QApplication([])
    tile = PlotTile()
    tile.set_plot(df, x='x', y='y', sem_column='sem', sem_precomputed=True)
    
    # Verify pre-computed flag is set
    assert tile._sem_precomputed == True
    assert tile._sem_column == 'sem'
    
    # Verify plot was created
    assert len(tile.figure.axes) > 0
    ax = tile.figure.axes[0]
    
    # Should have a line
    lines = ax.get_lines()
    assert len(lines) >= 1
    
    # Should have filled region for SEM
    collections = ax.collections
    assert len(collections) > 0


def test_precomputed_sem_duplicate_x_values():
    """Test pre-computed SEM with duplicate x-values (should average)."""
    data = {
        'x': [1, 1, 2, 2, 3, 3],
        'y': [10, 12, 20, 22, 30, 32],
        'sem': [1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
    }
    df = pd.DataFrame(data)
    
    app = QApplication.instance() or QApplication([])
    tile = PlotTile()
    
    # This should trigger averaging and a warning
    tile.set_plot(df, x='x', y='y', sem_column='sem', sem_precomputed=True)
    
    # Verify plot was created
    assert len(tile.figure.axes) > 0
    
    # Get the plotted data
    ax = tile.figure.axes[0]
    lines = ax.get_lines()
    assert len(lines) >= 1
    
    # Verify data was aggregated (should have 3 x-values)
    x_data = lines[0].get_xdata()
    assert len(x_data) == 3


def test_precomputed_sem_with_hue():
    """Test pre-computed SEM with hue grouping."""
    data = {
        'x': [1, 2, 3] * 2,
        'y': [10, 20, 30, 15, 25, 35],
        'sem': [1.0, 2.0, 3.0, 1.5, 2.5, 3.5],
        'condition': ['A'] * 3 + ['B'] * 3
    }
    df = pd.DataFrame(data)
    
    app = QApplication.instance() or QApplication([])
    tile = PlotTile()
    tile.set_plot(df, x='x', y='y', hue='condition', sem_column='sem', sem_precomputed=True)
    
    # Verify plot was created with hue
    ax = tile.figure.axes[0]
    lines = ax.get_lines()
    assert len(lines) == 2  # Two lines (one per hue value)
    
    # Should have legend
    legend = ax.get_legend()
    assert legend is not None
    
    # Should have filled regions for both hue categories
    collections = ax.collections
    assert len(collections) >= 2


def test_precomputed_sem_vs_computed_sem():
    """Test that pre-computed and computed modes are different."""
    # Create data where computed SEM would differ from pre-computed
    data = {
        'x': [1, 1, 2, 2],
        'y': [10, 20, 30, 40],
        'subject': ['s1', 's2', 's1', 's2'],
        'sem_precomp': [2.0, 2.0, 3.0, 3.0]
    }
    df = pd.DataFrame(data)
    
    app = QApplication.instance() or QApplication([])
    
    # Computed SEM mode
    tile_computed = PlotTile()
    tile_computed.set_plot(df, x='x', y='y', sem_column='subject', sem_precomputed=False)
    
    # Pre-computed SEM mode
    tile_precomp = PlotTile()
    tile_precomp.set_plot(df, x='x', y='y', sem_column='sem_precomp', sem_precomputed=True)
    
    # Both should create plots
    assert len(tile_computed.figure.axes) > 0
    assert len(tile_precomp.figure.axes) > 0
    
    # Flags should be different
    assert tile_computed._sem_precomputed == False
    assert tile_precomp._sem_precomputed == True


def test_precomputed_sem_clear_plot():
    """Test that clearing a plot resets pre-computed flag."""
    data = {
        'x': [1, 2, 3],
        'y': [10, 20, 30],
        'sem': [1.0, 2.0, 3.0]
    }
    df = pd.DataFrame(data)
    
    app = QApplication.instance() or QApplication([])
    tile = PlotTile()
    tile.set_plot(df, x='x', y='y', sem_column='sem', sem_precomputed=True)
    
    assert tile._sem_precomputed == True
    
    # Clear the plot
    tile.clear_plot()
    
    # Flag should be reset
    assert tile._sem_precomputed == False


def test_precomputed_sem_shared_limits():
    """Test shared limits calculation with pre-computed SEM."""
    data = {
        'x': [1, 2, 3] * 2,
        'y': [10, 20, 30, 15, 25, 35],
        'sem': [2.0, 3.0, 4.0, 2.5, 3.5, 4.5],
        'group': ['A'] * 3 + ['B'] * 3
    }
    df = pd.DataFrame(data)
    
    filter_queries = [{'group': 'A'}, {'group': 'B'}]
    
    # Compute shared limits with pre-computed SEM
    xlim, ylim = shared_limits_with_sem(
        df, filter_queries, 'x', 'y', 'sem', None, sem_precomputed=True
    )
    
    # Verify limits were computed
    assert xlim[0] < xlim[1]
    assert ylim[0] < ylim[1]
    
    # Y-limits should account for SEM (mean ± sem)
    # Group A: y=10±2, 20±3, 30±4 → min~8, max~34
    # Group B: y=15±2.5, 25±3.5, 35±4.5 → min~12.5, max~39.5
    # Overall: min~8, max~39.5
    assert ylim[0] <= 8.0
    assert ylim[1] >= 39.0


def test_precomputed_sem_with_nan_values():
    """Test pre-computed SEM with NaN SEM values."""
    data = {
        'x': [1, 2, 3],
        'y': [10, 20, 30],
        'sem': [1.0, np.nan, 3.0]
    }
    df = pd.DataFrame(data)
    
    app = QApplication.instance() or QApplication([])
    tile = PlotTile()
    
    # Should handle NaN SEM gracefully
    tile.set_plot(df, x='x', y='y', sem_column='sem', sem_precomputed=True)
    
    # Verify plot was created
    assert len(tile.figure.axes) > 0


def test_precomputed_sem_zero_values():
    """Test pre-computed SEM with zero SEM values."""
    data = {
        'x': [1, 2, 3],
        'y': [10, 20, 30],
        'sem': [0.0, 0.0, 0.0]
    }
    df = pd.DataFrame(data)
    
    app = QApplication.instance() or QApplication([])
    tile = PlotTile()
    tile.set_plot(df, x='x', y='y', sem_column='sem', sem_precomputed=True)
    
    # Verify plot was created
    assert len(tile.figure.axes) > 0
    
    # Should still create filled region (even if zero)
    ax = tile.figure.axes[0]
    collections = ax.collections
    assert len(collections) > 0


def test_backward_compatibility_default_computed():
    """Test that default behavior is computed SEM (not pre-computed)."""
    data = {
        'x': [1, 1, 2, 2],
        'y': [10, 20, 30, 40],
        'subject': ['s1', 's2', 's1', 's2']
    }
    df = pd.DataFrame(data)
    
    app = QApplication.instance() or QApplication([])
    tile = PlotTile()
    
    # Don't specify sem_precomputed (should default to False)
    tile.set_plot(df, x='x', y='y', sem_column='subject')
    
    # Should use computed mode
    assert tile._sem_precomputed == False
    
    # Verify plot was created
    assert len(tile.figure.axes) > 0


def test_precomputed_sem_checkbox_state():
    """Test that checkbox state is properly captured in dialog."""
    from plot_organizer.ui.dialogs import QuickPlotDialog
    
    app = QApplication.instance() or QApplication([])
    dialog = QuickPlotDialog(
        ds_to_columns={'test': ['x', 'y', 'sem']},
        ds_names={'test': 'Test Data'}
    )
    
    # Initially unchecked
    assert dialog.precomputed_sem_check.isChecked() == False
    
    # Check it
    dialog.precomputed_sem_check.setChecked(True)
    assert dialog.precomputed_sem_check.isChecked() == True
    
    # Uncheck it
    dialog.precomputed_sem_check.setChecked(False)
    assert dialog.precomputed_sem_check.isChecked() == False


def test_precomputed_sem_info_label_updates():
    """Test that info label updates when checkbox state changes."""
    from plot_organizer.ui.dialogs import QuickPlotDialog
    
    app = QApplication.instance() or QApplication([])
    dialog = QuickPlotDialog(
        ds_to_columns={'test': ['x', 'y', 'sem']},
        ds_names={'test': 'Test Data'}
    )
    
    # Initially shows computed mode text
    initial_text = dialog.sem_info.text()
    assert "computes" in initial_text.lower() or "averaging" in initial_text.lower()
    
    # Check the box
    dialog.precomputed_sem_check.setChecked(True)
    dialog._update_sem_info()
    
    # Should show pre-computed mode text
    precomp_text = dialog.sem_info.text()
    assert "pre-computed" in precomp_text.lower()
    
    # Uncheck the box
    dialog.precomputed_sem_check.setChecked(False)
    dialog._update_sem_info()
    
    # Should return to computed mode text
    computed_text = dialog.sem_info.text()
    assert "computes" in computed_text.lower() or "averaging" in computed_text.lower()

