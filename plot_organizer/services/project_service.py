from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any

from plot_organizer.models import ColumnSchema, DataSource, PlotSpec, PlotInstance, GridLayout


def save_project(
    path: str,
    data_sources: list[DataSource],
    plots: list[PlotSpec],
    instances: list[PlotInstance],
    grid: GridLayout,
) -> None:
    """Legacy save function using model-based approach (not currently used by UI)."""
    root = Path(path).resolve().parent

    def make_rel(p: str) -> str:
        try:
            return str(Path(p).resolve().relative_to(root))
        except Exception:
            return p

    payload: dict[str, Any] = {
        "version": 1,
        "data_sources": [
            {
                "id": ds.id,
                "name": ds.name,
                "path": make_rel(ds.path),
                "schema": [asdict(s) for s in ds.schema],
            }
            for ds in data_sources
        ],
        "plots": [asdict(p) for p in plots],
        "instances": [asdict(i) for i in instances],
        "grid": {
            "rows": grid.rows,
            "cols": grid.cols,
            "cells": {str(k): v for k, v in grid.cells.items()},
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def save_workspace(
    path: str,
    grid_layout: list[dict[str, Any]],
    data_sources: dict[str, dict[str, Any]],
    grid_rows: int,
    grid_cols: int,
) -> None:
    """Save workspace state from UI components to JSON file.
    
    Args:
        path: Output file path (.ppo)
        grid_layout: List of plot descriptors from GridBoard.serialize_layout()
        data_sources: Dict of datasource info {id: {name, path, schema}}
        grid_rows: Actual number of rows in the grid
        grid_cols: Actual number of columns in the grid
    """
    root = Path(path).resolve().parent

    def make_rel(p: str) -> str:
        """Convert absolute path to relative path from project file."""
        try:
            abs_path = str(Path(p).resolve())
            rel_path = os.path.relpath(abs_path, root)
            return rel_path
        except (ValueError, Exception):
            # If relpath fails (e.g., different drive on Windows), keep absolute
            return str(p)

    # Use the actual grid dimensions passed in
    rows, cols = grid_rows, grid_cols

    # Convert data sources to list format with relative paths
    ds_list = []
    for ds_id, ds_info in data_sources.items():
        ds_dict = {
            "id": ds_id,
            "name": ds_info["name"],
            "path": make_rel(ds_info["path"]),
            "schema": ds_info.get("schema", []),
        }
        ds_list.append(ds_dict)

    payload: dict[str, Any] = {
        "version": "0.9.0",
        "grid": {
            "rows": rows,
            "cols": cols,
        },
        "data_sources": ds_list,
        "plots": grid_layout,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def load_workspace(path: str) -> dict[str, Any]:
    """Load workspace state from JSON file.
    
    Args:
        path: Input file path (.ppo)
    
    Returns:
        Dict with keys: version, grid, data_sources, plots
        Paths in data_sources are converted to absolute paths.
    
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
        ValueError: If version is incompatible
    """
    root = Path(path).resolve().parent

    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    # Version check
    version = payload.get("version", "0.0.0")
    if not isinstance(version, str):
        raise ValueError(f"Invalid version format: {version}")
    
    # For now, accept any 0.x version
    if not version.startswith("0."):
        raise ValueError(f"Incompatible version: {version}. Expected 0.x")

    def make_abs(p: str) -> str:
        """Convert relative path to absolute path."""
        path_obj = Path(p)
        if path_obj.is_absolute():
            return str(path_obj)
        return str((root / path_obj).resolve())

    # Convert relative paths to absolute
    for ds in payload.get("data_sources", []):
        ds["path"] = make_abs(ds["path"])

    return payload


