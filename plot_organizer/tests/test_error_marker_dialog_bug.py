"""Test for the error marker dialog bug fix.

This test verifies that opening the "Manage Error Markers" dialog and clicking
OK without adding markers does not create duplicate axes or cause the plot to
shrink/move.
"""

from __future__ import annotations

import pandas as pd
import pytest


def test_marker_dialog_doesnt_duplicate_axes():
    """Test that opening marker dialog multiple times doesn't create duplicate axes."""
    try:
        from PySide6.QtWidgets import QApplication
        import sys
        
        # Create QApplication if not exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from plot_organizer.ui.grid_board import PlotTile
        
        # Create test data
        df = pd.DataFrame({
            "time": [1, 2, 3, 4, 5],
            "accuracy": [0.5, 0.6, 0.7, 0.8, 0.9]
        })
        
        # Create tile with a plot
        tile = PlotTile()
        tile.set_plot(
            df=df,
            x="time",
            y="accuracy",
            title="Test Plot"
        )
        
        # Initially should have exactly 1 axis
        assert len(tile.figure.axes) == 1
        initial_title = tile.figure.axes[0].get_title()
        assert initial_title == "Test Plot"
        
        # Simulate calling set_plot again (like the dialog does)
        # This would create duplicate axes before the fix
        tile.set_plot(
            df=df,
            x="time",
            y="accuracy",
            title="Test Plot"
        )
        
        # Should still have exactly 1 axis (not 2)
        assert len(tile.figure.axes) == 1, "Multiple axes created - bug not fixed!"
        
        # Title should be preserved
        assert tile.figure.axes[0].get_title() == "Test Plot"
        
        # Call set_plot multiple more times (simulating multiple dialog opens)
        for _ in range(5):
            tile.set_plot(
                df=df,
                x="time",
                y="accuracy",
                title="Test Plot"
            )
        
        # Still should have exactly 1 axis
        assert len(tile.figure.axes) == 1, f"Expected 1 axis, got {len(tile.figure.axes)}"
        assert tile.figure.axes[0].get_title() == "Test Plot"
        
    except ImportError:
        pytest.skip("PySide6 not available for UI test")


def test_marker_dialog_preserves_title():
    """Test that the marker dialog preserves plot title."""
    try:
        from PySide6.QtWidgets import QApplication
        import sys
        
        # Create QApplication if not exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from plot_organizer.ui.grid_board import PlotTile
        
        # Create test data
        df = pd.DataFrame({
            "time": [1, 2, 3, 4, 5],
            "accuracy": [0.5, 0.6, 0.7, 0.8, 0.9]
        })
        
        # Create tile with a plot with title
        tile = PlotTile()
        tile.set_plot(
            df=df,
            x="time",
            y="accuracy",
            title="Important Results"
        )
        
        # Get initial title
        initial_title = tile.figure.axes[0].get_title()
        assert initial_title == "Important Results"
        
        # Simulate the _open_markers_dialog re-render path
        # (extract title and pass it back)
        title = None
        if tile.figure.axes:
            title = tile.figure.axes[0].get_title() or None
        
        tile.set_plot(
            df=df,
            x="time",
            y="accuracy",
            title=title  # Pass the extracted title
        )
        
        # Title should still be there
        assert tile.figure.axes[0].get_title() == "Important Results"
        
    except ImportError:
        pytest.skip("PySide6 not available for UI test")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

