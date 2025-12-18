"""Tests for flip_axes feature (Y independent, X dependent)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from plot_organizer.api import (
    create_datasource,
    create_plot,
    create_project,
    create_grouped_plots,
    save_project_file,
    load_project_file,
)
from plot_organizer.services.plot_service import shared_limits, shared_limits_with_sem


def test_flip_axes_in_api():
    """Test that flip_axes can be created via programmatic API."""
    ds = create_datasource("test", "dummy.csv")
    
    plot = create_plot(
        ds["id"],
        x="value",
        y="time",
        flip_axes=True,
    )
    
    assert "flip_axes" in plot
    assert plot["flip_axes"] is True


def test_flip_axes_default_false():
    """Test that flip_axes defaults to False."""
    ds = create_datasource("test", "dummy.csv")
    plot = create_plot(ds["id"], x="time", y="accuracy")
    
    assert "flip_axes" in plot
    assert plot["flip_axes"] is False


def test_flip_axes_save_load():
    """Test that flip_axes is preserved through save/load cycle."""
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("time,accuracy\n")
        f.write("1,0.5\n")
        f.write("2,0.7\n")
        f.write("3,0.9\n")
        csv_path = f.name
    
    try:
        # Create project with flip_axes=True
        ds = create_datasource("test", csv_path)
        plot = create_plot(
            ds["id"],
            x="accuracy",
            y="time",
            flip_axes=True,
        )
        project = create_project((2, 2), [ds], [plot])
        
        # Save to file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ppo', delete=False) as f:
            project_path = f.name
        
        save_project_file(project, project_path)
        
        # Load back
        loaded_project = load_project_file(project_path)
        
        # Verify flip_axes is preserved
        assert len(loaded_project["plots"]) == 1
        loaded_plot = loaded_project["plots"][0]
        assert "flip_axes" in loaded_plot
        assert loaded_plot["flip_axes"] is True
        
        # Cleanup
        Path(project_path).unlink()
    
    finally:
        Path(csv_path).unlink()


def test_flip_axes_rendering():
    """Test that flip_axes plots are rendered correctly (integration test with UI)."""
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
        
        # Create tile with flip_axes=True
        tile = PlotTile()
        tile.set_plot(
            df=df,
            x="accuracy",
            y="time",
            flip_axes=True,
        )
        
        # Verify flip_axes is stored
        assert tile._flip_axes is True
        
        # Verify plot data includes flip_axes
        plot_data = tile.get_plot_data(datasource_id="test_ds")
        assert "flip_axes" in plot_data
        assert plot_data["flip_axes"] is True
        
        # Verify flip_axes is restored from data
        tile2 = PlotTile()
        tile2.set_plot_from_data(df, plot_data)
        assert tile2._flip_axes is True
        
    except ImportError:
        pytest.skip("PySide6 not available for rendering test")


def test_flip_axes_with_sem():
    """Test flip_axes with SEM column."""
    try:
        from PySide6.QtWidgets import QApplication
        import sys
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from plot_organizer.ui.grid_board import PlotTile
        
        # Create test data with subject for SEM
        df = pd.DataFrame({
            "time": [1, 1, 1, 2, 2, 2, 3, 3, 3],
            "accuracy": [0.5, 0.52, 0.48, 0.6, 0.62, 0.58, 0.7, 0.72, 0.68],
            "subject": ["s1", "s2", "s3"] * 3
        })
        
        # Create tile with flip_axes=True and SEM
        tile = PlotTile()
        tile.set_plot(
            df=df,
            x="accuracy",
            y="time",
            sem_column="subject",
            flip_axes=True,
        )
        
        # Verify plot was created
        assert tile._flip_axes is True
        assert tile._sem_column == "subject"
        
        # Verify axis was rendered (check axes exist)
        ax = tile.figure.axes[0]
        assert ax.get_xlabel() == "accuracy"
        assert ax.get_ylabel() == "time"
        
    except ImportError:
        pytest.skip("PySide6 not available for rendering test")


def test_flip_axes_with_precomputed_sem():
    """Test flip_axes with pre-computed SEM values."""
    try:
        from PySide6.QtWidgets import QApplication
        import sys
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from plot_organizer.ui.grid_board import PlotTile
        
        # Create test data with pre-computed SEM
        df = pd.DataFrame({
            "time": [1, 2, 3],
            "accuracy": [0.5, 0.6, 0.7],
            "sem": [0.02, 0.03, 0.01]
        })
        
        # Create tile with flip_axes=True and pre-computed SEM
        tile = PlotTile()
        tile.set_plot(
            df=df,
            x="accuracy",
            y="time",
            sem_column="sem",
            sem_precomputed=True,
            flip_axes=True,
        )
        
        # Verify plot was created
        assert tile._flip_axes is True
        assert tile._sem_precomputed is True
        
    except ImportError:
        pytest.skip("PySide6 not available for rendering test")


def test_flip_axes_with_hue():
    """Test flip_axes with hue grouping."""
    try:
        from PySide6.QtWidgets import QApplication
        import sys
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from plot_organizer.ui.grid_board import PlotTile
        
        # Create test data with hue
        df = pd.DataFrame({
            "time": [1, 2, 3, 1, 2, 3],
            "accuracy": [0.5, 0.6, 0.7, 0.4, 0.5, 0.6],
            "model": ["A", "A", "A", "B", "B", "B"]
        })
        
        # Create tile with flip_axes=True and hue
        tile = PlotTile()
        tile.set_plot(
            df=df,
            x="accuracy",
            y="time",
            hue="model",
            flip_axes=True,
        )
        
        # Verify plot was created with legend
        ax = tile.figure.axes[0]
        legend = ax.get_legend()
        assert legend is not None
        
    except ImportError:
        pytest.skip("PySide6 not available for rendering test")


def test_shared_limits_with_flip_axes():
    """Test that shared_limits returns raw limits regardless of flip_axes.
    
    shared_limits always returns raw min/max from data:
    - xlim = (min x, max x) from raw data
    - ylim = (min y, max y) from raw data
    
    The flip_axes parameter is accepted but doesn't change the raw limits calculation.
    For aggregated limits, use shared_limits_with_sem().
    """
    df1 = pd.DataFrame({
        "time": [1, 2, 3],
        "accuracy": [0.5, 0.6, 0.7]
    })
    df2 = pd.DataFrame({
        "time": [1, 2, 3],
        "accuracy": [0.4, 0.5, 0.6]
    })
    
    # Test standard (flip_axes=False)
    xlim_std, ylim_std = shared_limits([df1, df2], "time", "accuracy", flip_axes=False)
    assert xlim_std == (1.0, 3.0)  # raw time range
    assert ylim_std == (0.4, 0.7)  # raw accuracy range
    
    # Test flipped (flip_axes=True) - should give same results (raw limits)
    xlim_flip, ylim_flip = shared_limits([df1, df2], "time", "accuracy", flip_axes=True)
    
    # Same raw limits regardless of flip_axes
    assert xlim_flip == (1.0, 3.0)  # raw time range
    assert ylim_flip == (0.4, 0.7)  # raw accuracy range


def test_shared_limits_with_sem_flip_axes():
    """Test that shared_limits_with_sem computes correct limits when flip_axes=True."""
    df = pd.DataFrame({
        "time": [1, 1, 1, 2, 2, 2],
        "accuracy": [0.5, 0.52, 0.48, 0.7, 0.72, 0.68],
        "subject": ["s1", "s2", "s3", "s1", "s2", "s3"]
    })
    
    filter_queries = [{}]  # No filtering
    
    # Test standard (flip_axes=False) with x="time", y="accuracy"
    # X is independent (time), Y is dependent (accuracy)
    xlim_std, ylim_std = shared_limits_with_sem(
        df, filter_queries, "time", "accuracy", "subject", flip_axes=False
    )
    # xlim_std = time range (independent)
    assert xlim_std[0] == 1.0
    assert xlim_std[1] == 2.0
    
    # Test flipped (flip_axes=True) with x="time", y="accuracy"
    # Now Y (accuracy) is independent, X (time) is dependent
    xlim_flip, ylim_flip = shared_limits_with_sem(
        df, filter_queries, "time", "accuracy", "subject", flip_axes=True
    )
    
    # ylim = accuracy range (independent axis - what we group by)
    # raw accuracy values: 0.48, 0.5, 0.52, 0.68, 0.7, 0.72
    assert ylim_flip[0] == 0.48  # min accuracy
    assert ylim_flip[1] == 0.72  # max accuracy
    
    # xlim = time range (dependent axis - with SEM)
    # SEM is computed on time values grouped by accuracy
    assert xlim_flip[0] <= 1.0  # min time (with SEM adjustment)
    assert xlim_flip[1] >= 2.0  # max time (with SEM adjustment)


def test_flip_axes_in_grouped_plots():
    """Test that flip_axes works with grouped plots."""
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
        
        # Create grouped plots with flip_axes=True
        plots = create_grouped_plots(
            ds["id"],
            csv_path,
            x="accuracy",
            y="time",
            groups=["model"],
            flip_axes=True,
        )
        
        # Should create 2 plots (one per model)
        assert len(plots) == 2
        
        # Both plots should have flip_axes=True
        for plot in plots:
            assert "flip_axes" in plot
            assert plot["flip_axes"] is True
    
    finally:
        Path(csv_path).unlink()


def test_flip_axes_error_markers():
    """Test error marker stacking with flip_axes."""
    try:
        from PySide6.QtWidgets import QApplication
        import sys
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from plot_organizer.ui.grid_board import PlotTile
        
        # Create test data
        df = pd.DataFrame({
            "time": [1, 2, 3, 4, 5],
            "accuracy": [0.5, 0.6, 0.7, 0.8, 0.9]
        })
        
        # Create tile with flip_axes and error markers
        tile = PlotTile()
        error_markers = [
            {"x": 0.6, "xerr": 0.05, "y": 0, "color": "red", "label": "X Error"},
            {"y": 2.5, "yerr": 0.5, "x": 0, "color": "blue", "label": "Y Error"},
        ]
        
        tile.set_plot(
            df=df,
            x="accuracy",
            y="time",
            flip_axes=True,
            error_markers=error_markers,
        )
        
        # Verify markers are stored
        assert len(tile._error_markers) == 2
        assert tile._flip_axes is True
        
    except ImportError:
        pytest.skip("PySide6 not available for rendering test")


def test_flip_axes_clear_plot():
    """Test that clear_plot resets flip_axes to False."""
    try:
        from PySide6.QtWidgets import QApplication
        import sys
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from plot_organizer.ui.grid_board import PlotTile
        
        df = pd.DataFrame({
            "time": [1, 2, 3],
            "accuracy": [0.5, 0.6, 0.7]
        })
        
        tile = PlotTile()
        tile.set_plot(
            df=df,
            x="accuracy",
            y="time",
            flip_axes=True,
        )
        
        assert tile._flip_axes is True
        
        tile.clear_plot()
        
        assert tile._flip_axes is False
        
    except ImportError:
        pytest.skip("PySide6 not available for rendering test")


def test_flip_axes_xlim_parameter():
    """Test that xlim parameter works with flip_axes."""
    ds = create_datasource("test", "dummy.csv")
    
    plot = create_plot(
        ds["id"],
        x="accuracy",
        y="time",
        flip_axes=True,
        xlim=(0.0, 1.0),
        ylim=(0, 10),
    )
    
    assert plot["flip_axes"] is True
    assert plot["xlim"] == [0.0, 1.0]
    assert plot["ylim"] == [0, 10]


def test_flip_axes_preserves_axis_labels():
    """Test that axis labels remain correct with flip_axes."""
    try:
        from PySide6.QtWidgets import QApplication
        import sys
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from plot_organizer.ui.grid_board import PlotTile
        
        df = pd.DataFrame({
            "time": [1, 2, 3],
            "accuracy": [0.5, 0.6, 0.7]
        })
        
        # With flip_axes, x column still shows on x-axis, y column on y-axis
        tile = PlotTile()
        tile.set_plot(
            df=df,
            x="accuracy",
            y="time",
            flip_axes=True,
        )
        
        ax = tile.figure.axes[0]
        assert ax.get_xlabel() == "accuracy"
        assert ax.get_ylabel() == "time"
        
    except ImportError:
        pytest.skip("PySide6 not available for rendering test")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

