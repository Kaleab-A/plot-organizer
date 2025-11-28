"""Tests for programmatic API."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from plot_organizer.api import (
    create_datasource,
    create_plot,
    create_project,
    save_project_file,
    load_project_file,
    quick_project,
    create_grouped_plots,
    quick_grouped_project,
)


def test_create_datasource():
    """Test datasource creation."""
    ds = create_datasource("test_data", "data/test.csv")
    
    assert "id" in ds
    assert ds["name"] == "test_data"
    assert ds["path"] == "data/test.csv"
    assert ds["schema"] == []


def test_create_datasource_with_schema():
    """Test datasource with schema."""
    schema = [
        {"name": "x", "dtype": "int64", "var_type": "continuous"},
        {"name": "y", "dtype": "float64", "var_type": "continuous"},
    ]
    
    ds = create_datasource("test", "data.csv", schema=schema)
    
    assert ds["schema"] == schema


def test_create_plot_basic():
    """Test basic plot creation."""
    plot = create_plot(
        "ds123",
        x="time",
        y="value",
        row=0,
        col=0
    )
    
    assert plot["datasource_id"] == "ds123"
    assert plot["x"] == "time"
    assert plot["y"] == "value"
    assert plot["grid_position"]["row"] == 0
    assert plot["grid_position"]["col"] == 0
    assert plot["grid_position"]["rowspan"] == 1
    assert plot["grid_position"]["colspan"] == 1
    assert plot["hue"] is None
    assert plot["style_line"] is True
    assert plot["style_marker"] is False


def test_create_plot_with_multi_hue():
    """Test plot with multi-column hue."""
    plot = create_plot(
        "ds123",
        x="time",
        y="value",
        hue=["species", "gender"],
        row=0,
        col=0
    )
    
    assert plot["hue"] == ["species", "gender"]


def test_create_plot_with_sem():
    """Test plot with SEM."""
    plot = create_plot(
        "ds123",
        x="time",
        y="value",
        sem_column="trial",
        sem_precomputed=True,
        row=0,
        col=0
    )
    
    assert plot["sem_column"] == "trial"
    assert plot["sem_precomputed"] is True


def test_create_plot_with_reference_lines():
    """Test plot with reference lines."""
    plot = create_plot(
        "ds123",
        x="time",
        y="value",
        hlines=[0, 50, 100],
        vlines=[10, 20],
        row=0,
        col=0
    )
    
    assert plot["hlines"] == [0, 50, 100]
    assert plot["vlines"] == [10, 20]


def test_create_plot_with_spanning():
    """Test plot with row/col spanning."""
    plot = create_plot(
        "ds123",
        x="time",
        y="value",
        row=1,
        col=2,
        rowspan=2,
        colspan=3
    )
    
    assert plot["grid_position"]["row"] == 1
    assert plot["grid_position"]["col"] == 2
    assert plot["grid_position"]["rowspan"] == 2
    assert plot["grid_position"]["colspan"] == 3


def test_create_plot_with_all_options():
    """Test plot with all options."""
    plot = create_plot(
        "ds123",
        x="time",
        y="accuracy",
        row=0,
        col=0,
        rowspan=1,
        colspan=2,
        hue=["model", "dataset"],
        sem_column="fold",
        sem_precomputed=False,
        filter_query={"experiment": "A"},
        hlines=[0.5, 0.9],
        vlines=[100, 200],
        style_line=True,
        style_marker=True,
        ylim=(0.0, 1.0),
        title="Model Performance"
    )
    
    assert plot["x"] == "time"
    assert plot["y"] == "accuracy"
    assert plot["hue"] == ["model", "dataset"]
    assert plot["sem_column"] == "fold"
    assert plot["filter_query"] == {"experiment": "A"}
    assert plot["hlines"] == [0.5, 0.9]
    assert plot["vlines"] == [100, 200]
    assert plot["style_line"] is True
    assert plot["style_marker"] is True
    assert plot["ylim"] == [0.0, 1.0]
    assert plot["title"] == "Model Performance"


def test_create_project():
    """Test project creation."""
    ds = create_datasource("data", "data.csv")
    plot1 = create_plot(ds["id"], "x", "y", row=0, col=0)
    plot2 = create_plot(ds["id"], "x", "z", row=0, col=1)
    
    project = create_project(
        grid_size=(2, 2),
        datasources=[ds],
        plots=[plot1, plot2]
    )
    
    assert project["version"] == "0.9.0"
    assert project["grid"]["rows"] == 2
    assert project["grid"]["cols"] == 2
    assert len(project["data_sources"]) == 1
    assert len(project["plots"]) == 2


def test_save_and_load_project_file(tmp_path):
    """Test saving and loading project files."""
    ds = create_datasource("test", "data.csv")
    plot = create_plot(ds["id"], "x", "y", row=0, col=0)
    project = create_project((2, 2), [ds], [plot])
    
    project_path = tmp_path / "test.ppo"
    save_project_file(project, str(project_path))
    
    assert project_path.exists()
    
    loaded = load_project_file(str(project_path))
    
    assert loaded["version"] == "0.9.0"
    assert len(loaded["data_sources"]) == 1
    assert len(loaded["plots"]) == 1


def test_quick_project():
    """Test quick_project convenience function."""
    plots = [
        create_plot("", "x", "y1", row=0, col=0),
        create_plot("", "x", "y2", row=0, col=1),
        create_plot("", "x", "y3", row=1, col=0),
    ]
    
    project = quick_project(
        "mydata",
        "data/results.csv",
        plots
    )
    
    assert len(project["data_sources"]) == 1
    assert project["data_sources"][0]["name"] == "mydata"
    assert len(project["plots"]) == 3
    
    # All plots should have same datasource_id
    ds_id = project["data_sources"][0]["id"]
    for plot in project["plots"]:
        assert plot["datasource_id"] == ds_id
    
    # Grid size should be auto-computed
    assert project["grid"]["rows"] == 2
    assert project["grid"]["cols"] == 2


def test_quick_project_with_explicit_grid():
    """Test quick_project with explicit grid size."""
    plots = [
        create_plot("", "x", "y", row=0, col=0),
    ]
    
    project = quick_project(
        "data",
        "test.csv",
        plots,
        grid_size=(3, 3)
    )
    
    assert project["grid"]["rows"] == 3
    assert project["grid"]["cols"] == 3


def test_json_serialization(tmp_path):
    """Test that all created objects are JSON-serializable."""
    ds = create_datasource("test", "data.csv")
    plot = create_plot(
        ds["id"],
        "x",
        "y",
        hue=["a", "b"],
        sem_column="sem",
        sem_precomputed=True,
        filter_query={"group": "A"},
        hlines=[0.5],
        vlines=[10],
        ylim=(0, 1),
        title="Test"
    )
    project = create_project((2, 2), [ds], [plot])
    
    # Should not raise
    json_str = json.dumps(project)
    
    # Should round-trip
    loaded = json.loads(json_str)
    assert loaded == project


def test_create_grouped_plots(tmp_path):
    """Test creating grouped plots with auto-computed shared limits."""
    # Create test CSV
    csv_path = tmp_path / "test_groups.csv"
    df = pd.DataFrame({
        "time": [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
        "value": [10, 20, 30, 15, 25, 35, 12, 22, 32, 18, 28, 38],
        "species": ["A", "A", "A", "A", "A", "A", "B", "B", "B", "B", "B", "B"],
        "treatment": ["X", "X", "X", "Y", "Y", "Y", "X", "X", "X", "Y", "Y", "Y"],
    })
    df.to_csv(csv_path, index=False)
    
    # Create grouped plots
    plots = create_grouped_plots(
        datasource_id="ds123",
        dataframe_path=str(csv_path),
        x="time",
        y="value",
        groups=["species", "treatment"],
        start_row=0,
        start_col=0,
        layout="row"
    )
    
    # Should create 4 plots (2 species × 2 treatments)
    assert len(plots) == 4
    
    # All plots should have the same ylim (shared)
    ylims = [p["ylim"] for p in plots]
    assert all(ylim == ylims[0] for ylim in ylims), "All plots should share ylim"
    assert ylims[0] is not None, "ylim should be computed"
    
    # Check positions (row layout)
    assert plots[0]["grid_position"]["row"] == 0
    assert plots[0]["grid_position"]["col"] == 0
    assert plots[1]["grid_position"]["row"] == 0
    assert plots[1]["grid_position"]["col"] == 1
    assert plots[2]["grid_position"]["row"] == 0
    assert plots[2]["grid_position"]["col"] == 2
    
    # Check filter queries
    assert plots[0]["filter_query"] == {"species": "A", "treatment": "X"}
    assert plots[1]["filter_query"] == {"species": "A", "treatment": "Y"}
    assert plots[2]["filter_query"] == {"species": "B", "treatment": "X"}
    assert plots[3]["filter_query"] == {"species": "B", "treatment": "Y"}
    
    # Check titles
    assert "species=A" in plots[0]["title"]
    assert "treatment=X" in plots[0]["title"]


def test_create_grouped_plots_column_layout(tmp_path):
    """Test grouped plots with column layout."""
    csv_path = tmp_path / "test_col_layout.csv"
    df = pd.DataFrame({
        "x": [1, 2, 3] * 2,
        "y": [10, 20, 30] * 2,
        "group": ["A"] * 3 + ["B"] * 3,
    })
    df.to_csv(csv_path, index=False)
    
    plots = create_grouped_plots(
        datasource_id="ds",
        dataframe_path=str(csv_path),
        x="x",
        y="y",
        groups=["group"],
        start_row=1,
        start_col=2,
        layout="col"  # Vertical layout
    )
    
    assert len(plots) == 2
    # Column layout: stack vertically
    assert plots[0]["grid_position"]["row"] == 1
    assert plots[0]["grid_position"]["col"] == 2
    assert plots[1]["grid_position"]["row"] == 2
    assert plots[1]["grid_position"]["col"] == 2


def test_create_grouped_plots_with_manual_ylim(tmp_path):
    """Test that manual ylim overrides auto-computation."""
    csv_path = tmp_path / "test_manual_ylim.csv"
    df = pd.DataFrame({
        "x": [1, 2] * 2,
        "y": [10, 20] * 2,
        "group": ["A", "A", "B", "B"],
    })
    df.to_csv(csv_path, index=False)
    
    manual_ylim = (0, 100)
    plots = create_grouped_plots(
        datasource_id="ds",
        dataframe_path=str(csv_path),
        x="x",
        y="y",
        groups=["group"],
        ylim=manual_ylim
    )
    
    # All plots should use manual ylim
    assert all(p["ylim"] == list(manual_ylim) for p in plots)


def test_quick_grouped_project(tmp_path):
    """Test quick_grouped_project convenience function."""
    csv_path = tmp_path / "test_quick_grouped.csv"
    df = pd.DataFrame({
        "time": [1, 2, 3] * 4,
        "accuracy": [0.8, 0.85, 0.9] * 4,
        "model": ["A"] * 6 + ["B"] * 6,
        "dataset": ["X", "X", "X", "Y", "Y", "Y"] * 2,
    })
    df.to_csv(csv_path, index=False)
    
    project = quick_grouped_project(
        datasource_name="ML Results",
        datasource_path=str(csv_path),
        x="time",
        y="accuracy",
        groups=["model", "dataset"],
        hue="model",
    )
    
    # Check structure
    assert "version" in project
    assert "grid" in project
    assert "data_sources" in project
    assert "plots" in project
    
    # Should have 4 plots (2 models × 2 datasets)
    assert len(project["plots"]) == 4
    
    # All should have same datasource
    ds_ids = {p["datasource_id"] for p in project["plots"]}
    assert len(ds_ids) == 1
    
    # Grid size should be auto-computed
    assert project["grid"]["rows"] >= 1
    assert project["grid"]["cols"] >= 4  # 4 plots in row layout

