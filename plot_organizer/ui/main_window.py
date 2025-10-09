from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel

from plot_organizer.ui.grid_board import GridBoard


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Plot Organizer")

        self._init_menu()

        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(6, 6, 6, 6)
        self.grid_board = GridBoard(rows=2, cols=3, parent=central)
        layout.addWidget(self.grid_board)
        self.setCentralWidget(central)

    def _init_menu(self) -> None:
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        grid_menu = menubar.addMenu("Grid")
        add_row = QAction("+ Row", self)
        add_col = QAction("+ Col", self)
        add_row.triggered.connect(lambda: self.grid_board.add_row())
        add_col.triggered.connect(lambda: self.grid_board.add_col())
        grid_menu.addAction(add_row)
        grid_menu.addAction(add_col)


