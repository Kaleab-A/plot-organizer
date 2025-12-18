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
from matplotlib.ticker import AutoMinorLocator


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
        self._hue: Optional[str | list[str]] = None
        self._sem_column: Optional[str] = None
        self._sem_precomputed: bool = False
        self._filter_query: Optional[dict] = None
        self._hlines: list[float] = []
        self._vlines: list[float] = []
        self._style_line: bool = True
        self._style_marker: bool = False
        self._ylim: Optional[tuple[float, float]] = None
        self._xlim: Optional[tuple[float, float]] = None
        self._error_markers: list[dict] = []
        self._flip_axes: bool = False  # When True, Y is independent, X is dependent
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
            # Add error markers option
            markers_action = QAction("Manage Error Markers...", self)
            markers_action.triggered.connect(self._open_markers_dialog)
            menu.addAction(markers_action)
            
            clear_action = QAction("Clear Plot", self)
            clear_action.triggered.connect(lambda: self.clear_requested.emit(self))
            menu.addAction(clear_action)
        
        menu.exec(event.globalPos())

    def set_plot(
        self, 
        df: pd.DataFrame, 
        x: str, 
        y: str, 
        hue: Optional[str | list[str]] = None,
        sem_column: Optional[str] = None,
        sem_precomputed: bool = False,
        title: Optional[str] = None,
        filter_query: Optional[dict] = None,
        xlim: Optional[tuple[float, float]] = None,
        ylim: Optional[tuple[float, float]] = None,
        hlines: Optional[list[float]] = None,
        vlines: Optional[list[float]] = None,
        style_line: bool = True,
        style_marker: bool = False,
        error_markers: Optional[list[dict]] = None,
        flip_axes: bool = False,
    ) -> None:
        self._df, self._x, self._y, self._hue = df, x, y, hue
        self._sem_column = sem_column
        self._sem_precomputed = sem_precomputed
        self._filter_query = filter_query
        self._hlines = hlines or []
        self._vlines = vlines or []
        self._style_line = style_line
        self._style_marker = style_marker
        self._ylim = ylim  # Store y-limits for export
        self._xlim = xlim  # Store x-limits for export
        self._error_markers = error_markers or []
        self._flip_axes = flip_axes  # When True, Y is independent, X is dependent
        
        # Apply filter if provided
        plot_df = df.copy()  # Make a copy to avoid modifying original
        if filter_query:
            for col, val in filter_query.items():
                plot_df = plot_df[plot_df[col] == val]
        
        # Create composite hue column if hue is a list of columns
        actual_hue = None
        if hue:
            if isinstance(hue, list) and len(hue) > 0:
                # Create composite column with format: Col1=val1, Col2=val2
                composite_name = "__composite_hue__"
                plot_df[composite_name] = plot_df.apply(
                    lambda row: ", ".join(f"{col}={row[col]}" for col in hue),
                    axis=1
                )
                actual_hue = composite_name
            elif isinstance(hue, str):
                # Single string hue (backward compatibility)
                actual_hue = hue
            # else: hue is empty list or None, actual_hue stays None
        
        # Reuse existing axes if available, otherwise create new one
        if self.figure.axes:
            ax = self.figure.axes[0]
            ax.clear()
        else:
            ax = self.figure.subplots()
        
        if plot_df.empty:
            ax.text(0.5, 0.5, "No data", ha='center', va='center', transform=ax.transAxes, alpha=0.3)
        elif actual_hue:
            # Group by hue and aggregate
            for key, sub in plot_df.groupby(actual_hue):
                self._plot_with_sem(ax, sub, x, y, sem_column, label=str(key))
            ax.legend(loc="best", fontsize='small')
        else:
            # No hue: aggregate duplicate values along independent axis
            self._plot_with_sem(ax, plot_df, x, y, sem_column)
        
        if title:
            ax.set_title(title, fontsize='small', pad=2)
        ax.set_xlabel(x, fontsize='small')
        ax.set_ylabel(y, fontsize='small')
        ax.tick_params(labelsize='small')

        # Add minor ticks for a finer grid without extra labels
        if self._flip_axes:
            # When flipped, Y is independent - add minor y-ticks
            ax.yaxis.set_minor_locator(AutoMinorLocator(5))
            ax.tick_params(axis='y', which='minor', length=3, labelleft=False)
        else:
            # Standard: X is independent - add minor x-ticks
            ax.xaxis.set_minor_locator(AutoMinorLocator(5))
            ax.tick_params(axis='x', which='minor', length=3, labelbottom=False)
        
        if xlim:
            ax.set_xlim(xlim)
        if ylim:
            ax.set_ylim(ylim)
        
        # Draw reference lines
        for yval in self._hlines:
            ax.axhline(y=yval, color='black', linestyle='--', linewidth=1, alpha=0.7, zorder=1)
        
        for xval in self._vlines:
            ax.axvline(x=xval, color='black', linestyle='--', linewidth=1, alpha=0.7, zorder=1)
        
        # Draw error markers
        self._render_error_markers(ax, plot_df)
        
        self.canvas.draw_idle()
    
    def _get_plot_format(self) -> str:
        """Get the format string for plot() based on style settings."""
        if self._style_line and self._style_marker:
            return '-o'  # Line with markers
        elif self._style_marker:
            return 'o'   # Markers only
        else:
            return '-'   # Line only (default)
    
    def _plot_with_sem(self, ax, df: pd.DataFrame, x: str, y: str, sem_column: Optional[str], label: Optional[str] = None) -> None:
        """Plot data with optional SEM shaded region.
        
        If sem_column is provided:
        - If pre-computed mode: Use SEM values directly from the column
        - If computed mode: Group by sem_column, compute mean and SEM
        
        When flip_axes is True:
        - Y is the independent variable (what we group by)
        - X is the dependent variable (what we compute mean/SEM of)
        - SEM bands are horizontal (using fill_betweenx)
        """
        import numpy as np
        
        # Determine independent and dependent axes based on flip_axes
        if self._flip_axes:
            ind_col, dep_col = y, x  # Y is independent, X is dependent
        else:
            ind_col, dep_col = x, y  # X is independent, Y is dependent
        
        if sem_column and sem_column in df.columns:
            if self._sem_precomputed:
                # Pre-computed SEM mode: use values from column
                self._plot_with_precomputed_sem(ax, df, x, y, sem_column, label)
            else:
                # Computed SEM mode
                # Step 1: Group by sem_column, then by independent axis, compute mean of dependent
                grouped = df.groupby([sem_column, ind_col], as_index=False)[dep_col].mean()
                
                # Step 2: For each ind_col value, compute mean and SEM across sem_column groups
                stats = grouped.groupby(ind_col)[dep_col].agg(['mean', 'sem']).reset_index()
                stats.columns = [ind_col, 'mean_dep', 'sem_dep']
                
                # Choose between error bars (markers only) or shaded region (with line)
                if self._should_use_error_bars():
                    # Use error bars for each point
                    import matplotlib.pyplot as plt
                    color = plt.rcParams['axes.prop_cycle'].by_key()['color'][0]
                    if label:
                        # Get next color from cycle for different hue groups
                        ax_colors = [line.get_color() for line in ax.lines]
                        color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
                        color = color_cycle[len(ax_colors) % len(color_cycle)]
                    self._plot_error_bars(ax, stats[ind_col].values, stats['mean_dep'].values,
                                         stats['sem_dep'].fillna(0).values, color, label)
                else:
                    # Plot mean line with style
                    fmt = self._get_plot_format()
                    line = self._plot_line(ax, stats[ind_col], stats['mean_dep'], fmt, label)
                    
                    # Plot SEM as shaded region
                    if stats['sem_dep'].notna().any():
                        color = line.get_color()
                        self._fill_sem(ax, stats[ind_col], 
                                       stats['mean_dep'] - stats['sem_dep'],
                                       stats['mean_dep'] + stats['sem_dep'],
                                       color)
        else:
            # No SEM: just aggregate by independent axis and plot mean
            agg_df = df.groupby(ind_col, as_index=False)[dep_col].mean()
            fmt = self._get_plot_format()
            self._plot_line(ax, agg_df[ind_col], agg_df[dep_col], fmt, label)
    
    def _plot_line(self, ax, ind_data, dep_data, fmt: str, label: Optional[str] = None):
        """Plot line with coordinates based on flip_axes setting.
        
        Returns the Line2D object for color extraction.
        """
        if self._flip_axes:
            # X is dependent, Y is independent
            return ax.plot(dep_data, ind_data, fmt, label=label)[0]
        else:
            # X is independent, Y is dependent (standard)
            return ax.plot(ind_data, dep_data, fmt, label=label)[0]
    
    def _fill_sem(self, ax, ind_vals, lower, upper, color) -> None:
        """Fill SEM region based on flip_axes setting."""
        if self._flip_axes:
            # Horizontal bands: X varies, Y is fixed
            ax.fill_betweenx(ind_vals, lower, upper, alpha=0.2, color=color)
        else:
            # Vertical bands: Y varies, X is fixed
            ax.fill_between(ind_vals, lower, upper, alpha=0.2, color=color)
    
    def _should_use_error_bars(self) -> bool:
        """Determine if error bars should be used instead of shaded region.
        
        Returns True when markers only (no line) is selected.
        """
        return self._style_marker and not self._style_line
    
    def _plot_error_bars(self, ax, ind_vals, dep_vals, sem_vals, color, label: Optional[str] = None) -> None:
        """Plot error bars for each data point based on flip_axes setting.
        
        Used when markers only (no line) is selected.
        """
        if self._flip_axes:
            # X is dependent (with error), Y is independent
            ax.errorbar(
                dep_vals, ind_vals, xerr=sem_vals,
                fmt='o', color=color, capsize=3, markersize=6,
                label=label, elinewidth=1.5
            )
        else:
            # Y is dependent (with error), X is independent
            ax.errorbar(
                ind_vals, dep_vals, yerr=sem_vals,
                fmt='o', color=color, capsize=3, markersize=6,
                label=label, elinewidth=1.5
            )
    
    def _plot_with_precomputed_sem(self, ax, df: pd.DataFrame, x: str, y: str, sem_column: str, label: Optional[str] = None) -> None:
        """Plot data with pre-computed SEM values from a column.
        
        If multiple rows exist for same independent axis value:
        - Average dependent values
        - Average SEM values
        - Show warning to user
        
        When flip_axes is True:
        - Y is the independent variable
        - X is the dependent variable with SEM
        """
        import numpy as np
        import logging
        
        # Determine independent and dependent axes based on flip_axes
        if self._flip_axes:
            ind_col, dep_col = y, x  # Y is independent, X is dependent
        else:
            ind_col, dep_col = x, y  # X is independent, Y is dependent
        
        # Check for duplicates
        dup_check = df.groupby(ind_col).size()
        has_duplicates = (dup_check > 1).any()
        
        # Aggregate by independent column: mean of dependent and mean of sem
        agg_df = df.groupby(ind_col, as_index=False).agg({
            dep_col: 'mean',
            sem_column: 'mean'
        })
        
        # Warning if duplicates were averaged
        if has_duplicates:
            logging.warning(
                f"Multiple rows found for some {ind_col}-values. "
                f"Averaged {dep_col}-values and SEM values for plotting. "
                f"Consider pre-aggregating your data."
            )
        
        # Choose between error bars (markers only) or shaded region (with line)
        if self._should_use_error_bars():
            # Use error bars for each point
            import matplotlib.pyplot as plt
            color = plt.rcParams['axes.prop_cycle'].by_key()['color'][0]
            if label:
                # Get next color from cycle for different hue groups
                ax_colors = [line.get_color() for line in ax.lines]
                color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
                color = color_cycle[len(ax_colors) % len(color_cycle)]
            self._plot_error_bars(ax, agg_df[ind_col].values, agg_df[dep_col].values,
                                 agg_df[sem_column].fillna(0).values, color, label)
        else:
            # Plot mean line with style
            fmt = self._get_plot_format()
            line = self._plot_line(ax, agg_df[ind_col], agg_df[dep_col], fmt, label)
            
            # Plot SEM as shaded region
            if agg_df[sem_column].notna().any():
                color = line.get_color()
                self._fill_sem(ax, agg_df[ind_col],
                              agg_df[dep_col] - agg_df[sem_column],
                              agg_df[dep_col] + agg_df[sem_column],
                              color)
    
    def _render_error_markers(self, ax, plot_df: pd.DataFrame) -> None:
        """Render error bar markers on the plot.
        
        Auto-computes missing x or y positions and stacks multiple markers.
        Each marker dict can have: x, y, xerr, yerr, color, label
        
        When flip_axes is True:
        - xerr markers (horizontal error bars) represent error on the dependent axis (X)
          and stack along the independent axis (Y) - stacking is from the right of X
        - yerr markers (vertical error bars) represent error on the independent axis (Y)
          and stack along the dependent axis (X) - stacking is from the top of Y
        """
        if not self._error_markers:
            return
        
        import numpy as np
        
        # Get current axis limits for auto-positioning
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]
        
        # Track markers for stacking
        x_markers = []  # Markers with xerr (horizontal error bars)
        y_markers = []  # Markers with yerr (vertical error bars)
        
        for marker in self._error_markers:
            if marker.get('xerr') is not None:
                x_markers.append(marker)
            elif marker.get('yerr') is not None:
                y_markers.append(marker)
        
        # Render x-error markers (horizontal error bars)
        # When flip_axes=False: xerr is error on independent axis (unusual), stack from top (Y)
        # When flip_axes=True: xerr is error on dependent axis (X), stack from right (X)
        for i, marker in enumerate(x_markers):
            x_val = marker.get('x')
            y_val = marker.get('y')
            xerr = marker.get('xerr')
            color = marker.get('color', 'red')
            label = marker.get('label')
            marker_shape = marker.get('marker', 'v')  # Default to triangle down
            
            if self._flip_axes:
                # xerr is error on X (dependent axis), stack horizontally from right
                if x_val is not None:
                    if isinstance(x_val, (int, float)) and x_val >= 0 and x_val == int(x_val):
                        x_val = xlim[1] - (0.05 + int(x_val) * 0.08) * x_range
                    else:
                        continue
                else:
                    x_val = xlim[1] - (0.05 + i * 0.08) * x_range
            else:
                # Standard: xerr stacks vertically from top
                if y_val is not None:
                    if isinstance(y_val, (int, float)) and y_val >= 0 and y_val == int(y_val):
                        y_val = ylim[1] - (0.05 + int(y_val) * 0.08) * y_range
                    else:
                        continue
                else:
                    y_val = ylim[1] - (0.05 + i * 0.08) * y_range
            
            ax.errorbar(
                x=x_val,
                y=y_val,
                xerr=xerr,
                fmt=marker_shape,
                color=color,
                capsize=3.5,
                markersize=8,
                fillstyle='none',  # Hollow markers (no fill)
                label=label,
                zorder=10  # Render on top
            )
        
        # Render y-error markers (vertical error bars)
        # When flip_axes=False: yerr is error on dependent axis (Y), stack from right (X)
        # When flip_axes=True: yerr is error on independent axis (unusual), stack from top (Y)
        for i, marker in enumerate(y_markers):
            x_val = marker.get('x')
            y_val = marker.get('y')
            yerr = marker.get('yerr')
            color = marker.get('color', 'red')
            label = marker.get('label')
            marker_shape = marker.get('marker', 'v')  # Default to triangle down
            
            if self._flip_axes:
                # yerr stacks vertically from top (along Y, the independent axis)
                if y_val is not None:
                    if isinstance(y_val, (int, float)) and y_val >= 0 and y_val == int(y_val):
                        y_val = ylim[1] - (0.05 + int(y_val) * 0.08) * y_range
                    else:
                        continue
                else:
                    y_val = ylim[1] - (0.05 + i * 0.08) * y_range
            else:
                # Standard: yerr stacks horizontally from right
                if x_val is not None:
                    if isinstance(x_val, (int, float)) and x_val >= 0 and x_val == int(x_val):
                        x_val = xlim[1] - (0.05 + int(x_val) * 0.08) * x_range
                    else:
                        continue
                else:
                    x_val = xlim[1] - (0.05 + i * 0.08) * x_range
            
            ax.errorbar(
                x=x_val,
                y=y_val,
                yerr=yerr,
                fmt=marker_shape,
                color=color,
                capsize=3.5,
                markersize=8,
                fillstyle='none',  # Hollow markers (no fill)
                label=label,
                zorder=10  # Render on top
            )
    
    def _open_markers_dialog(self) -> None:
        """Open dialog to manage error markers."""
        from plot_organizer.ui.dialogs import ErrorMarkersManagerDialog
        
        dialog = ErrorMarkersManagerDialog(self, markers=self._error_markers)
        dialog.exec()
        updated_markers = dialog.get_markers()
        
        if updated_markers is not None:
            # Update markers and refresh plot
            self._error_markers = updated_markers
            # Re-render the plot with updated markers
            if self._df is not None and self._x and self._y:
                # Preserve the current title
                title = None
                if self.figure.axes:
                    title = self.figure.axes[0].get_title() or None
                
                self.set_plot(
                    df=self._df,
                    x=self._x,
                    y=self._y,
                    hue=self._hue,
                    sem_column=self._sem_column,
                    sem_precomputed=self._sem_precomputed,
                    title=title,
                    filter_query=self._filter_query,
                    hlines=self._hlines,
                    vlines=self._vlines,
                    style_line=self._style_line,
                    style_marker=self._style_marker,
                    xlim=self._xlim,
                    ylim=self._ylim,
                    error_markers=self._error_markers,
                    flip_axes=self._flip_axes,
                )
    
    def clear_plot(self) -> None:
        """Clear the plot data and reset to empty state."""
        self._df = None
        self._x = None
        self._y = None
        self._hue = None
        self._sem_column = None
        self._sem_precomputed = False
        self._filter_query = None
        self._hlines = []
        self._vlines = []
        self._style_line = True
        self._style_marker = False
        self._ylim = None
        self._xlim = None
        self._error_markers = []
        self._flip_axes = False
        self.figure.clear()
        self.canvas.draw_idle()
    
    def get_plot_data(self, datasource_id: Optional[str] = None) -> Optional[dict]:
        """Extract plot parameters for serialization.
        
        Args:
            datasource_id: ID of the datasource (required for saving)
        
        Returns:
            Dict of plot parameters or None if tile is empty
        """
        if self.is_empty():
            return None
        
        # Get title from figure if it exists
        title = None
        if self.figure.axes:
            title = self.figure.axes[0].get_title() or None
        
        return {
            "datasource_id": datasource_id,
            "x": self._x,
            "y": self._y,
            "hue": self._hue,  # Can be None, str, or list[str]
            "sem_column": self._sem_column,
            "sem_precomputed": self._sem_precomputed,
            "filter_query": self._filter_query,
            "hlines": self._hlines,
            "vlines": self._vlines,
            "style_line": self._style_line,
            "style_marker": self._style_marker,
            "ylim": list(self._ylim) if self._ylim else None,  # Convert tuple to list for JSON
            "xlim": list(self._xlim) if self._xlim else None,  # Convert tuple to list for JSON
            "title": title,
            "error_markers": self._error_markers,
            "flip_axes": self._flip_axes,
        }
    
    def set_plot_from_data(self, df: pd.DataFrame, plot_data: dict) -> None:
        """Reconstruct plot from serialized data.
        
        Args:
            df: DataFrame to plot (from datasource)
            plot_data: Dict of plot parameters from get_plot_data()
        """
        # Convert ylim back to tuple if present
        ylim = plot_data.get("ylim")
        if ylim and isinstance(ylim, list) and len(ylim) == 2:
            ylim = tuple(ylim)
        
        # Convert xlim back to tuple if present
        xlim = plot_data.get("xlim")
        if xlim and isinstance(xlim, list) and len(xlim) == 2:
            xlim = tuple(xlim)
        
        self.set_plot(
            df=df,
            x=plot_data["x"],
            y=plot_data["y"],
            hue=plot_data.get("hue"),
            sem_column=plot_data.get("sem_column"),
            sem_precomputed=plot_data.get("sem_precomputed", False),
            title=plot_data.get("title"),
            filter_query=plot_data.get("filter_query"),
            xlim=xlim,
            ylim=ylim,
            hlines=plot_data.get("hlines", []),
            vlines=plot_data.get("vlines", []),
            style_line=plot_data.get("style_line", True),
            style_marker=plot_data.get("style_marker", False),
            error_markers=plot_data.get("error_markers", []),
            flip_axes=plot_data.get("flip_axes", False),
        )


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
    
    def reset_to_size(self, rows: int, cols: int) -> None:
        """Reset the grid to a specific size, removing all existing widgets."""
        # Remove all existing widgets
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item and item.widget():
                widget = item.widget()
                widget.deleteLater()
        
        # Update dimensions
        self._rows = rows
        self._cols = cols
        
        # Repopulate with fresh empty tiles
        self._populate()
    
    def serialize_layout(self, datasources: dict[str, object]) -> list[dict]:
        """Extract all non-empty plots with their grid positions.
        
        Args:
            datasources: Map from datasource ID to datasource object {id: ds}
        
        Returns:
            List of plot descriptors with grid_position and plot data
        """
        plots = []
        processed = set()
        
        for r in range(self._rows):
            for c in range(self._cols):
                if (r, c) in processed:
                    continue
                
                tile = self.tile_at(r, c)
                if tile is None or tile.is_empty():
                    continue
                
                # Get position and span
                pos = self.find_tile_position(tile)
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
                
                # Find datasource ID by matching dataframe
                datasource_id = None
                for ds_id, ds_obj in datasources.items():
                    if tile._df is ds_obj.dataframe:  # type: ignore
                        datasource_id = ds_id
                        break
                
                # Get plot data
                plot_data = tile.get_plot_data(datasource_id=datasource_id)
                if plot_data is None:
                    continue
                
                # Add grid position
                plot_descriptor = {
                    "grid_position": {
                        "row": tile_row,
                        "col": tile_col,
                        "rowspan": rowspan,
                        "colspan": colspan,
                    },
                    **plot_data,
                }
                plots.append(plot_descriptor)
        
        return plots


