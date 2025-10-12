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


def shared_limits_with_sem(
    df: pd.DataFrame,
    filter_queries: list[dict[str, Any]],
    x: str,
    y: str,
    sem_column: str | None,
    hue: str | None = None,
    sem_precomputed: bool = False,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Compute shared x/y limits accounting for SEM aggregation.
    
    When sem_column is provided, computes limits based on the aggregated
    means ± SEM rather than raw data values. This ensures the y-axis is
    scaled appropriately for what will actually be plotted.
    """
    xmins: list[float] = []
    xmaxs: list[float] = []
    ymins: list[float] = []
    ymaxs: list[float] = []
    
    for fq in filter_queries:
        # Apply filter
        subset = df
        for col, val in fq.items():
            subset = subset[subset[col] == val]
        
        if subset.empty:
            continue
        
        # Process x-axis
        xnum = pd.to_numeric(subset[x], errors="coerce")
        if xnum.notna().any():
            xmins.append(float(xnum.min()))
            xmaxs.append(float(xnum.max()))
        
        # Process y-axis with SEM aggregation if needed
        if sem_column and sem_column in subset.columns:
            # Apply same aggregation logic as plotting
            if hue and hue in subset.columns:
                # Group by hue first, then aggregate
                for _, hue_sub in subset.groupby(hue):
                    if sem_precomputed:
                        y_vals = _compute_precomputed_sem_stats(hue_sub, x, y, sem_column)
                    else:
                        y_vals = _compute_sem_stats(hue_sub, x, y, sem_column)
                    if y_vals:
                        ymins.extend(y_vals[0])  # means - SEM
                        ymaxs.extend(y_vals[1])  # means + SEM
            else:
                if sem_precomputed:
                    y_vals = _compute_precomputed_sem_stats(subset, x, y, sem_column)
                else:
                    y_vals = _compute_sem_stats(subset, x, y, sem_column)
                if y_vals:
                    ymins.extend(y_vals[0])
                    ymaxs.extend(y_vals[1])
        else:
            # No SEM: use aggregated means
            if hue and hue in subset.columns:
                for _, hue_sub in subset.groupby(hue):
                    agg = hue_sub.groupby(x, as_index=False)[y].mean()
                    ynum = pd.to_numeric(agg[y], errors="coerce")
                    if ynum.notna().any():
                        ymins.append(float(ynum.min()))
                        ymaxs.append(float(ynum.max()))
            else:
                agg = subset.groupby(x, as_index=False)[y].mean()
                ynum = pd.to_numeric(agg[y], errors="coerce")
                if ynum.notna().any():
                    ymins.append(float(ynum.min()))
                    ymaxs.append(float(ynum.max()))
    
    if not xmins or not ymins:
        return (0.0, 1.0), (0.0, 1.0)
    
    return (min(xmins), max(xmaxs)), (min(ymins), max(ymaxs))


def _compute_sem_stats(
    df: pd.DataFrame, x: str, y: str, sem_column: str
) -> tuple[list[float], list[float]] | None:
    """Helper to compute mean ± SEM values for a dataframe.
    
    Returns (lower_bounds, upper_bounds) where lower = mean - SEM
    and upper = mean + SEM for each x value.
    """
    grouped = df.groupby([sem_column, x], as_index=False)[y].mean()
    stats = grouped.groupby(x)[y].agg(['mean', 'sem']).reset_index()
    
    if stats.empty:
        return None
    
    means = stats['mean'].values
    sems = stats['sem'].fillna(0).values  # Fill NaN SEM with 0
    
    lower_bounds = (means - sems).tolist()
    upper_bounds = (means + sems).tolist()
    
    return (lower_bounds, upper_bounds)


def _compute_precomputed_sem_stats(
    df: pd.DataFrame, x: str, y: str, sem_column: str
) -> tuple[list[float], list[float]] | None:
    """Helper to compute mean ± pre-computed SEM values for a dataframe.
    
    Averages y and SEM values if multiple rows exist for the same x.
    Returns (lower_bounds, upper_bounds) where lower = mean - SEM
    and upper = mean + SEM for each x value.
    """
    # Aggregate by x: mean of y and mean of sem
    agg_df = df.groupby(x, as_index=False).agg({
        y: 'mean',
        sem_column: 'mean'
    })
    
    if agg_df.empty:
        return None
    
    means = agg_df[y].values
    sems = agg_df[sem_column].fillna(0).values  # Fill NaN SEM with 0
    
    lower_bounds = (means - sems).tolist()
    upper_bounds = (means + sems).tolist()
    
    return (lower_bounds, upper_bounds)


