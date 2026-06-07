from __future__ import annotations

import itertools
from typing import Any

import pandas as pd


def expand_groups(df: pd.DataFrame, groups: list[str]) -> list[dict[str, Any]]:
    """Return concrete equality filter dictionaries for the Cartesian product of group columns.

    Caps the number of combinations at 200 to align with v1 UX constraints.
    """
    if not groups:
        return [{}]
    uniques: list[list[Any]] = [
        sorted(df[g].dropna().unique().tolist()) for g in groups
    ]
    combos = [dict(zip(groups, vals)) for vals in itertools.product(*uniques)]
    if len(combos) > 200:
        raise ValueError("Too many combinations (>200). Reduce groups or categories.")
    return combos


def shared_limits(
    subsets: list[pd.DataFrame], x: str, y: str, flip_axes: bool = False
) -> tuple[tuple[float, float] | None, tuple[float, float] | None]:
    """Compute shared x/y limits across non-empty subsets.

    Returns None for an axis if its column is categorical (non-numeric).
    This allows matplotlib to handle categorical axes automatically.
    
    This function returns the raw min/max values from the data. For aggregated
    limits that account for SEM, use shared_limits_with_sem().
    
    The flip_axes parameter doesn't change the calculation since we're just
    computing raw min/max for both columns - xlim always comes from x values,
    ylim always comes from y values.
    """
    # Check if columns are numeric - skip limit computation for categorical
    # Use first non-empty subset to check dtype
    x_is_numeric = False
    y_is_numeric = False
    for sub in subsets:
        if sub is not None and not sub.empty:
            x_is_numeric = pd.api.types.is_numeric_dtype(sub[x])
            y_is_numeric = pd.api.types.is_numeric_dtype(sub[y])
            break
    
    xmins: list[float] = []
    xmaxs: list[float] = []
    ymins: list[float] = []
    ymaxs: list[float] = []
    
    for sub in subsets:
        if sub is None or sub.empty:
            continue
        # Only compute limits for numeric columns
        if x_is_numeric:
            xnum = pd.to_numeric(sub[x], errors="coerce")
            if xnum.notna().any():
                xmins.append(float(xnum.min()))
                xmaxs.append(float(xnum.max()))
        if y_is_numeric:
            ynum = pd.to_numeric(sub[y], errors="coerce")
            if ynum.notna().any():
                ymins.append(float(ynum.min()))
                ymaxs.append(float(ynum.max()))
    
    # Return None for non-numeric or empty axes
    xlim = (min(xmins), max(xmaxs)) if xmins and x_is_numeric else None
    ylim = (min(ymins), max(ymaxs)) if ymins and y_is_numeric else None
    
    return xlim, ylim


def shared_limits_with_sem(
    df: pd.DataFrame,
    filter_queries: list[dict[str, Any]],
    x: str,
    y: str,
    sem_column: str | None,
    hue: str | list[str] | None = None,
    sem_precomputed: bool = False,
    flip_axes: bool = False,
) -> tuple[tuple[float, float] | None, tuple[float, float] | None]:
    """Compute shared x/y limits accounting for SEM aggregation.
    
    Returns None for an axis if its column is categorical (non-numeric).
    This allows matplotlib to handle categorical axes automatically.
    
    When sem_column is provided, computes limits based on the aggregated
    means ± SEM rather than raw data values. This ensures the dependent axis is
    scaled appropriately for what will actually be plotted.
    
    When flip_axes is True:
    - Y is the independent variable (grouped by)
    - X is the dependent variable (with SEM computed on it)
    """
    # Check if columns are numeric - skip limit computation for categorical
    x_is_numeric = pd.api.types.is_numeric_dtype(df[x])
    y_is_numeric = pd.api.types.is_numeric_dtype(df[y])
    
    # Determine independent and dependent columns and their numeric status
    if flip_axes:
        ind_col, dep_col = y, x
        ind_is_numeric, dep_is_numeric = y_is_numeric, x_is_numeric
    else:
        ind_col, dep_col = x, y
        ind_is_numeric, dep_is_numeric = x_is_numeric, y_is_numeric
    
    xmins: list[float] = []
    xmaxs: list[float] = []
    ymins: list[float] = []
    ymaxs: list[float] = []
    
    # Create composite hue column if hue is a list
    df_to_use = df
    actual_hue = None
    if hue:
        if isinstance(hue, list) and len(hue) > 0:
            # Create composite column with format: Col1=val1, Col2=val2
            df_to_use = df.copy()
            composite_name = "__composite_hue__"
            df_to_use[composite_name] = df_to_use.apply(
                lambda row: ", ".join(f"{col}={row[col]}" for col in hue),
                axis=1
            )
            actual_hue = composite_name
        elif isinstance(hue, str):
            actual_hue = hue
    
    def add_limits(ind_min, ind_max, dep_min, dep_max):
        """Add limits to the correct axis based on flip_axes."""
        if flip_axes:
            if ind_is_numeric and ind_min is not None and ind_max is not None:
                ymins.append(ind_min)
                ymaxs.append(ind_max)
            if dep_is_numeric:
                xmins.append(dep_min)
                xmaxs.append(dep_max)
        else:
            if ind_is_numeric and ind_min is not None and ind_max is not None:
                xmins.append(ind_min)
                xmaxs.append(ind_max)
            if dep_is_numeric:
                ymins.append(dep_min)
                ymaxs.append(dep_max)
    
    for fq in filter_queries:
        # Apply filter
        subset = df_to_use
        for col, val in fq.items():
            subset = subset[subset[col] == val]
        
        if subset.empty:
            continue
        
        # Process independent axis - only if numeric
        ind_min_val = None
        ind_max_val = None
        if ind_is_numeric:
            ind_num = pd.to_numeric(subset[ind_col], errors="coerce")
            if ind_num.notna().any():
                ind_min_val = float(ind_num.min())
                ind_max_val = float(ind_num.max())
        
        # Process dependent axis with SEM aggregation if needed (only if numeric)
        if not dep_is_numeric:
            # Dependent axis is categorical, skip
            continue
            
        if sem_column and sem_column in subset.columns:
            # Apply same aggregation logic as plotting
            if actual_hue and actual_hue in subset.columns:
                # Group by hue first, then aggregate
                for _, hue_sub in subset.groupby(actual_hue):
                    if sem_precomputed:
                        dep_vals = _compute_precomputed_sem_stats_generic(hue_sub, ind_col, dep_col, sem_column)
                    else:
                        dep_vals = _compute_sem_stats_generic(hue_sub, ind_col, dep_col, sem_column)
                    if dep_vals:
                        for lower, upper in zip(dep_vals[0], dep_vals[1]):
                            add_limits(ind_min_val, ind_max_val, lower, upper)
            else:
                if sem_precomputed:
                    dep_vals = _compute_precomputed_sem_stats_generic(subset, ind_col, dep_col, sem_column)
                else:
                    dep_vals = _compute_sem_stats_generic(subset, ind_col, dep_col, sem_column)
                if dep_vals:
                    for lower, upper in zip(dep_vals[0], dep_vals[1]):
                        add_limits(ind_min_val, ind_max_val, lower, upper)
        else:
            # No SEM: use aggregated means
            if actual_hue and actual_hue in subset.columns:
                for _, hue_sub in subset.groupby(actual_hue):
                    agg = hue_sub.groupby(ind_col, as_index=False)[dep_col].mean()
                    dep_num = pd.to_numeric(agg[dep_col], errors="coerce")
                    if dep_num.notna().any():
                        add_limits(ind_min_val, ind_max_val, 
                                   float(dep_num.min()), float(dep_num.max()))
            else:
                agg = subset.groupby(ind_col, as_index=False)[dep_col].mean()
                dep_num = pd.to_numeric(agg[dep_col], errors="coerce")
                if dep_num.notna().any():
                    add_limits(ind_min_val, ind_max_val,
                               float(dep_num.min()), float(dep_num.max()))
    
    # Return None for non-numeric or empty axes
    xlim = (min(xmins), max(xmaxs)) if xmins and x_is_numeric else None
    ylim = (min(ymins), max(ymaxs)) if ymins and y_is_numeric else None
    
    return xlim, ylim


def _compute_sem_stats(
    df: pd.DataFrame, x: str, y: str, sem_column: str
) -> tuple[list[float], list[float]] | None:
    """Helper to compute mean ± SEM values for a dataframe.
    
    Returns (lower_bounds, upper_bounds) where lower = mean - SEM
    and upper = mean + SEM for each x value.
    """
    return _compute_sem_stats_generic(df, x, y, sem_column)


def _compute_precomputed_sem_stats(
    df: pd.DataFrame, x: str, y: str, sem_column: str
) -> tuple[list[float], list[float]] | None:
    """Helper to compute mean ± pre-computed SEM values for a dataframe.
    
    Averages y and SEM values if multiple rows exist for the same x.
    Returns (lower_bounds, upper_bounds) where lower = mean - SEM
    and upper = mean + SEM for each x value.
    """
    return _compute_precomputed_sem_stats_generic(df, x, y, sem_column)


def _compute_sem_stats_generic(
    df: pd.DataFrame, ind_col: str, dep_col: str, sem_column: str
) -> tuple[list[float], list[float]] | None:
    """Helper to compute mean ± SEM values for a dataframe.
    
    Args:
        df: DataFrame to process
        ind_col: Independent column (group by this)
        dep_col: Dependent column (compute mean and SEM on this)
        sem_column: Column to group by for SEM computation
    
    Returns (lower_bounds, upper_bounds) where lower = mean - SEM
    and upper = mean + SEM for each independent value.
    """
    grouped = df.groupby([sem_column, ind_col], as_index=False)[dep_col].mean()
    stats = grouped.groupby(ind_col)[dep_col].agg(['mean', 'sem']).reset_index()
    
    if stats.empty:
        return None
    
    means = stats['mean'].values
    sems = stats['sem'].fillna(0).values  # Fill NaN SEM with 0
    
    lower_bounds = (means - sems).tolist()
    upper_bounds = (means + sems).tolist()
    
    return (lower_bounds, upper_bounds)


def _compute_precomputed_sem_stats_generic(
    df: pd.DataFrame, ind_col: str, dep_col: str, sem_column: str
) -> tuple[list[float], list[float]] | None:
    """Helper to compute mean ± pre-computed SEM values for a dataframe.
    
    Args:
        df: DataFrame to process
        ind_col: Independent column (group by this)
        dep_col: Dependent column (compute mean on this)
        sem_column: Column containing pre-computed SEM values
    
    Averages dependent and SEM values if multiple rows exist for the same independent value.
    Returns (lower_bounds, upper_bounds) where lower = mean - SEM
    and upper = mean + SEM for each independent value.
    """
    # Aggregate by independent column: mean of dependent and mean of sem
    agg_df = df.groupby(ind_col, as_index=False).agg({
        dep_col: 'mean',
        sem_column: 'mean'
    })
    
    if agg_df.empty:
        return None
    
    means = agg_df[dep_col].values
    sems = agg_df[sem_column].fillna(0).values  # Fill NaN SEM with 0
    
    lower_bounds = (means - sems).tolist()
    upper_bounds = (means + sems).tolist()
    
    return (lower_bounds, upper_bounds)


