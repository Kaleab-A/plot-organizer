from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Optional

import pandas as pd


@dataclass
class ColumnSchema:
    name: str
    dtype: str
    var_type: Literal["categorical", "continuous", "ordinal"]
    categories: list[str] | None = None
    notes: Optional[str] = None


@dataclass
class DataSource:
    id: str
    name: str
    path: str
    dataframe: pd.DataFrame
    schema: list[ColumnSchema]


@dataclass
class PlotSpec:
    id: str
    datasource_id: str
    x: str
    y: str
    hue: str | None
    groups: list[str]
    title: str | None = None
    share_axes: bool = False
    style_overrides: dict[str, Any] = field(default_factory=dict)


@dataclass
class PlotInstance:
    id: str
    spec_id: str
    filter_query: dict[str, Any]
    empty: bool


@dataclass
class GridLayout:
    rows: int
    cols: int
    # For simplicity of persistence and decoupling the view layer, store plot instance IDs in cells
    # rather than object references.
    cells: dict[tuple[int, int], str | None] = field(default_factory=dict)


