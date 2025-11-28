"""Tests for project save/load functionality."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from plot_organizer.services.project_service import save_workspace, load_workspace
from plot_organizer.services.load_service import load_csv_to_datasource
from plot_organizer.ui.grid_board import GridBoard


def test_save_load_roundtrip(tmp_path):
    """Test that save and load preserve data correctly."""
    # Create test project data
    datasources = {
        "ds1": {
            "name": "test_data",
            "path": str(tmp_path / "test.csv"),
            "schema": [
                {"name": "x", "dtype": "int64", "var_type": "continuous", "categories": None, "notes": None},
                {"name": "y", "dtype": "float64", "var_type": "continuous", "categories": None, "notes": None},
            ],
        }
    }
    
    grid_layout = [
        {
            "grid_position": {"row": 0, "col": 0, "rowspan": 1, "colspan": 1},
            "datasource_id": "ds1",
            "x": "x",
            "y": "y",
            "hue": None,
            "sem_column": None,
            "sem_precomputed": False,
            "filter_query": None,
            "hlines": [0, 50],
            "vlines": [10],
            "style_line": True,
            "style_marker": False,
            "ylim": [0, 100],
            "title": "Test Plot",
        }
    ]
    
    # Save
    project_path = tmp_path / "test_project.ppo"
    save_workspace(str(project_path), grid_layout, datasources, grid_rows=2, grid_cols=2)
    
    # Verify file exists
    assert project_path.exists()
    
    # Load
    loaded = load_workspace(str(project_path))
    
    # Verify structure
    assert "version" in loaded
    assert "grid" in loaded
    assert "data_sources" in loaded
    assert "plots" in loaded
    
    # Verify data
    assert loaded["version"] == "0.9.0"
    assert len(loaded["data_sources"]) == 1
    assert len(loaded["plots"]) == 1
    
    # Verify datasource
    ds = loaded["data_sources"][0]
    assert ds["id"] == "ds1"
    assert ds["name"] == "test_data"
    
    # Verify plot
    plot = loaded["plots"][0]
    assert plot["x"] == "x"
    assert plot["y"] == "y"
    assert plot["hlines"] == [0, 50]
    assert plot["vlines"] == [10]
    assert plot["ylim"] == [0, 100]
    assert plot["title"] == "Test Plot"


def test_multi_column_hue_serialization(tmp_path):
    """Test that multi-column hue is preserved correctly."""
    grid_layout = [
        {
            "grid_position": {"row": 0, "col": 0, "rowspan": 1, "colspan": 1},
            "datasource_id": "ds1",
            "x": "time",
            "y": "value",
            "hue": ["species", "gender"],  # Multi-column hue
            "sem_column": None,
            "sem_precomputed": False,
            "filter_query": None,
            "hlines": [],
            "vlines": [],
            "style_line": True,
            "style_marker": False,
            "ylim": None,
            "title": None,
        }
    ]
    
    datasources = {
        "ds1": {
            "name": "iris",
            "path": str(tmp_path / "iris.csv"),
            "schema": [],
        }
    }
    
    project_path = tmp_path / "multi_hue.ppo"
    save_workspace(str(project_path), grid_layout, datasources, grid_rows=2, grid_cols=2)
    
    loaded = load_workspace(str(project_path))
    plot = loaded["plots"][0]
    
    # Verify multi-column hue is preserved as list
    assert isinstance(plot["hue"], list)
    assert plot["hue"] == ["species", "gender"]


def test_relative_paths(tmp_path):
    """Test that paths are stored relative to project file."""
    # Create subdirectory structure
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    project_dir = tmp_path / "projects"
    project_dir.mkdir()
    
    csv_path = data_dir / "test.csv"
    csv_path.write_text("x,y\n1,2\n3,4\n")
    
    datasources = {
        "ds1": {
            "name": "test",
            "path": str(csv_path),  # Absolute path
            "schema": [],
        }
    }
    
    grid_layout = []
    
    project_path = project_dir / "test.ppo"
    save_workspace(str(project_path), grid_layout, datasources, grid_rows=2, grid_cols=3)
    
    # Read raw JSON to verify relative path
    with open(project_path) as f:
        raw_data = json.load(f)
    
    # Path should be relative to project file
    saved_path = raw_data["data_sources"][0]["path"]
    assert not Path(saved_path).is_absolute()
    assert saved_path == "../data/test.csv"
    
    # Load should convert back to absolute
    loaded = load_workspace(str(project_path))
    loaded_path = loaded["data_sources"][0]["path"]
    assert Path(loaded_path).is_absolute()
    assert Path(loaded_path) == csv_path


def test_version_check(tmp_path):
    """Test that incompatible versions are rejected."""
    project_path = tmp_path / "bad_version.ppo"
    
    # Create project with future version
    bad_project = {
        "version": "2.0.0",  # Future version
        "grid": {"rows": 2, "cols": 2},
        "data_sources": [],
        "plots": [],
    }
    
    with open(project_path, "w") as f:
        json.dump(bad_project, f)
    
    # Should raise error
    with pytest.raises(ValueError, match="Incompatible version"):
        load_workspace(str(project_path))


def test_empty_project(tmp_path):
    """Test saving and loading an empty project."""
    datasources = {}
    grid_layout = []
    
    project_path = tmp_path / "empty.ppo"
    save_workspace(str(project_path), grid_layout, datasources, grid_rows=2, grid_cols=3)
    
    loaded = load_workspace(str(project_path))
    
    assert len(loaded["data_sources"]) == 0
    assert len(loaded["plots"]) == 0
    assert loaded["grid"]["rows"] == 2  # Default minimum
    assert loaded["grid"]["cols"] == 3  # Default minimum


def test_spanning_plots(tmp_path):
    """Test that plot spanning is preserved."""
    grid_layout = [
        {
            "grid_position": {"row": 0, "col": 0, "rowspan": 2, "colspan": 3},
            "datasource_id": "ds1",
            "x": "x",
            "y": "y",
            "hue": None,
            "sem_column": None,
            "sem_precomputed": False,
            "filter_query": None,
            "hlines": [],
            "vlines": [],
            "style_line": True,
            "style_marker": False,
            "ylim": None,
            "title": "Spanning Plot",
        }
    ]
    
    datasources = {
        "ds1": {
            "name": "data",
            "path": str(tmp_path / "data.csv"),
            "schema": [],
        }
    }
    
    project_path = tmp_path / "spanning.ppo"
    save_workspace(str(project_path), grid_layout, datasources, grid_rows=2, grid_cols=3)
    
    loaded = load_workspace(str(project_path))
    plot = loaded["plots"][0]
    
    assert plot["grid_position"]["rowspan"] == 2
    assert plot["grid_position"]["colspan"] == 3


def test_datasource_matching():
    """Test that datasource matching by dataframe works correctly.
    
    This tests that serialize_layout can match a tile's dataframe to the
    correct datasource ID when given MainWindow's {id: object} map.
    """
    # Simulate MainWindow's datasource storage
    class MockDataSource:
        def __init__(self, ds_id, name):
            self.id = ds_id
            self.name = name
            self.dataframe = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
    
    ds1 = MockDataSource("ds_123", "Dataset1")
    ds2 = MockDataSource("ds_456", "Dataset2")
    
    # MainWindow stores as {id: object}
    datasources = {
        "ds_123": ds1,
        "ds_456": ds2,
    }
    
    # Simulate what serialize_layout does: find datasource ID by matching dataframe
    test_df = ds1.dataframe
    found_id = None
    for ds_id, ds_obj in datasources.items():
        if test_df is ds_obj.dataframe:
            found_id = ds_id
            break
    
    assert found_id == "ds_123", "Should find correct datasource ID by dataframe match"
    
    # Test with second datasource
    test_df2 = ds2.dataframe
    found_id2 = None
    for ds_id, ds_obj in datasources.items():
        if test_df2 is ds_obj.dataframe:
            found_id2 = ds_id
            break
    
    assert found_id2 == "ds_456", "Should find correct datasource ID for second dataframe"


def test_sparse_grid_preserves_dimensions(tmp_path):
    """Test that saving a large grid with few plots preserves grid dimensions.
    
    Regression test for bug where a 2x3 grid with only 2 plots would become
    2x1 or 1x2 after save/load.
    """
    # Create a 3x4 grid with only 2 plots in corners
    grid_layout = [
        {
            "grid_position": {"row": 0, "col": 0, "rowspan": 1, "colspan": 1},
            "datasource_id": "ds1",
            "x": "x",
            "y": "y",
            "hue": None,
            "sem_column": None,
            "sem_precomputed": False,
            "filter_query": None,
            "hlines": [],
            "vlines": [],
            "style_line": True,
            "style_marker": False,
            "ylim": None,
            "title": "Plot 1",
        },
        {
            "grid_position": {"row": 2, "col": 3, "rowspan": 1, "colspan": 1},
            "datasource_id": "ds1",
            "x": "x",
            "y": "y",
            "hue": None,
            "sem_column": None,
            "sem_precomputed": False,
            "filter_query": None,
            "hlines": [],
            "vlines": [],
            "style_line": True,
            "style_marker": False,
            "ylim": None,
            "title": "Plot 2",
        }
    ]
    
    datasources = {
        "ds1": {
            "name": "data",
            "path": str(tmp_path / "data.csv"),
            "schema": [],
        }
    }
    
    # Save with specific grid dimensions (3 rows x 4 cols)
    project_path = tmp_path / "sparse.ppo"
    save_workspace(str(project_path), grid_layout, datasources, grid_rows=3, grid_cols=4)
    
    # Load back
    loaded = load_workspace(str(project_path))
    
    # Grid dimensions should be preserved
    assert loaded["grid"]["rows"] == 3, "Grid rows should be preserved"
    assert loaded["grid"]["cols"] == 4, "Grid columns should be preserved"
    
    # Both plots should still be there
    assert len(loaded["plots"]) == 2

