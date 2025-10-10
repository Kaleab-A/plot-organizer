from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QFileDialog, QMessageBox, QDialog

from plot_organizer.ui.grid_board import GridBoard
from plot_organizer.ui.data_manager import DataManagerDock
from plot_organizer.ui.dialogs import QuickPlotDialog
from plot_organizer.services.load_service import load_csv_to_datasource
from plot_organizer.services.plot_service import expand_groups, shared_limits


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

        # state
        self._datasources: dict[str, object] = {}
        self._ds_names: dict[str, str] = {}
        self._ds_columns: dict[str, list[str]] = {}

        # docks
        self.data_manager = DataManagerDock(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.data_manager)
        self.data_manager.btn_add.clicked.connect(self._action_add_csv)
        self.data_manager.btn_remove.clicked.connect(self._action_remove_selected_ds)

    def _init_menu(self) -> None:
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        data_menu = menubar.addMenu("Data")
        add_csv = QAction("Add CSV…", self)
        add_csv.triggered.connect(self._action_add_csv)
        data_menu.addAction(add_csv)

        plot_menu = menubar.addMenu("Plot")
        quick_plot = QAction("Quick Plot…", self)
        quick_plot.triggered.connect(self._action_quick_plot)
        plot_menu.addAction(quick_plot)

        grid_menu = menubar.addMenu("Grid")
        add_row = QAction("+ Row", self)
        add_col = QAction("+ Col", self)
        add_row.triggered.connect(lambda: self.grid_board.add_row())
        add_col.triggered.connect(lambda: self.grid_board.add_col())
        grid_menu.addAction(add_row)
        grid_menu.addAction(add_col)

    # actions
    def _action_add_csv(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        try:
            ds = load_csv_to_datasource(path)
        except Exception as e:
            QMessageBox.critical(self, "Load Error", str(e))
            return
        self._datasources[ds.id] = ds
        self._ds_names[ds.id] = ds.name
        self._ds_columns[ds.id] = list(ds.dataframe.columns)
        self.data_manager.add_source(ds.id, ds.name)

    def _action_remove_selected_ds(self) -> None:
        ds_id = self.data_manager.remove_selected()
        if not ds_id:
            return
        self._datasources.pop(ds_id, None)
        self._ds_names.pop(ds_id, None)
        self._ds_columns.pop(ds_id, None)

    def _action_quick_plot(self) -> None:
        if not self._datasources:
            QMessageBox.information(self, "Quick Plot", "Please add a CSV first.")
            return
        dlg = QuickPlotDialog(self, ds_to_columns=self._ds_columns, ds_names=self._ds_names)
        if dlg.exec() != QDialog.Accepted:
            return
        sel = dlg.selection()
        if not sel:
            return
        ds = self._datasources.get(sel["datasource_id"])  # type: ignore[assignment]
        if ds is None:
            return
        
        df = ds.dataframe  # type: ignore[attr-defined]
        x, y, hue = sel["x"], sel["y"], sel["hue"]
        groups = sel.get("groups", [])
        
        # Expand groups to create multiple plots
        try:
            filter_queries = expand_groups(df, groups)
        except ValueError as e:
            QMessageBox.warning(self, "Too Many Combinations", str(e))
            return
        
        # Compute shared axes if groups present
        xlim, ylim = None, None
        if len(filter_queries) > 1:
            subsets = []
            for fq in filter_queries:
                subset = df
                for col, val in fq.items():
                    subset = subset[subset[col] == val]
                subsets.append(subset)
            xlim, ylim = shared_limits(subsets, x, y)
        
        # Place plots in grid
        for fq in filter_queries:
            coord = self.grid_board.first_empty_coord()
            if coord is None:
                self.grid_board.add_row()
                coord = (self.grid_board._rows - 1, 0)
            
            tile = self.grid_board.tile_at(*coord)
            
            # Build title from filter query
            if fq:
                title_parts = [f"{k}={v}" for k, v in fq.items()]
                title = ", ".join(title_parts)
            else:
                title = None
            
            tile.set_plot(
                df=df,
                x=x,
                y=y,
                hue=hue,
                title=title,
                filter_query=fq,
                xlim=xlim,
                ylim=ylim,
            )


