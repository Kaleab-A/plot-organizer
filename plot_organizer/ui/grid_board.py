from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QFrame,
    QLabel,
    QVBoxLayout,
)


class PlotTile(QFrame):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("PlotTile")
        layout = QVBoxLayout(self)
        label = QLabel("Empty", self)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)


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


