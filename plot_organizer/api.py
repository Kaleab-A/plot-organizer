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
    xlim: tuple[float, float] | list[float] | None = None,
    xticks: list[float] | None = None,
    yticks: list[float] | None = None,
    title: str | None = None,
    error_markers: list[dict[str, Any]] | None = None,
    flip_axes: bool = False,
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
        xlim: X-axis limits as (min, max) tuple or list
        xticks: Custom x-axis tick values (in order to display). If None, use default.
        yticks: Custom y-axis tick values (in order to display). If None, use default.
        title: Plot title
        error_markers: List of error bar marker dicts. Each dict should have:
            - x, y: position values. For horizontal bars (xerr), y can be integer 0,1,2...
                to select stacking level. For vertical bars (yerr), x can be integer 0,1,2...
                to select stacking level. If not provided, auto-computed.
            - xerr, yerr: error bar widths (at least one required)
            - marker: marker shape (default: 'v' for triangle down)
                Available: 'v', '^', 'o', 's', 'D', '*', 'x', '+', '<', '>'
            - color: marker color (required)
            - label: optional label for legend
        flip_axes: If True, Y is the independent variable (control) and X is the
            dependent variable (measure). Lines connect vertically, SEM bands are
            horizontal. (default: False)
    
    Returns:
        Plot dict with all parameters and grid position
    
    Example:
        >>> plot = create_plot(
        ...     ds_id,
        ...     x="time",
        ...     y="accuracy",
        ...     error_markers=[
        ...         {"x": 5.0, "xerr": 0.5, "y": 0, "marker": "v", "color": "red", "label": "Event 1"},
        ...         {"x": 10.0, "xerr": 0.3, "y": 1, "marker": "^", "color": "blue", "label": "Event 2"}
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
        "xlim": list(xlim) if xlim else None,
        "xticks": xticks,
        "yticks": yticks,
        "title": title,
        "error_markers": error_markers or [],
        "flip_axes": flip_axes,
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


def _expand_limits_for_reference_lines(
    xlim: list[float] | None,
    ylim: list[float] | None,
    hlines: list[float] | None,
    vlines: list[float] | None,
    xlim_auto: bool = True,
    ylim_auto: bool = True,
) -> tuple[list[float] | None, list[float] | None]:
    """Expand axis limits to include reference lines and add padding.
    
    For auto-computed limits, adds 10% total padding (5% on each side).
    Also ensures that horizontal and vertical reference lines are visible.
    
    Args:
        xlim: X-axis limits
        ylim: Y-axis limits
        hlines: Horizontal reference line positions
        vlines: Vertical reference line positions
        xlim_auto: If True, xlim was auto-computed (apply padding)
        ylim_auto: If True, ylim was auto-computed (apply padding)
    """
    # Add 5% margin on each side (10% total) only for auto-computed limits
    MARGIN_FACTOR = 0.05
    
    # First, add padding to auto-computed base limits
    if xlim is not None and xlim_auto:
        xmin, xmax = xlim[0], xlim[1]
        x_range = xmax - xmin
        xmin = xmin - x_range * MARGIN_FACTOR
        xmax = xmax + x_range * MARGIN_FACTOR
        xlim = [xmin, xmax]
    
    if ylim is not None and ylim_auto:
        ymin, ymax = ylim[0], ylim[1]
        y_range = ymax - ymin
        ymin = ymin - y_range * MARGIN_FACTOR
        ymax = ymax + y_range * MARGIN_FACTOR
        ylim = [ymin, ymax]
    
    # Then, expand to include reference lines if needed (regardless of auto)
    if hlines and ylim is not None:
        ymin, ymax = ylim[0], ylim[1]
        for hval in hlines:
            if hval < ymin:
                margin = (ymax - ymin) * MARGIN_FACTOR
                ymin = hval - margin
            if hval > ymax:
                margin = (ymax - ymin) * MARGIN_FACTOR
                ymax = hval + margin
        ylim = [ymin, ymax]
    
    if vlines and xlim is not None:
        xmin, xmax = xlim[0], xlim[1]
        for vval in vlines:
            if vval < xmin:
                margin = (xmax - xmin) * MARGIN_FACTOR
                xmin = vval - margin
            if vval > xmax:
                margin = (xmax - xmin) * MARGIN_FACTOR
                xmax = vval + margin
        xlim = [xmin, xmax]
    
    return xlim, ylim


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
    xlim: tuple[float, float] | list[float] | None = None,
    xticks: list[float] | None = None,
    yticks: list[float] | None = None,
    error_markers: list[dict[str, Any]] | None = None,
    flip_axes: bool = False,
) -> list[dict[str, Any]]:
    """Create multiple plots from group columns with shared axis limits.
    
    This replicates the GUI's "groups" feature, where plots are created for
    each unique combination of group column values and automatically share
    axis limits.
    
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
        xlim: Manual x-limits (if None, auto-computed and shared)
        xticks: Custom x-axis tick values (in order to display). If None, use default.
        yticks: Custom y-axis tick values (in order to display). If None, use default.
        error_markers: List of error bar markers to add to each plot
        flip_axes: If True, Y is independent, X is dependent. (default: False)
    
    Returns:
        List of plot dicts with auto-computed positions and shared limits
    
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
        >>> # All plots share the same auto-computed axis limits
    """
    from plot_organizer.services.plot_service import expand_groups, shared_limits, shared_limits_with_sem
    
    # Load dataframe to compute limits.
    # low_memory=False ensures consistent type inference across the full file —
    # avoids mixed int/str for columns that contain both numeric and non-numeric
    # values (e.g. "Dim" column with values 1, 2, 3 and "All").
    df = pd.read_csv(dataframe_path, low_memory=False)
    
    # Expand groups to get filter queries
    filter_queries = expand_groups(df, groups)
    
    # Compute shared limits if not provided
    computed_xlim = xlim
    computed_ylim = ylim
    xlim_auto = xlim is None  # Track if limits were auto-computed
    ylim_auto = ylim is None
    
    if (ylim is None or xlim is None) and len(filter_queries) > 1:
        if sem_column:
            # SEM-aware limits
            xlim_tuple, ylim_tuple = shared_limits_with_sem(
                df, filter_queries, x, y, sem_column, hue, sem_precomputed, flip_axes
            )
        else:
            # Standard limits
            subsets = []
            for fq in filter_queries:
                subset = df
                for col, val in fq.items():
                    subset = subset[subset[col] == val]
                subsets.append(subset)
            xlim_tuple, ylim_tuple = shared_limits(subsets, x, y, flip_axes)
        
        # Convert tuples to lists for JSON, only if not provided
        if xlim is None:
            computed_xlim = list(xlim_tuple) if xlim_tuple else None
        if ylim is None:
            computed_ylim = list(ylim_tuple) if ylim_tuple else None
    
    # Expand limits to include reference lines (padding only for auto-computed)
    computed_xlim, computed_ylim = _expand_limits_for_reference_lines(
        computed_xlim, computed_ylim, hlines, vlines, xlim_auto, ylim_auto
    )
    
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
            ylim=computed_ylim,
            xlim=computed_xlim,
            xticks=xticks,
            yticks=yticks,
            title=title,
            error_markers=error_markers,
            flip_axes=flip_axes,
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

