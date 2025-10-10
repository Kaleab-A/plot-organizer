"""Tests for reference lines (horizontal and vertical dashed lines) feature."""

import pandas as pd
from PySide6.QtWidgets import QApplication
from plot_organizer.ui.grid_board import PlotTile


def test_horizontal_reference_lines():
    """Test that horizontal reference lines are drawn correctly."""
    data = {'x': [1, 2, 3], 'y': [10, 20, 30]}
    df = pd.DataFrame(data)
    
    app = QApplication.instance() or QApplication([])
    tile = PlotTile()
    
    # Add plot with horizontal reference lines
    tile.set_plot(df, x='x', y='y', hlines=[15.0, 25.0])
    
    # Verify reference lines were stored
    assert tile._hlines == [15.0, 25.0]
    assert tile._vlines == []
    
    # Verify plot was created
    assert len(tile.figure.axes) > 0
    ax = tile.figure.axes[0]
    
    # Check that horizontal lines were drawn
    # Note: axhline creates Line2D objects that we can check
    lines = ax.get_lines()
    # Should have 1 data line + 2 horizontal reference lines = 3 total
    assert len(lines) >= 3


def test_vertical_reference_lines():
    """Test that vertical reference lines are drawn correctly."""
    data = {'x': [1, 2, 3, 4], 'y': [10, 20, 30, 40]}
    df = pd.DataFrame(data)
    
    app = QApplication.instance() or QApplication([])
    tile = PlotTile()
    
    # Add plot with vertical reference lines
    tile.set_plot(df, x='x', y='y', vlines=[1.5, 2.5, 3.5])
    
    # Verify reference lines were stored
    assert tile._vlines == [1.5, 2.5, 3.5]
    assert tile._hlines == []
    
    # Verify plot was created
    assert len(tile.figure.axes) > 0


def test_both_reference_lines():
    """Test both horizontal and vertical reference lines together."""
    data = {'x': [1, 2, 3], 'y': [10, 20, 30]}
    df = pd.DataFrame(data)
    
    app = QApplication.instance() or QApplication([])
    tile = PlotTile()
    
    # Add plot with both types of reference lines
    tile.set_plot(df, x='x', y='y', hlines=[15.0], vlines=[2.0])
    
    # Verify both types were stored
    assert tile._hlines == [15.0]
    assert tile._vlines == [2.0]
    
    # Verify plot was created
    assert len(tile.figure.axes) > 0


def test_no_reference_lines():
    """Test that plots work without reference lines (backward compatibility)."""
    data = {'x': [1, 2, 3], 'y': [10, 20, 30]}
    df = pd.DataFrame(data)
    
    app = QApplication.instance() or QApplication([])
    tile = PlotTile()
    
    # Add plot without reference lines
    tile.set_plot(df, x='x', y='y')
    
    # Verify no reference lines
    assert tile._hlines == []
    assert tile._vlines == []
    
    # Verify plot was still created normally
    assert len(tile.figure.axes) > 0


def test_clear_plot_resets_reference_lines():
    """Test that clearing a plot also clears reference lines."""
    data = {'x': [1, 2, 3], 'y': [10, 20, 30]}
    df = pd.DataFrame(data)
    
    app = QApplication.instance() or QApplication([])
    tile = PlotTile()
    
    # Add plot with reference lines
    tile.set_plot(df, x='x', y='y', hlines=[15.0], vlines=[2.0])
    assert tile._hlines == [15.0]
    assert tile._vlines == [2.0]
    
    # Clear the plot
    tile.clear_plot()
    
    # Verify reference lines were cleared
    assert tile._hlines == []
    assert tile._vlines == []


def test_reference_lines_with_hue():
    """Test reference lines work correctly with hue grouping."""
    data = {
        'x': [1, 2, 3] * 2,
        'y': [10, 20, 30, 15, 25, 35],
        'category': ['A'] * 3 + ['B'] * 3
    }
    df = pd.DataFrame(data)
    
    app = QApplication.instance() or QApplication([])
    tile = PlotTile()
    
    # Add plot with hue and reference lines
    tile.set_plot(df, x='x', y='y', hue='category', hlines=[20.0], vlines=[2.0])
    
    # Verify reference lines were stored
    assert tile._hlines == [20.0]
    assert tile._vlines == [2.0]
    
    # Verify plot was created with hue
    assert len(tile.figure.axes) > 0
    ax = tile.figure.axes[0]
    
    # Should have a legend due to hue
    legend = ax.get_legend()
    assert legend is not None


def test_reference_lines_with_sem():
    """Test reference lines work correctly with SEM column."""
    data = {
        'x': [1, 1, 1, 2, 2, 2],
        'y': [10, 12, 14, 20, 22, 24],
        'subject': ['s1', 's2', 's3', 's1', 's2', 's3']
    }
    df = pd.DataFrame(data)
    
    app = QApplication.instance() or QApplication([])
    tile = PlotTile()
    
    # Add plot with SEM and reference lines
    tile.set_plot(df, x='x', y='y', sem_column='subject', hlines=[15.0], vlines=[1.5])
    
    # Verify reference lines were stored
    assert tile._hlines == [15.0]
    assert tile._vlines == [1.5]
    
    # Verify plot was created
    assert len(tile.figure.axes) > 0


def test_parse_numbers_helper():
    """Test the _parse_numbers helper function in QuickPlotDialog."""
    from plot_organizer.ui.dialogs import QuickPlotDialog
    
    # Create a minimal dialog instance
    app = QApplication.instance() or QApplication([])
    dialog = QuickPlotDialog(
        ds_to_columns={'test': ['x', 'y']},
        ds_names={'test': 'Test Data'}
    )
    
    # Test valid inputs
    assert dialog._parse_numbers("1, 2, 3") == [1.0, 2.0, 3.0]
    assert dialog._parse_numbers("10.5, 20.7, 30.9") == [10.5, 20.7, 30.9]
    assert dialog._parse_numbers("100") == [100.0]
    
    # Test empty/whitespace
    assert dialog._parse_numbers("") == []
    assert dialog._parse_numbers("   ") == []
    
    # Test with extra whitespace
    assert dialog._parse_numbers("  1 ,  2  , 3  ") == [1.0, 2.0, 3.0]
    
    # Test with invalid values (should skip them)
    assert dialog._parse_numbers("1, abc, 3") == [1.0, 3.0]
    assert dialog._parse_numbers("invalid") == []
    
    # Test mixed valid and invalid
    assert dialog._parse_numbers("10, , 20, xyz, 30") == [10.0, 20.0, 30.0]


def test_multiple_reference_lines():
    """Test plotting with many reference lines."""
    data = {'x': [1, 2, 3, 4, 5], 'y': [10, 20, 30, 40, 50]}
    df = pd.DataFrame(data)
    
    app = QApplication.instance() or QApplication([])
    tile = PlotTile()
    
    # Add many reference lines
    hlines = [15.0, 25.0, 35.0, 45.0]
    vlines = [1.5, 2.5, 3.5, 4.5]
    
    tile.set_plot(df, x='x', y='y', hlines=hlines, vlines=vlines)
    
    # Verify all were stored
    assert tile._hlines == hlines
    assert tile._vlines == vlines
    
    # Verify plot was created
    assert len(tile.figure.axes) > 0

