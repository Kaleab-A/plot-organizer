"""Programmatic API for creating PlotOrganizer projects without GUI.

This module provides functions to create project files (.ppo) programmatically,
enabling automated plot generation workflows.

Example:
    >>> from plot_organizer.api import *
    >>> 
    >>> ds = create_datasource("experiment", "data/results.csv")
    >>> plot1 = create_plot(
    ...     ds["id"],
    ...     x="time",
    ...     y="accuracy",
    ...     hue=["model", "dataset"],
    ...     row=0, col=0
    ... )
    >>> plot2 = create_plot(
    ...     ds["id"],
    ...     x="time",
    ...     y="loss",
    ...     row=0, col=1
    ... )
    >>> 
    >>> project = create_project(
    ...     grid_size=(2, 2),
    ...     datasources=[ds],
    ...     plots=[plot1, plot2]
    ... )
    >>> save_project_file(project, "experiment.ppo")
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

import pandas as pd


def create_datasource(name: str, path: str, schema: list[dict] | None = None) -> dict[str, Any]:
    """Create a datasource descriptor.
    
    Args:
        name: Display name for the datasource
        path: Path to CSV file (can be relative or absolute)
        schema: Optional list of column schemas. If None, will be inferred on load.
            Each schema dict should have: name, dtype, var_type, categories (optional)
    
    Returns:
        Datasource dict with id, name, path, schema
    """
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "path": str(path),
        "schema": schema or [],
    }


def create_plot(
    datasource_id: str,
    x: str,
    y: str,
    *,
    row: int = 0,
    col: int = 0,
    rowspan: int = 1,
    colspan: int = 1,
    hue: str | list[str] | None = None,
    sem_column: str | None = None,
    sem_precomputed: bool = False,
    filter_query: dict[str, Any] | None = None,
    hlines: list[float] | None = None,
    vlines: list[float] | None = None,
    style_line: bool = True,
    style_marker: bool = False,
    ylim: tuple[float, float] | list[float] | None = None,
    title: str | None = None,
    error_markers: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create a plot descriptor.
    
    Args:
        datasource_id: ID of the datasource (from create_datasource)
        x: Column name for x-axis
        y: Column name for y-axis
        row: Grid row position (0-indexed)
        col: Grid column position (0-indexed)
        rowspan: Number of rows to span (default: 1)
        colspan: Number of columns to span (default: 1)
        hue: Column name(s) for color grouping. Can be:
            - None: no hue
            - str: single column
            - list[str]: multiple columns (creates composite labels)
        sem_column: Column for SEM calculation or pre-computed SEM values
        sem_precomputed: If True, use sem_column values directly (default: False)
        filter_query: Dict of column=value filters to apply
        hlines: List of y-values for horizontal reference lines
        vlines: List of x-values for vertical reference lines
        style_line: Show lines (default: True)
        style_marker: Show markers (default: False)
        ylim: Y-axis limits as (min, max) tuple or list
        title: Plot title
        error_markers: List of error bar marker dicts. Each dict should have:
            - x, y: position values (at least one required, others auto-computed)
            - xerr, yerr: error bar widths (at least one required)
            - color: marker color (required)
            - label: optional label for legend
    
    Returns:
        Plot dict with all parameters and grid position
    
    Example:
        >>> plot = create_plot(
        ...     ds_id,
        ...     x="time",
        ...     y="accuracy",
        ...     error_markers=[
        ...         {"x": 5.0, "xerr": 0.5, "color": "red", "label": "Event 1"},
        ...         {"x": 10.0, "xerr": 0.3, "color": "blue", "label": "Event 2"}
        ...     ]
        ... )
    """
    plot_data = {
        "id": str(uuid.uuid4()),
        "grid_position": {
            "row": row,
            "col": col,
            "rowspan": rowspan,
            "colspan": colspan,
        },
        "datasource_id": datasource_id,
        "x": x,
        "y": y,
        "hue": hue,
        "sem_column": sem_column,
        "sem_precomputed": sem_precomputed,
        "filter_query": filter_query,
        "hlines": hlines or [],
        "vlines": vlines or [],
        "style_line": style_line,
        "style_marker": style_marker,
        "ylim": list(ylim) if ylim else None,
        "title": title,
        "error_markers": error_markers or [],
    }
    return plot_data


def create_project(
    grid_size: tuple[int, int],
    datasources: list[dict[str, Any]],
    plots: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create a complete project descriptor.
    
    Args:
        grid_size: (rows, cols) tuple for grid dimensions
        datasources: List of datasource dicts from create_datasource()
        plots: List of plot dicts from create_plot()
    
    Returns:
        Complete project dict ready for save_project_file()
    """
    rows, cols = grid_size
    return {
        "version": "0.9.0",
        "grid": {
            "rows": rows,
            "cols": cols,
        },
        "data_sources": datasources,
        "plots": plots,
    }


def save_project_file(project: dict[str, Any], path: str) -> None:
    """Save project dict to .ppo file.
    
    Args:
        project: Project dict from create_project()
        path: Output file path (.ppo extension recommended)
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(project, f, indent=2)


def load_project_file(path: str) -> dict[str, Any]:
    """Load project dict from .ppo file.
    
    Args:
        path: Input file path
    
    Returns:
        Project dict
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# Convenience function for quick project creation
def create_grouped_plots(
    datasource_id: str,
    dataframe_path: str,
    x: str,
    y: str,
    groups: list[str],
    *,
    start_row: int = 0,
    start_col: int = 0,
    layout: str = "row",
    hue: str | list[str] | None = None,
    sem_column: str | None = None,
    sem_precomputed: bool = False,
    hlines: list[float] | None = None,
    vlines: list[float] | None = None,
    style_line: bool = True,
    style_marker: bool = False,
    ylim: tuple[float, float] | list[float] | None = None,
    error_markers: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Create multiple plots from group columns with shared y-axis limits.
    
    This replicates the GUI's "groups" feature, where plots are created for
    each unique combination of group column values and automatically share
    y-axis limits.
    
    Args:
        datasource_id: ID of the datasource
        dataframe_path: Path to CSV file (needed to compute shared limits)
        x: Column name for x-axis
        y: Column name for y-axis
        groups: List of columns to group by (creates one plot per combination)
        start_row: Starting row for plot placement (default: 0)
        start_col: Starting column for plot placement (default: 0)
        layout: "row" (left-to-right) or "col" (top-to-bottom) layout
        hue: Column name(s) for color grouping
        sem_column: Column for SEM calculation
        sem_precomputed: If True, use sem_column values directly
        hlines: Horizontal reference lines
        vlines: Vertical reference lines
        style_line: Show lines
        style_marker: Show markers
        ylim: Manual y-limits (if None, auto-computed and shared)
        error_markers: List of error bar markers to add to each plot
    
    Returns:
        List of plot dicts with auto-computed positions and shared ylim
    
    Example:
        >>> plots = create_grouped_plots(
        ...     ds["id"],
        ...     "data/results.csv",
        ...     x="time",
        ...     y="accuracy",
        ...     groups=["species", "treatment"],
        ...     hue=["model"],
        ...     start_row=0,
        ...     start_col=0,
        ...     layout="row"
        ... )
        >>> # Creates one plot per (species, treatment) combination
        >>> # All plots share the same auto-computed y-axis limits
    """
    from plot_organizer.services.plot_service import expand_groups, shared_limits, shared_limits_with_sem
    
    # Load dataframe to compute limits
    df = pd.read_csv(dataframe_path)
    
    # Expand groups to get filter queries
    filter_queries = expand_groups(df, groups)
    
    # Compute shared limits if not provided
    if ylim is None and len(filter_queries) > 1:
        if sem_column:
            # SEM-aware limits
            xlim, ylim_tuple = shared_limits_with_sem(
                df, filter_queries, x, y, sem_column, hue, sem_precomputed
            )
        else:
            # Standard limits
            subsets = []
            for fq in filter_queries:
                subset = df
                for col, val in fq.items():
                    subset = subset[subset[col] == val]
                subsets.append(subset)
            xlim, ylim_tuple = shared_limits(subsets, x, y)
        
        # Convert tuple to list for JSON
        ylim = list(ylim_tuple) if ylim_tuple else None
    
    # Create plots with auto-positioning
    plots = []
    for i, fq in enumerate(filter_queries):
        # Compute position based on layout
        if layout == "row":
            row = start_row
            col = start_col + i
        else:  # "col"
            row = start_row + i
            col = start_col
        
        # Build title from filter query
        if fq:
            title_parts = [f"{k}={v}" for k, v in fq.items()]
            title = ", ".join(title_parts)
        else:
            title = None
        
        # Create plot
        plot = create_plot(
            datasource_id,
            x=x,
            y=y,
            row=row,
            col=col,
            hue=hue,
            sem_column=sem_column,
            sem_precomputed=sem_precomputed,
            filter_query=fq,
            hlines=hlines,
            vlines=vlines,
            style_line=style_line,
            style_marker=style_marker,
            ylim=ylim,
            title=title,
            error_markers=error_markers,
        )
        plots.append(plot)
    
    return plots


def quick_grouped_project(
    datasource_name: str,
    datasource_path: str,
    x: str,
    y: str,
    groups: list[str],
    **kwargs,
) -> dict[str, Any]:
    """Create a project with grouped plots from a single datasource.
    
    This is a convenience function that combines datasource creation and
    grouped plot generation.
    
    Args:
        datasource_name: Name for the datasource
        datasource_path: Path to CSV file
        x: Column name for x-axis
        y: Column name for y-axis
        groups: List of columns to group by
        **kwargs: Additional arguments passed to create_grouped_plots()
            (hue, sem_column, style_line, etc.)
    
    Returns:
        Complete project dict
    
    Example:
        >>> project = quick_grouped_project(
        ...     "Experiment",
        ...     "data/results.csv",
        ...     x="time",
        ...     y="accuracy",
        ...     groups=["species", "treatment"],
        ...     hue=["model"],
        ... )
        >>> save_project_file(project, "experiment.ppo")
    """
    ds = create_datasource(datasource_name, datasource_path)
    
    plots = create_grouped_plots(
        datasource_id=ds["id"],
        dataframe_path=datasource_path,
        x=x,
        y=y,
        groups=groups,
        **kwargs
    )
    
    # Auto-compute grid size
    if plots:
        max_row = max((p["grid_position"]["row"] + p["grid_position"]["rowspan"] for p in plots), default=1)
        max_col = max((p["grid_position"]["col"] + p["grid_position"]["colspan"] for p in plots), default=1)
        grid_size = (max_row, max_col)
    else:
        grid_size = (2, 3)
    
    return create_project(grid_size, [ds], plots)


def quick_project(
    datasource_name: str,
    datasource_path: str,
    plots: list[dict[str, Any]],
    grid_size: tuple[int, int] | None = None,
) -> dict[str, Any]:
    """Create a project with a single datasource.
    
    Args:
        datasource_name: Name for the datasource
        datasource_path: Path to CSV file
        plots: List of plot dicts (datasource_id will be auto-filled)
        grid_size: Optional grid size, auto-computed if None
    
    Returns:
        Complete project dict
    """
    ds = create_datasource(datasource_name, datasource_path)
    
    # Auto-fill datasource_id in plots
    for plot in plots:
        if "datasource_id" not in plot or not plot["datasource_id"]:
            plot["datasource_id"] = ds["id"]
    
    # Auto-compute grid size if not provided
    if grid_size is None:
        max_row = max((p["grid_position"]["row"] + p["grid_position"]["rowspan"] for p in plots), default=1)
        max_col = max((p["grid_position"]["col"] + p["grid_position"]["colspan"] for p in plots), default=1)
        grid_size = (max_row, max_col)
    
    return create_project(grid_size, [ds], plots)

