from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional
import uuid
from pathlib import Path

import pandas as pd

from plot_organizer.models import ColumnSchema, DataSource


def infer_var_type(series: pd.Series) -> str:
    if pd.api.types.is_numeric_dtype(series):
        nunique = series.dropna().nunique()
        if nunique <= 20 and nunique <= max(1, int(0.05 * len(series))):
            return "categorical"
        return "continuous"
    if pd.api.types.is_categorical_dtype(series):
        return "ordinal" if series.cat.ordered else "categorical"
    return "categorical"


def build_schema(df: pd.DataFrame) -> list[ColumnSchema]:
    schema: list[ColumnSchema] = []
    for name, col in df.items():
        var_type = infer_var_type(col)
        categories = None
        if var_type in {"categorical", "ordinal"}:
            categories = sorted(col.dropna().unique().tolist())
        schema.append(
            ColumnSchema(
                name=name,
                dtype=str(col.dtype),
                var_type=var_type, 
                categories=categories,
            )
        )
    return schema


def load_csv_to_datasource(path: str, name: Optional[str] = None) -> DataSource:
    """Load a CSV file into a DataSource with inferred schema.

    This is a synchronous loader; call it from a worker thread in the UI.
    """
    df = pd.read_csv(path)
    schema = build_schema(df)
    ds = DataSource(
        id=str(uuid.uuid4()),
        name=name or Path(path).stem,
        path=path,
        dataframe=df,
        schema=schema,
    )
    return ds


