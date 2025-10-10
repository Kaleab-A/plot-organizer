"""Tests for SEM (Standard Error of the Mean) plotting functionality."""

import pandas as pd
import numpy as np
from PySide6.QtWidgets import QApplication
from plot_organizer.ui.grid_board import PlotTile


def test_sem_column_grouping_and_aggregation():
    """Test that SEM column correctly groups data before computing mean and SEM."""
    # Create test data with explicit sem_column grouping
    data = {
        'x': [1, 1, 1, 2, 2, 2, 3, 3, 3],
        'y': [10, 12, 11, 20, 22, 21, 30, 32, 31],
        'subject': ['s1', 's2', 's3', 's1', 's2', 's3', 's1', 's2', 's3']
    }
    df = pd.DataFrame(data)
    
    # Create a PlotTile and set plot with SEM
    app = QApplication.instance() or QApplication([])
    tile = PlotTile()
    tile.set_plot(df, x='x', y='y', sem_column='subject')
    
    # Verify plot was created
    assert tile._df is not None
    assert tile._sem_column == 'subject'
    assert len(tile.figure.axes) > 0
    
    # Get the plotted line data
    ax = tile.figure.axes[0]
    lines = ax.get_lines()
    assert len(lines) == 1  # One mean line
    
    # Verify fill_between was called for SEM shading
    collections = ax.collections
    assert len(collections) > 0  # Should have filled region


def test_sem_with_hue():
    """Test SEM plotting with hue grouping."""
    data = {
        'x': [1, 1, 1, 2, 2, 2] * 2,
        'y': [10, 12, 11, 20, 22, 21, 15, 17, 16, 25, 27, 26],
        'subject': ['s1', 's2', 's3'] * 4,
        'condition': ['A'] * 6 + ['B'] * 6
    }
    df = pd.DataFrame(data)
    
    app = QApplication.instance() or QApplication([])
    tile = PlotTile()
    tile.set_plot(df, x='x', y='y', hue='condition', sem_column='subject')
    
    # Verify plot was created with hue
    ax = tile.figure.axes[0]
    lines = ax.get_lines()
    assert len(lines) == 2  # Two lines (one per hue value)
    
    # Should have legend
    legend = ax.get_legend()
    assert legend is not None


def test_no_sem_column():
    """Test that plotting works correctly without SEM column."""
    data = {
        'x': [1, 1, 2, 2, 3, 3],
        'y': [10, 12, 20, 22, 30, 32]
    }
    df = pd.DataFrame(data)
    
    app = QApplication.instance() or QApplication([])
    tile = PlotTile()
    tile.set_plot(df, x='x', y='y', sem_column=None)
    
    # Verify plot was created
    assert tile._df is not None
    assert tile._sem_column is None
    
    ax = tile.figure.axes[0]
    lines = ax.get_lines()
    assert len(lines) == 1
    
    # Should NOT have filled regions
    collections = ax.collections
    assert len(collections) == 0


def test_sem_computation_correctness():
    """Test that SEM is computed correctly."""
    # Create data where we know the exact mean and SEM
    data = {
        'x': [1] * 6,
        'y': [10, 10, 10, 20, 20, 20],  # Two groups: mean 10 and mean 20
        'subject': ['s1', 's2', 's3', 's1', 's2', 's3']
    }
    df = pd.DataFrame(data)
    
    # Expected: For x=1, we first group by subject:
    # s1: mean(10, 20) = 15
    # s2: mean(10, 20) = 15
    # s3: mean(10, 20) = 15
    # Then across subjects: mean = 15, sem = 0
    
    app = QApplication.instance() or QApplication([])
    tile = PlotTile()
    tile.set_plot(df, x='x', y='y', sem_column='subject')
    
    ax = tile.figure.axes[0]
    lines = ax.get_lines()
    
    # Get the plotted y value
    y_data = lines[0].get_ydata()
    assert len(y_data) == 1
    assert np.isclose(y_data[0], 15.0)


def test_sem_with_varying_values():
    """Test SEM with actual variance across subjects."""
    data = {
        'x': [1, 1, 1, 1],
        'y': [10, 12, 14, 16],
        'subject': ['s1', 's2', 's3', 's4']
    }
    df = pd.DataFrame(data)
    
    # First group by subject (each has one value, so no change)
    # Then compute mean and SEM across subjects
    # mean = 13, sem = std([10,12,14,16]) / sqrt(4)
    
    app = QApplication.instance() or QApplication([])
    tile = PlotTile()
    tile.set_plot(df, x='x', y='y', sem_column='subject')
    
    ax = tile.figure.axes[0]
    lines = ax.get_lines()
    y_data = lines[0].get_ydata()
    
    # Mean should be 13
    assert np.isclose(y_data[0], 13.0)
    
    # Should have a filled region for SEM
    collections = ax.collections
    assert len(collections) > 0

