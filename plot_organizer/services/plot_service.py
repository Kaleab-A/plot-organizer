from __future__ import annotations

import itertools
from typing import Any

import pandas as pd


def expand_groups(df: pd.DataFrame, groups: list[str]) -> list[dict[str, Any]]:
    """Return concrete equality filter dictionaries for the Cartesian product of group columns.

    Caps the number of combinations at 50 to align with v1 UX constraints.
    """
    if not groups:
        return [{}]
    uniques: list[list[Any]] = [
        sorted(df[g].dropna().unique().tolist()) for g in groups
    ]
    combos = [dict(zip(groups, vals)) for vals in itertools.product(*uniques)]
    if len(combos) > 50:
        raise ValueError("Too many combinations (>50). Reduce groups or categories.")
    return combos


def shared_limits(
    subsets: list[pd.DataFrame], x: str, y: str
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Compute shared x/y limits across non-empty subsets.

    Non-numeric columns are coerced with to_numeric (errors coerced to NaN) to
    provide a consistent numeric range for plotting comparisons.
    """
    xmins: list[float] = []
    xmaxs: list[float] = []
    ymins: list[float] = []
    ymaxs: list[float] = []
    for sub in subsets:
        if sub is None or sub.empty:
            continue
        xnum = pd.to_numeric(sub[x], errors="coerce")
        ynum = pd.to_numeric(sub[y], errors="coerce")
        if xnum.notna().any():
            xmins.append(float(xnum.min()))
            xmaxs.append(float(xnum.max()))
        if ynum.notna().any():
            ymins.append(float(ynum.min()))
            ymaxs.append(float(ynum.max()))
    if not xmins or not ymins:
        # Fallback to zeros if everything is empty/NaN to avoid crashes upstream
        return (0.0, 1.0), (0.0, 1.0)
    return (min(xmins), max(xmaxs)), (min(ymins), max(ymaxs))


