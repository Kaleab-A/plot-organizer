from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QFileDialog, QMessageBox, QDialog

from plot_organizer.ui.grid_board import GridBoard, PlotTile
from plot_organizer.ui.data_manager import DataManagerDock
from plot_organizer.ui.dialogs import QuickPlotDialog, PlotSettingsDialog, ExportDialog
from plot_organizer.services.load_service import load_csv_to_datasource
from plot_organizer.services.plot_service import expand_groups, shared_limits
from plot_organizer.services.export_service import export_grid


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
        
        # Connect tile signals
        self._connect_tile_signals()

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
        grid_menu.addSeparator()
        remove_row = QAction("- Row...", self)
        remove_col = QAction("- Col...", self)
        remove_row.triggered.connect(self._action_remove_row)
        remove_col.triggered.connect(self._action_remove_col)
        grid_menu.addAction(remove_row)
        grid_menu.addAction(remove_col)
        grid_menu.addSeparator()
        reset_grid = QAction("Reset Grid...", self)
        reset_grid.triggered.connect(self._action_reset_grid)
        grid_menu.addAction(reset_grid)
        
        export_menu = menubar.addMenu("Export")
        export_grid_action = QAction("Export Grid...", self)
        export_grid_action.triggered.connect(self._action_export_grid)
        export_menu.addAction(export_grid_action)

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
        sem_column = sel.get("sem_column")
        sem_precomputed = sel.get("sem_precomputed", False)
        groups = sel.get("groups", [])
        hlines = sel.get("hlines", [])
        vlines = sel.get("vlines", [])
        style_line = sel.get("style_line", True)
        style_marker = sel.get("style_marker", False)
        
        # Expand groups to create multiple plots
        try:
            filter_queries = expand_groups(df, groups)
        except ValueError as e:
            QMessageBox.warning(self, "Too Many Combinations", str(e))
            return
        
        # Compute shared axes if groups present
        xlim, ylim = None, None
        if len(filter_queries) > 1:
            if sem_column:
                # Use SEM-aware limits calculation
                from plot_organizer.services.plot_service import shared_limits_with_sem
                xlim, ylim = shared_limits_with_sem(df, filter_queries, x, y, sem_column, hue, sem_precomputed)
            else:
                # Use original limits calculation
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
                sem_column=sem_column,
                sem_precomputed=sem_precomputed,
                title=title,
                filter_query=fq,
                xlim=xlim,
                ylim=ylim,
                hlines=hlines,
                vlines=vlines,
                style_line=style_line,
                style_marker=style_marker,
            )
            # Connect signals for new tiles
            tile.settings_requested.connect(self._on_tile_settings, Qt.UniqueConnection)
            tile.clear_requested.connect(self._on_tile_clear, Qt.UniqueConnection)
    
    def _connect_tile_signals(self) -> None:
        """Connect signals for all existing tiles."""
        for r in range(self.grid_board._rows):
            for c in range(self.grid_board._cols):
                tile = self.grid_board.tile_at(r, c)
                if tile:
                    tile.settings_requested.connect(self._on_tile_settings, Qt.UniqueConnection)
                    tile.clear_requested.connect(self._on_tile_clear, Qt.UniqueConnection)
    
    def _on_tile_settings(self, tile: PlotTile) -> None:
        """Handle settings request from a tile."""
        pos = self.grid_board.find_tile_position(tile)
        if pos is None:
            return
        
        row, col, rowspan, colspan = pos
        dlg = PlotSettingsDialog(
            self,
            max_rows=self.grid_board._rows,
            max_cols=self.grid_board._cols,
            current_row=row,
            current_col=col,
            current_rowspan=rowspan,
            current_colspan=colspan,
        )
        
        if dlg.exec() == QDialog.Accepted:
            settings = dlg.get_settings()
            if not settings:
                return
            
            # Handle position change (swap)
            if settings.get("position_changed"):
                target_row = settings["row"]
                target_col = settings["col"]
                
                # Check if moving to same position
                if target_row == row and target_col == col:
                    QMessageBox.information(self, "No Change", "Plot is already at this position.")
                    return
                
                # Get tile at target position
                target_tile = self.grid_board.tile_at(target_row, target_col)
                if target_tile is None:
                    QMessageBox.warning(self, "Invalid Target", "No tile found at target position.")
                    return
                
                # Attempt swap
                success, message = self.grid_board.swap_plots(tile, target_tile)
                if success:
                    QMessageBox.information(self, "Success", message)
                    self._connect_tile_signals()
                else:
                    QMessageBox.warning(self, "Cannot Swap", message)
            
            # Handle span change
            elif settings.get("span_changed"):
                self.grid_board.move_plot(
                    row, col,
                    row, col,  # Same position
                    settings["rowspan"], settings["colspan"]
                )
                self._connect_tile_signals()
    
    def _on_tile_clear(self, tile: PlotTile) -> None:
        """Handle clear request from a tile."""
        reply = QMessageBox.question(
            self, "Clear Plot",
            "Are you sure you want to clear this plot?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            tile.clear_plot()
    
    def _action_remove_row(self) -> None:
        """Remove a row from the grid."""
        from PySide6.QtWidgets import QInputDialog
        row, ok = QInputDialog.getInt(
            self, "Remove Row",
            f"Enter row number to remove (0-{self.grid_board._rows - 1}):",
            0, 0, self.grid_board._rows - 1
        )
        if ok:
            if self.grid_board.remove_row(row):
                QMessageBox.information(self, "Success", f"Row {row} removed.")
            else:
                QMessageBox.warning(self, "Cannot Remove", "Row contains non-empty plots. Clear them first.")
    
    def _action_remove_col(self) -> None:
        """Remove a column from the grid."""
        from PySide6.QtWidgets import QInputDialog
        col, ok = QInputDialog.getInt(
            self, "Remove Column",
            f"Enter column number to remove (0-{self.grid_board._cols - 1}):",
            0, 0, self.grid_board._cols - 1
        )
        if ok:
            if self.grid_board.remove_col(col):
                QMessageBox.information(self, "Success", f"Column {col} removed.")
            else:
                QMessageBox.warning(self, "Cannot Remove", "Column contains non-empty plots. Clear them first.")
    
    def _action_reset_grid(self) -> None:
        """Reset the grid to default size and clear all plots."""
        reply = QMessageBox.question(
            self,
            "Reset Grid",
            "This will clear all plots and reset the grid to 2 rows × 3 columns. Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # Clear all plots first
            for r in range(self.grid_board._rows):
                for c in range(self.grid_board._cols):
                    tile = self.grid_board.tile_at(r, c)
                    if tile and not tile.is_empty():
                        tile.clear_plot()
            
            # Reset to default size (2 rows, 3 cols)
            self.grid_board.reset_to_size(2, 3)
            QMessageBox.information(self, "Success", "Grid has been reset to 2×3 with all plots cleared.")
    
    def _action_export_grid(self) -> None:
        """Export the grid layout to a file."""
        # Check if there are any plots
        has_plots = False
        for r in range(self.grid_board._rows):
            for c in range(self.grid_board._cols):
                tile = self.grid_board.tile_at(r, c)
                if tile and not tile.is_empty():
                    has_plots = True
                    break
            if has_plots:
                break
        
        if not has_plots:
            QMessageBox.information(self, "No Plots", "Add some plots to the grid before exporting.")
            return
        
        # Show export dialog
        dlg = ExportDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return
        
        settings = dlg.get_settings()
        if not settings:
            return
        
        # Get output file path
        fmt = settings["format"]
        filters = {
            "pdf": "PDF Files (*.pdf)",
            "svg": "SVG Files (*.svg)",
            "eps": "EPS Files (*.eps)",
            "png": "PNG Files (*.png)",
        }
        
        out_path, _ = QFileDialog.getSaveFileName(
            self, "Save Export",
            f"grid_export.{fmt}",
            filters.get(fmt, "All Files (*)")
        )
        
        if not out_path:
            return
        
        # Perform export
        try:
            export_grid(
                self.grid_board,
                out_path,
                fmt=fmt,
                width_in=settings["width"],
                height_in=settings["height"],
                dpi=settings["dpi"],
            )
            QMessageBox.information(self, "Export Successful", f"Grid exported to:\n{out_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export grid:\n{str(e)}")


