from __future__ import annotations

import json
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


