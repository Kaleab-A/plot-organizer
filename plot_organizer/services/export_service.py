from __future__ import annotations

from typing import Iterable, Optional, TYPE_CHECKING

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for export
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import pandas as pd
from matplotlib.ticker import AutoMinorLocator

if TYPE_CHECKING:
    from plot_organizer.ui.grid_board import GridBoard, PlotTile


def export_grid(
    grid_board: "GridBoard",
    out_path: str,
    fmt: str = "pdf",
    width_in: float = 11.0,
    height_in: float = 8.5,
    dpi: int = 150,
) -> None:
    """Export the entire grid layout to a file.
    
    Creates a new matplotlib figure with GridSpec matching the grid layout,
    then re-renders each plot into its corresponding subplot.
    """
    rows = grid_board._rows
    cols = grid_board._cols
    
    # Create figure with GridSpec
    fig = plt.figure(figsize=(width_in, height_in))
    gs = GridSpec(rows, cols, figure=fig, hspace=0.3, wspace=0.3)
    
    # Track which cells have been processed (for spanning plots)
    processed = set()
    
    # Render each plot
    for r in range(rows):
        for c in range(cols):
            if (r, c) in processed:
                continue
            
            tile = grid_board.tile_at(r, c)
            if tile is None or tile.is_empty():
                continue
            
            # Get position and span
            pos = grid_board.find_tile_position(tile)
            if pos is None:
                continue
            
            tile_row, tile_col, rowspan, colspan = pos
            
            # Mark cells as processed
            for dr in range(rowspan):
                for dc in range(colspan):
                    processed.add((tile_row + dr, tile_col + dc))
            
            # Skip if not at the starting position
            if (r, c) != (tile_row, tile_col):
                continue
            
            # Create subplot with span
            ax = fig.add_subplot(gs[tile_row:tile_row+rowspan, tile_col:tile_col+colspan])
            
            # Re-render the plot
            _render_plot_to_ax(tile, ax)
    
    # Save figure
    fig.savefig(out_path, format=fmt, dpi=dpi, bbox_inches='tight')
    plt.close(fig)


def _render_plot_to_ax(tile: "PlotTile", ax) -> None:
    """Render a PlotTile's data to a matplotlib axis."""
    import numpy as np
    
    if tile._df is None:
        return
    
    df = tile._df
    x, y, hue = tile._x, tile._y, tile._hue
    sem_column = tile._sem_column
    sem_precomputed = tile._sem_precomputed
    filter_query = tile._filter_query
    style_line = tile._style_line
    style_marker = tile._style_marker
    
    # Get format string for plotting
    if style_line and style_marker:
        fmt = '-o'  # Line with markers
    elif style_marker:
        fmt = 'o'   # Markers only
    else:
        fmt = '-'   # Line only (default)
    
    # Apply filter if present
    plot_df = df
    if filter_query:
        for col, val in filter_query.items():
            plot_df = plot_df[plot_df[col] == val]
    
    # Helper function to plot with SEM (same logic as PlotTile._plot_with_sem)
    def plot_with_sem(data, label=None):
        if sem_column and sem_column in data.columns:
            if sem_precomputed:
                # Pre-computed SEM: aggregate by x
                agg_data = data.groupby(x, as_index=False).agg({
                    y: 'mean',
                    sem_column: 'mean'
                })
                
                line = ax.plot(agg_data[x], agg_data[y], fmt, label=label)[0]
                
                if agg_data[sem_column].notna().any():
                    color = line.get_color()
                    ax.fill_between(
                        agg_data[x],
                        agg_data[y] - agg_data[sem_column],
                        agg_data[y] + agg_data[sem_column],
                        alpha=0.2,
                        color=color
                    )
            else:
                # Computed SEM: group by sem_column first, then by x
                grouped = data.groupby([sem_column, x], as_index=False)[y].mean()
                # Compute mean and SEM across sem_column groups
                stats = grouped.groupby(x)[y].agg(['mean', 'sem']).reset_index()
                stats.columns = [x, 'mean_y', 'sem_y']
                
                line = ax.plot(stats[x], stats['mean_y'], fmt, label=label)[0]
                
                if stats['sem_y'].notna().any():
                    color = line.get_color()
                    ax.fill_between(
                        stats[x],
                        stats['mean_y'] - stats['sem_y'],
                        stats['mean_y'] + stats['sem_y'],
                        alpha=0.2,
                        color=color
                    )
        else:
            agg_data = data.groupby(x, as_index=False)[y].mean()
            ax.plot(agg_data[x], agg_data[y], fmt, label=label)
    
    # Apply aggregation with SEM
    if hue:
        for key, sub in plot_df.groupby(hue):
            plot_with_sem(sub, label=str(key))
        ax.legend(loc="best", fontsize='small')
    else:
        plot_with_sem(plot_df)
    
    # Get title from the tile's figure if it has one
    if tile.figure.axes:
        orig_ax = tile.figure.axes[0]
        if orig_ax.get_title():
            ax.set_title(orig_ax.get_title(), fontsize='small', pad=2)
    
    ax.set_xlabel(x, fontsize='small')
    ax.set_ylabel(y, fontsize='small')
    ax.tick_params(labelsize='small')

    # Add minor x-ticks for a finer grid without extra labels (match UI)
    ax.xaxis.set_minor_locator(AutoMinorLocator(5))  # 5 minor ticks between majors
    ax.tick_params(axis='x', which='minor', length=3, labelbottom=False)
    
    # Apply stored y-limits if present
    if tile._ylim is not None:
        ax.set_ylim(tile._ylim)
    
    # Draw reference lines
    for yval in tile._hlines:
        ax.axhline(y=yval, color='black', linestyle='--', linewidth=1, alpha=0.7, zorder=1)
    
    for xval in tile._vlines:
        ax.axvline(x=xval, color='black', linestyle='--', linewidth=1, alpha=0.7, zorder=1)

    # Draw error markers (if any), using the same semantics as PlotTile._render_error_markers
    _render_error_markers_to_ax(tile, ax)


def _render_error_markers_to_ax(tile: "PlotTile", ax) -> None:
    """Render error bar markers from a PlotTile onto the given axis.
    
    Mirrors the behaviour of PlotTile._render_error_markers for exports.
    """
    # Some older tiles may not have this attribute; fail gracefully
    error_markers = getattr(tile, "_error_markers", None)
    if not error_markers:
        return

    # Get current axis limits for auto-positioning
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    x_range = xlim[1] - xlim[0]
    y_range = ylim[1] - ylim[0]

    # Track markers for stacking
    x_markers: list[dict] = []  # Markers with xerr (stacked vertically)
    y_markers: list[dict] = []  # Markers with yerr (stacked horizontally)

    for marker in error_markers:
        if marker.get("xerr") is not None:
            x_markers.append(marker)
        elif marker.get("yerr") is not None:
            y_markers.append(marker)

    # Render x-error markers (horizontal error bars)
    for i, marker in enumerate(x_markers):
        x_val = marker.get("x")
        y_val = marker.get("y")
        xerr = marker.get("xerr")
        color = marker.get("color", "red")
        label = marker.get("label")
        marker_shape = marker.get("marker", "v")  # Default to triangle down

        # Auto-compute y position if not provided (stack from top)
        if y_val is None:
            y_val = ylim[1] - (0.05 + i * 0.08) * y_range

        ax.errorbar(
            x=x_val,
            y=y_val,
            xerr=xerr,
            fmt=marker_shape,
            color=color,
            capsize=3.5,
            markersize=8,
            label=label,
            zorder=10,  # Render on top
        )

    # Render y-error markers (vertical error bars)
    for i, marker in enumerate(y_markers):
        x_val = marker.get("x")
        y_val = marker.get("y")
        yerr = marker.get("yerr")
        color = marker.get("color", "red")
        label = marker.get("label")
        marker_shape = marker.get("marker", "v")  # Default to triangle down

        # Auto-compute x position if not provided (stack from right)
        if x_val is None:
            x_val = xlim[1] - (0.05 + i * 0.08) * x_range

        ax.errorbar(
            x=x_val,
            y=y_val,
            yerr=yerr,
            fmt=marker_shape,
            color=color,
            capsize=3.5,
            markersize=8,
            label=label,
            zorder=10,  # Render on top
        )


def export_single(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str],
    title: Optional[str],
    out_path: str,
    fmt: str = "png",
    width_in: float = 4.0,
    height_in: float = 3.0,
    dpi: int = 150,
) -> None:
    """Export a single plot to a file."""
    fig, ax = plt.subplots(figsize=(width_in, height_in))
    
    if hue:
        for key, sub in df.groupby(hue):
            agg_sub = sub.groupby(x, as_index=False)[y].mean()
            ax.plot(agg_sub[x], agg_sub[y], label=str(key))
        ax.legend(loc="best")
    else:
        agg_df = df.groupby(x, as_index=False)[y].mean()
        ax.plot(agg_df[x], agg_df[y])
    
    if title:
        ax.set_title(title)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    
    fig.savefig(out_path, format=fmt, dpi=dpi, bbox_inches='tight')
    plt.close(fig)


