from __future__ import annotations

from typing import Iterable, Optional, TYPE_CHECKING

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for export
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import pandas as pd

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
    if tile._df is None:
        return
    
    df = tile._df
    x, y, hue = tile._x, tile._y, tile._hue
    filter_query = tile._filter_query
    
    # Apply filter if present
    plot_df = df
    if filter_query:
        for col, val in filter_query.items():
            plot_df = plot_df[plot_df[col] == val]
    
    # Apply aggregation (same as in PlotTile.set_plot)
    if hue:
        for key, sub in plot_df.groupby(hue):
            agg_sub = sub.groupby(x, as_index=False)[y].mean()
            ax.plot(agg_sub[x], agg_sub[y], label=str(key))
        ax.legend(loc="best", fontsize='small')
    else:
        agg_df = plot_df.groupby(x, as_index=False)[y].mean()
        ax.plot(agg_df[x], agg_df[y])
    
    # Get title from the tile's figure if it has one
    if tile.figure.axes:
        orig_ax = tile.figure.axes[0]
        if orig_ax.get_title():
            ax.set_title(orig_ax.get_title(), fontsize='small', pad=2)
    
    ax.set_xlabel(x, fontsize='small')
    ax.set_ylabel(y, fontsize='small')
    ax.tick_params(labelsize='small')


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


