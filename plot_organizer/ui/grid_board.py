from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QFrame,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd


class PlotTile(QFrame):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("PlotTile")
        self._df: Optional[pd.DataFrame] = None
        self._x: Optional[str] = None
        self._y: Optional[str] = None
        self._hue: Optional[str] = None
        self._filter_query: Optional[dict] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        self.figure = Figure(figsize=(4, 3), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def is_empty(self) -> bool:
        return self._df is None

    def set_plot(
        self, 
        df: pd.DataFrame, 
        x: str, 
        y: str, 
        hue: Optional[str] = None, 
        title: Optional[str] = None,
        filter_query: Optional[dict] = None,
        xlim: Optional[tuple[float, float]] = None,
        ylim: Optional[tuple[float, float]] = None,
    ) -> None:
        self._df, self._x, self._y, self._hue = df, x, y, hue
        self._filter_query = filter_query
        
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
            for key, sub in plot_df.groupby(hue):
                ax.plot(sub[x], sub[y], label=str(key))
            ax.legend(loc="best", fontsize='small')
        else:
            ax.plot(plot_df[x], plot_df[y])
        
        if title:
            ax.set_title(title, fontsize='small', pad=2)
        ax.set_xlabel(x, fontsize='small')
        ax.set_ylabel(y, fontsize='small')
        ax.tick_params(labelsize='small')
        
        if xlim:
            ax.set_xlim(xlim)
        if ylim:
            ax.set_ylim(ylim)
        
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

    def tile_at(self, r: int, c: int) -> PlotTile:
        w = self._grid.itemAtPosition(r, c).widget()
        assert isinstance(w, PlotTile)
        return w


