from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QContextMenuEvent, QAction
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QFrame,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QMenu,
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd


class PlotTile(QFrame):
    settings_requested = Signal(object)  # Emits self
    clear_requested = Signal(object)  # Emits self
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("PlotTile")
        self._df: Optional[pd.DataFrame] = None
        self._x: Optional[str] = None
        self._y: Optional[str] = None
        self._hue: Optional[str] = None
        self._sem_column: Optional[str] = None
        self._filter_query: Optional[dict] = None
        self._hlines: list[float] = []
        self._vlines: list[float] = []
        self.setContextMenuPolicy(Qt.DefaultContextMenu)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        self.figure = Figure(figsize=(4, 3), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def is_empty(self) -> bool:
        return self._df is None
    
    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu = QMenu(self)
        settings_action = QAction("Plot Settings...", self)
        settings_action.triggered.connect(lambda: self.settings_requested.emit(self))
        menu.addAction(settings_action)
        
        if not self.is_empty():
            clear_action = QAction("Clear Plot", self)
            clear_action.triggered.connect(lambda: self.clear_requested.emit(self))
            menu.addAction(clear_action)
        
        menu.exec(event.globalPos())

    def set_plot(
        self, 
        df: pd.DataFrame, 
        x: str, 
        y: str, 
        hue: Optional[str] = None,
        sem_column: Optional[str] = None,
        title: Optional[str] = None,
        filter_query: Optional[dict] = None,
        xlim: Optional[tuple[float, float]] = None,
        ylim: Optional[tuple[float, float]] = None,
        hlines: Optional[list[float]] = None,
        vlines: Optional[list[float]] = None,
    ) -> None:
        self._df, self._x, self._y, self._hue = df, x, y, hue
        self._sem_column = sem_column
        self._filter_query = filter_query
        self._hlines = hlines or []
        self._vlines = vlines or []
        
        # Apply filter if provided
        plot_df = df
        if filter_query:
            for col, val in filter_query.items():
                plot_df = plot_df[plot_df[col] == val]
        
        ax = self.figure.subplots()
        ax.clear()
        
        if plot_df.empty:
            ax.text(0.5, 0.5, "No data", ha='center', va='center', transform=ax.transAxes, alpha=0.3)
        elif hue:
            # Group by hue and aggregate
            for key, sub in plot_df.groupby(hue):
                self._plot_with_sem(ax, sub, x, y, sem_column, label=str(key))
            ax.legend(loc="best", fontsize='small')
        else:
            # No hue: aggregate duplicate x values
            self._plot_with_sem(ax, plot_df, x, y, sem_column)
        
        if title:
            ax.set_title(title, fontsize='small', pad=2)
        ax.set_xlabel(x, fontsize='small')
        ax.set_ylabel(y, fontsize='small')
        ax.tick_params(labelsize='small')
        
        if xlim:
            ax.set_xlim(xlim)
        if ylim:
            ax.set_ylim(ylim)
        
        # Draw reference lines
        for yval in self._hlines:
            ax.axhline(y=yval, color='black', linestyle='--', linewidth=1, alpha=0.7, zorder=1)
        
        for xval in self._vlines:
            ax.axvline(x=xval, color='black', linestyle='--', linewidth=1, alpha=0.7, zorder=1)
        
        self.canvas.draw_idle()
    
    def _plot_with_sem(self, ax, df: pd.DataFrame, x: str, y: str, sem_column: Optional[str], label: Optional[str] = None) -> None:
        """Plot data with optional SEM shaded region.
        
        If sem_column is provided:
        1. Group by sem_column first
        2. Compute mean within each group
        3. Then aggregate across sem_column groups to get overall mean and SEM
        """
        import numpy as np
        
        if sem_column and sem_column in df.columns:
            # Step 1: Group by sem_column, then by x, compute mean of y
            grouped = df.groupby([sem_column, x], as_index=False)[y].mean()
            
            # Step 2: For each x, compute mean and SEM across sem_column groups
            stats = grouped.groupby(x)[y].agg(['mean', 'sem']).reset_index()
            stats.columns = [x, 'mean_y', 'sem_y']
            
            # Plot mean line
            line = ax.plot(stats[x], stats['mean_y'], label=label)[0]
            
            # Plot SEM as shaded region
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
            # No SEM: just aggregate by x and plot mean
            agg_df = df.groupby(x, as_index=False)[y].mean()
            ax.plot(agg_df[x], agg_df[y], label=label)
    
    def clear_plot(self) -> None:
        """Clear the plot data and reset to empty state."""
        self._df = None
        self._x = None
        self._y = None
        self._hue = None
        self._sem_column = None
        self._filter_query = None
        self._hlines = []
        self._vlines = []
        self.figure.clear()
        self.canvas.draw_idle()


class GridBoard(QWidget):
    def __init__(self, rows: int = 1, cols: int = 1, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._rows = rows
        self._cols = cols
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(6)
        self._populate()

    def _populate(self) -> None:
        for r in range(self._rows):
            for c in range(self._cols):
                self._grid.addWidget(PlotTile(self), r, c)

    def add_row(self) -> None:
        r = self._rows
        for c in range(self._cols):
            self._grid.addWidget(PlotTile(self), r, c)
        self._rows += 1

    def add_col(self) -> None:
        c = self._cols
        for r in range(self._rows):
            self._grid.addWidget(PlotTile(self), r, c)
        self._cols += 1

    def first_empty_coord(self) -> Optional[tuple[int, int]]:
        for r in range(self._rows):
            for c in range(self._cols):
                tile = self._grid.itemAtPosition(r, c).widget()
                if isinstance(tile, PlotTile) and tile.is_empty():
                    return (r, c)
        return None

    def tile_at(self, r: int, c: int) -> Optional[PlotTile]:
        item = self._grid.itemAtPosition(r, c)
        if item is None:
            return None
        w = item.widget()
        if isinstance(w, PlotTile):
            return w
        return None
    
    def remove_row(self, row: int) -> bool:
        """Remove a row from the grid. Returns False if row contains non-empty plots."""
        if row < 0 or row >= self._rows:
            return False
        
        # Check if row has any non-empty plots
        for c in range(self._cols):
            tile = self.tile_at(row, c)
            if tile and not tile.is_empty():
                return False
        
        # Remove widgets in this row
        for c in range(self._cols):
            item = self._grid.itemAtPosition(row, c)
            if item:
                widget = item.widget()
                if widget:
                    self._grid.removeWidget(widget)
                    widget.deleteLater()
        
        # Shift rows up
        for r in range(row + 1, self._rows):
            for c in range(self._cols):
                item = self._grid.itemAtPosition(r, c)
                if item:
                    widget = item.widget()
                    if widget:
                        self._grid.removeWidget(widget)
                        self._grid.addWidget(widget, r - 1, c)
        
        self._rows -= 1
        return True
    
    def remove_col(self, col: int) -> bool:
        """Remove a column from the grid. Returns False if column contains non-empty plots."""
        if col < 0 or col >= self._cols:
            return False
        
        # Check if column has any non-empty plots
        for r in range(self._rows):
            tile = self.tile_at(r, col)
            if tile and not tile.is_empty():
                return False
        
        # Remove widgets in this column
        for r in range(self._rows):
            item = self._grid.itemAtPosition(r, col)
            if item:
                widget = item.widget()
                if widget:
                    self._grid.removeWidget(widget)
                    widget.deleteLater()
        
        # Shift columns left
        for c in range(col + 1, self._cols):
            for r in range(self._rows):
                item = self._grid.itemAtPosition(r, c)
                if item:
                    widget = item.widget()
                    if widget:
                        self._grid.removeWidget(widget)
                        self._grid.addWidget(widget, r, c - 1)
        
        self._cols -= 1
        return True
    
    def move_plot(self, from_row: int, from_col: int, to_row: int, to_col: int, 
                  rowspan: int = 1, colspan: int = 1) -> None:
        """Move a plot to a new position with optional spanning."""
        # Ensure target area fits
        while to_row + rowspan > self._rows:
            self.add_row()
        while to_col + colspan > self._cols:
            self.add_col()
        
        # Get source tile
        source_tile = self.tile_at(from_row, from_col)
        if not source_tile:
            return
        
        # Remove from old position
        self._grid.removeWidget(source_tile)
        
        # Clear target cells if they have empty plots
        for r in range(to_row, to_row + rowspan):
            for c in range(to_col, to_col + colspan):
                if r == to_row and c == to_col:
                    continue  # Skip the main cell
                target_tile = self.tile_at(r, c)
                if target_tile and target_tile.is_empty():
                    self._grid.removeWidget(target_tile)
                    target_tile.deleteLater()
        
        # Add to new position with span
        self._grid.addWidget(source_tile, to_row, to_col, rowspan, colspan)
    
    def find_tile_position(self, tile: PlotTile) -> Optional[tuple[int, int, int, int]]:
        """Find the position and span of a tile. Returns (row, col, rowspan, colspan) or None."""
        for r in range(self._rows):
            for c in range(self._cols):
                item = self._grid.itemAtPosition(r, c)
                if item and item.widget() == tile:
                    # Get span info from layout
                    idx = self._grid.indexOf(tile)
                    if idx >= 0:
                        row, col, rowspan, colspan = self._grid.getItemPosition(idx)
                        return (row, col, rowspan, colspan)
        return None
    
    def swap_plots(self, tile1: PlotTile, tile2: PlotTile) -> tuple[bool, str]:
        """Swap two plots if they have matching spans.
        
        Returns (success, message) tuple.
        """
        pos1 = self.find_tile_position(tile1)
        pos2 = self.find_tile_position(tile2)
        
        if pos1 is None or pos2 is None:
            return False, "Could not find plot positions"
        
        row1, col1, rowspan1, colspan1 = pos1
        row2, col2, rowspan2, colspan2 = pos2
        
        # Check if spans match
        if rowspan1 != rowspan2 or colspan1 != colspan2:
            return False, (
                f"Cannot swap: Span mismatch.\n\n"
                f"Source: {rowspan1}×{colspan1} span\n"
                f"Target: {rowspan2}×{colspan2} span\n\n"
                f"Please make both plots 1×1 first, then swap."
            )
        
        # Remove both from grid
        self._grid.removeWidget(tile1)
        self._grid.removeWidget(tile2)
        
        # Add them back swapped
        self._grid.addWidget(tile1, row2, col2, rowspan2, colspan2)
        self._grid.addWidget(tile2, row1, col1, rowspan1, colspan1)
        
        return True, "Plots swapped successfully"


