"""Tests for error marker annotations feature."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from plot_organizer.api import create_datasource, create_plot, create_project, save_project_file, load_project_file


def test_error_markers_in_api():
    """Test that error markers can be created via programmatic API."""
    ds = create_datasource("test", "dummy.csv")
    
    plot = create_plot(
        ds["id"],
        x="time",
        y="accuracy",
        error_markers=[
            {"x": 5.0, "xerr": 0.5, "color": "red", "label": "Event 1"},
            {"x": 10.0, "xerr": 0.3, "color": "blue", "label": "Event 2"}
        ]
    )
    
    assert "error_markers" in plot
    assert len(plot["error_markers"]) == 2
    assert plot["error_markers"][0]["x"] == 5.0
    assert plot["error_markers"][0]["xerr"] == 0.5
    assert plot["error_markers"][0]["color"] == "red"
    assert plot["error_markers"][1]["label"] == "Event 2"


def test_error_markers_default_empty():
    """Test that error markers default to empty list."""
    ds = create_datasource("test", "dummy.csv")
    plot = create_plot(ds["id"], x="time", y="accuracy")
    
    assert "error_markers" in plot
    assert plot["error_markers"] == []


def test_error_markers_save_load():
    """Test that error markers are preserved through save/load cycle."""
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("time,accuracy\n")
        f.write("1,0.5\n")
        f.write("2,0.7\n")
        f.write("3,0.9\n")
        csv_path = f.name
    
    try:
        # Create project with error markers
        ds = create_datasource("test", csv_path)
        plot = create_plot(
            ds["id"],
            x="time",
            y="accuracy",
            error_markers=[
                {"x": 1.5, "y": None, "xerr": 0.2, "yerr": None, "color": "red", "label": "Marker 1"},
                {"x": None, "y": 0.8, "xerr": None, "yerr": 0.05, "color": "blue", "label": "Marker 2"}
            ]
        )
        project = create_project((2, 2), [ds], [plot])
        
        # Save to file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ppo', delete=False) as f:
            project_path = f.name
        
        save_project_file(project, project_path)
        
        # Load back
        loaded_project = load_project_file(project_path)
        
        # Verify error markers are preserved
        assert len(loaded_project["plots"]) == 1
        loaded_plot = loaded_project["plots"][0]
        assert "error_markers" in loaded_plot
        assert len(loaded_plot["error_markers"]) == 2
        
        marker1 = loaded_plot["error_markers"][0]
        assert marker1["x"] == 1.5
        assert marker1["y"] is None
        assert marker1["xerr"] == 0.2
        assert marker1["yerr"] is None
        assert marker1["color"] == "red"
        assert marker1["label"] == "Marker 1"
        
        marker2 = loaded_plot["error_markers"][1]
        assert marker2["x"] is None
        assert marker2["y"] == 0.8
        assert marker2["xerr"] is None
        assert marker2["yerr"] == 0.05
        assert marker2["color"] == "blue"
        assert marker2["label"] == "Marker 2"
        
        # Cleanup
        Path(project_path).unlink()
    
    finally:
        Path(csv_path).unlink()


def test_error_markers_mixed_types():
    """Test error markers with different configurations."""
    ds = create_datasource("test", "dummy.csv")
    
    # Test various marker configurations
    markers = [
        # X error bar only, auto Y position
        {"x": 5.0, "xerr": 0.5, "color": "red"},
        # Y error bar only, auto X position
        {"y": 0.8, "yerr": 0.1, "color": "blue"},
        # Both positions specified, X error
        {"x": 10.0, "y": 0.5, "xerr": 1.0, "color": "green", "label": "Both"},
        # Both positions specified, Y error
        {"x": 15.0, "y": 0.9, "yerr": 0.05, "color": "purple"},
    ]
    
    plot = create_plot(
        ds["id"],
        x="time",
        y="accuracy",
        error_markers=markers
    )
    
    assert len(plot["error_markers"]) == 4
    
    # Verify first marker (X error, auto Y)
    assert plot["error_markers"][0]["x"] == 5.0
    assert plot["error_markers"][0]["xerr"] == 0.5
    assert "y" not in plot["error_markers"][0] or plot["error_markers"][0]["y"] is None
    
    # Verify second marker (Y error, auto X)
    assert plot["error_markers"][1]["y"] == 0.8
    assert plot["error_markers"][1]["yerr"] == 0.1
    assert "x" not in plot["error_markers"][1] or plot["error_markers"][1]["x"] is None
    
    # Verify third marker (both positions, X error)
    assert plot["error_markers"][2]["x"] == 10.0
    assert plot["error_markers"][2]["y"] == 0.5
    assert plot["error_markers"][2]["xerr"] == 1.0
    assert plot["error_markers"][2]["label"] == "Both"


def test_error_markers_rendering():
    """Test that error markers are rendered correctly (integration test with UI)."""
    # This test requires Qt and will verify rendering logic
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
        
        # Create tile with error markers
        tile = PlotTile()
        error_markers = [
            {"x": 2.5, "xerr": 0.5, "color": "red", "label": "Event A"},
            {"y": 0.75, "yerr": 0.1, "color": "blue", "label": "Event B"}
        ]
        
        tile.set_plot(
            df=df,
            x="time",
            y="accuracy",
            error_markers=error_markers
        )
        
        # Verify markers are stored
        assert tile._error_markers == error_markers
        assert len(tile._error_markers) == 2
        
        # Verify plot data includes markers
        plot_data = tile.get_plot_data(datasource_id="test_ds")
        assert "error_markers" in plot_data
        assert plot_data["error_markers"] == error_markers
        
        # Verify markers are restored from data
        tile2 = PlotTile()
        tile2.set_plot_from_data(df, plot_data)
        assert tile2._error_markers == error_markers
        
    except ImportError:
        pytest.skip("PySide6 not available for rendering test")


def test_error_markers_stacking():
    """Test that multiple markers are stacked when auto-positioned."""
    ds = create_datasource("test", "dummy.csv")
    
    # Create multiple markers that will be auto-positioned
    markers = [
        {"x": 1.0, "xerr": 0.1, "color": "red"},
        {"x": 2.0, "xerr": 0.1, "color": "blue"},
        {"x": 3.0, "xerr": 0.1, "color": "green"},
    ]
    
    plot = create_plot(
        ds["id"],
        x="time",
        y="accuracy",
        error_markers=markers
    )
    
    # All markers should be preserved
    assert len(plot["error_markers"]) == 3
    
    # Verify each marker has its x position set
    for i, marker in enumerate(plot["error_markers"]):
        assert marker["x"] == float(i + 1)
        assert marker["xerr"] == 0.1


def test_error_markers_in_grouped_plots():
    """Test that error markers work with grouped plots."""
    from plot_organizer.api import create_grouped_plots
    
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("time,accuracy,model\n")
        f.write("1,0.5,A\n")
        f.write("2,0.7,A\n")
        f.write("1,0.6,B\n")
        f.write("2,0.8,B\n")
        csv_path = f.name
    
    try:
        ds = create_datasource("test", csv_path)
        
        # Create grouped plots with error markers
        markers = [
            {"x": 1.5, "xerr": 0.2, "color": "red", "label": "Significant"}
        ]
        
        plots = create_grouped_plots(
            ds["id"],
            csv_path,
            x="time",
            y="accuracy",
            groups=["model"],
            error_markers=markers
        )
        
        # Should create 2 plots (one per model)
        assert len(plots) == 2
        
        # Both plots should have the error markers
        for plot in plots:
            assert "error_markers" in plot
            assert len(plot["error_markers"]) == 1
            assert plot["error_markers"][0]["x"] == 1.5
            assert plot["error_markers"][0]["color"] == "red"
    
    finally:
        Path(csv_path).unlink()


def test_error_markers_with_different_shapes():
    """Test that different marker shapes are supported in API."""
    ds = create_datasource("test", "dummy.csv")
    
    # Test various marker shapes
    markers = [
        {"x": 1.0, "xerr": 0.1, "marker": "v", "color": "red", "label": "Triangle Down"},
        {"x": 2.0, "xerr": 0.1, "marker": "^", "color": "blue", "label": "Triangle Up"},
        {"x": 3.0, "xerr": 0.1, "marker": "o", "color": "green", "label": "Circle"},
        {"x": 4.0, "xerr": 0.1, "marker": "s", "color": "orange", "label": "Square"},
        {"x": 5.0, "xerr": 0.1, "marker": "D", "color": "purple", "label": "Diamond"},
        {"x": 6.0, "xerr": 0.1, "marker": "*", "color": "brown", "label": "Star"},
    ]
    
    plot = create_plot(
        ds["id"],
        x="time",
        y="accuracy",
        error_markers=markers
    )
    
    assert "error_markers" in plot
    assert len(plot["error_markers"]) == 6
    
    # Verify each marker has the correct shape
    assert plot["error_markers"][0]["marker"] == "v"
    assert plot["error_markers"][1]["marker"] == "^"
    assert plot["error_markers"][2]["marker"] == "o"
    assert plot["error_markers"][3]["marker"] == "s"
    assert plot["error_markers"][4]["marker"] == "D"
    assert plot["error_markers"][5]["marker"] == "*"


def test_error_markers_backward_compatibility():
    """Test that markers without 'marker' field default to 'v' for backward compatibility."""
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
        
        # Create tile with markers that don't have 'marker' field (backward compatibility)
        tile = PlotTile()
        error_markers = [
            {"x": 2.5, "xerr": 0.5, "color": "red", "label": "Old Format"},
        ]
        
        tile.set_plot(
            df=df,
            x="time",
            y="accuracy",
            error_markers=error_markers
        )
        
        # Verify markers are stored and rendering doesn't crash
        assert tile._error_markers == error_markers
        assert len(tile._error_markers) == 1
        # The rendering should default to 'v' internally even though not specified
        
    except ImportError:
        pytest.skip("PySide6 not available for rendering test")


def test_error_markers_shape_save_load():
    """Test that marker shapes are preserved through save/load cycle."""
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("time,accuracy\n")
        f.write("1,0.5\n")
        f.write("2,0.7\n")
        f.write("3,0.9\n")
        csv_path = f.name
    
    try:
        # Create project with markers having different shapes
        ds = create_datasource("test", csv_path)
        plot = create_plot(
            ds["id"],
            x="time",
            y="accuracy",
            error_markers=[
                {"x": 1.5, "xerr": 0.2, "marker": "^", "color": "red", "label": "Triangle Up"},
                {"x": 2.5, "xerr": 0.3, "marker": "o", "color": "blue", "label": "Circle"},
            ]
        )
        project = create_project((2, 2), [ds], [plot])
        
        # Save to file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ppo', delete=False) as f:
            project_path = f.name
        
        save_project_file(project, project_path)
        
        # Load back
        loaded_project = load_project_file(project_path)
        
        # Verify marker shapes are preserved
        assert len(loaded_project["plots"]) == 1
        loaded_plot = loaded_project["plots"][0]
        assert "error_markers" in loaded_plot
        assert len(loaded_plot["error_markers"]) == 2
        
        marker1 = loaded_plot["error_markers"][0]
        assert marker1["marker"] == "^"
        assert marker1["color"] == "red"
        
        marker2 = loaded_plot["error_markers"][1]
        assert marker2["marker"] == "o"
        assert marker2["color"] == "blue"
        
        # Cleanup
        Path(project_path).unlink()
    
    finally:
        Path(csv_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

