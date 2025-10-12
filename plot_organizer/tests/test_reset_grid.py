"""Tests for grid reset functionality."""
from __future__ import annotations

import pandas as pd
import pytest
import sys
from PySide6.QtWidgets import QApplication

# Ensure QApplication exists for Qt widgets
if not QApplication.instance():
    app = QApplication(sys.argv)

from plot_organizer.ui.grid_board import GridBoard


def test_reset_to_size_basic():
    """Test resetting grid to a specific size."""
    board = GridBoard(rows=4, cols=5)
    assert board._rows == 4
    assert board._cols == 5
    
    board.reset_to_size(2, 3)
    
    assert board._rows == 2
    assert board._cols == 3
    
    # Check that all tiles exist
    for r in range(2):
        for c in range(3):
            tile = board.tile_at(r, c)
            assert tile is not None
            assert tile.is_empty()


def test_reset_clears_plots():
    """Test that reset clears all plots."""
    board = GridBoard(rows=2, cols=2)
    df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
    
    # Add a plot
    tile = board.tile_at(0, 0)
    tile.set_plot(df=df, x='x', y='y')
    assert not tile.is_empty()
    
    # Reset grid
    board.reset_to_size(2, 2)
    
    # Check that the tile at (0, 0) is now empty (new tile created)
    new_tile = board.tile_at(0, 0)
    assert new_tile is not None
    assert new_tile.is_empty()


def test_reset_changes_size():
    """Test that reset can change grid dimensions."""
    board = GridBoard(rows=3, cols=4)
    
    # Increase size
    board.reset_to_size(5, 6)
    assert board._rows == 5
    assert board._cols == 6
    
    # Verify all tiles exist
    for r in range(5):
        for c in range(6):
            assert board.tile_at(r, c) is not None
    
    # Decrease size
    board.reset_to_size(1, 1)
    assert board._rows == 1
    assert board._cols == 1
    
    # Only (0, 0) should exist
    assert board.tile_at(0, 0) is not None


def test_reset_to_default_size():
    """Test resetting to default size (2x3)."""
    board = GridBoard(rows=10, cols=10)
    df = pd.DataFrame({'x': [1, 2], 'y': [3, 4]})
    
    # Fill some plots
    for r in range(3):
        for c in range(3):
            tile = board.tile_at(r, c)
            tile.set_plot(df=df, x='x', y='y', title=f"Plot {r},{c}")
    
    # Reset to default
    board.reset_to_size(2, 3)
    
    assert board._rows == 2
    assert board._cols == 3
    
    # All tiles should be empty and new
    for r in range(2):
        for c in range(3):
            tile = board.tile_at(r, c)
            assert tile is not None
            assert tile.is_empty()


def test_reset_removes_old_widgets():
    """Test that old widgets are properly removed."""
    board = GridBoard(rows=3, cols=3)
    df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
    
    # Add plots to all tiles
    original_tiles = []
    for r in range(3):
        for c in range(3):
            tile = board.tile_at(r, c)
            tile.set_plot(df=df, x='x', y='y')
            original_tiles.append(tile)
    
    # Get widget count before reset
    initial_count = board._grid.count()
    assert initial_count == 9
    
    # Reset
    board.reset_to_size(2, 2)
    
    # New widget count should be 4 (2x2)
    assert board._grid.count() == 4
    
    # All tiles should be new instances (different from original)
    for r in range(2):
        for c in range(2):
            new_tile = board.tile_at(r, c)
            assert new_tile not in original_tiles


def test_reset_with_complex_state():
    """Test reset with plots that have complex state (hue, SEM, etc.)."""
    board = GridBoard(rows=3, cols=3)
    df = pd.DataFrame({
        'x': [1, 2, 3, 1, 2, 3],
        'y': [4, 5, 6, 7, 8, 9],
        'hue': ['A', 'A', 'A', 'B', 'B', 'B'],
        'sem': [0.1, 0.2, 0.15, 0.12, 0.18, 0.14]
    })
    
    # Add a complex plot
    tile = board.tile_at(1, 1)
    tile.set_plot(
        df=df,
        x='x',
        y='y',
        hue='hue',
        sem_column='sem',
        sem_precomputed=True,
        hlines=[5.0],
        vlines=[2.0],
        style_line=True,
        style_marker=True
    )
    assert not tile.is_empty()
    
    # Reset
    board.reset_to_size(2, 2)
    
    # All tiles should be empty and have default state
    for r in range(2):
        for c in range(2):
            tile = board.tile_at(r, c)
            assert tile.is_empty()
            assert tile._style_line is True
            assert tile._style_marker is False
            assert tile._hlines == []
            assert tile._vlines == []

