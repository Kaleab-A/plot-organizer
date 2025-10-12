"""Tests for plot style (line, marker, both) feature."""
from __future__ import annotations

import pandas as pd
import pytest
import sys
from PySide6.QtWidgets import QApplication

# Ensure QApplication exists for Qt widgets
if not QApplication.instance():
    app = QApplication(sys.argv)

from plot_organizer.ui.grid_board import PlotTile


def test_default_style_line_only():
    """Test that default style is line only."""
    tile = PlotTile()
    df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
    
    tile.set_plot(df=df, x='x', y='y')
    
    assert tile._style_line is True
    assert tile._style_marker is False


def test_style_line_only():
    """Test plotting with line only."""
    tile = PlotTile()
    df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
    
    tile.set_plot(df=df, x='x', y='y', style_line=True, style_marker=False)
    
    assert tile._style_line is True
    assert tile._style_marker is False
    assert tile._get_plot_format() == '-'


def test_style_marker_only():
    """Test plotting with markers only."""
    tile = PlotTile()
    df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
    
    tile.set_plot(df=df, x='x', y='y', style_line=False, style_marker=True)
    
    assert tile._style_line is False
    assert tile._style_marker is True
    assert tile._get_plot_format() == 'o'


def test_style_line_and_marker():
    """Test plotting with both line and markers."""
    tile = PlotTile()
    df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
    
    tile.set_plot(df=df, x='x', y='y', style_line=True, style_marker=True)
    
    assert tile._style_line is True
    assert tile._style_marker is True
    assert tile._get_plot_format() == '-o'


def test_style_with_hue():
    """Test that style settings work with hue."""
    tile = PlotTile()
    df = pd.DataFrame({
        'x': [1, 2, 3, 1, 2, 3],
        'y': [4, 5, 6, 7, 8, 9],
        'hue': ['A', 'A', 'A', 'B', 'B', 'B']
    })
    
    tile.set_plot(df=df, x='x', y='y', hue='hue', style_line=True, style_marker=True)
    
    assert tile._style_line is True
    assert tile._style_marker is True
    # Should have 2 lines plotted (one for each hue value)
    ax = tile.figure.gca()
    assert len(ax.lines) == 2


def test_style_with_sem():
    """Test that style settings work with SEM."""
    tile = PlotTile()
    df = pd.DataFrame({
        'x': [1, 2, 3, 1, 2, 3],
        'y': [4, 5, 6, 4.5, 5.5, 6.5],
        'sem_col': ['A', 'A', 'A', 'B', 'B', 'B']
    })
    
    tile.set_plot(
        df=df,
        x='x',
        y='y',
        sem_column='sem_col',
        style_line=False,
        style_marker=True
    )
    
    assert tile._style_line is False
    assert tile._style_marker is True
    # Should have plot with markers
    ax = tile.figure.gca()
    assert len(ax.lines) > 0


def test_clear_plot_resets_style():
    """Test that clearing a plot resets style to defaults."""
    tile = PlotTile()
    df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
    
    tile.set_plot(df=df, x='x', y='y', style_line=False, style_marker=True)
    assert tile._style_line is False
    assert tile._style_marker is True
    
    tile.clear_plot()
    
    assert tile._style_line is True
    assert tile._style_marker is False


def test_style_format_string():
    """Test the _get_plot_format helper method."""
    tile = PlotTile()
    
    # Line only
    tile._style_line = True
    tile._style_marker = False
    assert tile._get_plot_format() == '-'
    
    # Marker only
    tile._style_line = False
    tile._style_marker = True
    assert tile._get_plot_format() == 'o'
    
    # Both
    tile._style_line = True
    tile._style_marker = True
    assert tile._get_plot_format() == '-o'
    
    # Neither (defaults to line)
    tile._style_line = False
    tile._style_marker = False
    assert tile._get_plot_format() == '-'


def test_style_with_precomputed_sem():
    """Test that style settings work with pre-computed SEM."""
    tile = PlotTile()
    df = pd.DataFrame({
        'x': [1, 2, 3],
        'y': [4, 5, 6],
        'sem': [0.1, 0.2, 0.15]
    })
    
    tile.set_plot(
        df=df,
        x='x',
        y='y',
        sem_column='sem',
        sem_precomputed=True,
        style_line=True,
        style_marker=True
    )
    
    assert tile._style_line is True
    assert tile._style_marker is True
    # Should have plot with line and markers
    ax = tile.figure.gca()
    assert len(ax.lines) > 0

