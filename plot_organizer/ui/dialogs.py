from __future__ import annotations

from typing import Dict, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QDialogButtonBox,
    QComboBox,
    QListWidget,
    QLabel,
    QAbstractItemView,
    QSpinBox,
    QGroupBox,
)


class QuickPlotDialog(QDialog):
    def __init__(self, parent=None, *, ds_to_columns: Dict[str, List[str]], ds_names: Dict[str, str]):
        super().__init__(parent)
        self.setWindowTitle("Create Plot")
        self._ds_to_columns = ds_to_columns
        self._ds_names = ds_names

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.ds_combo = QComboBox(self)
        for ds_id, name in ds_names.items():
            self.ds_combo.addItem(name, ds_id)
        form.addRow("Data Source", self.ds_combo)

        self.x_combo = QComboBox(self)
        self.y_combo = QComboBox(self)
        self.hue_combo = QComboBox(self)
        self.hue_combo.addItem("(none)", "")
        form.addRow("x", self.x_combo)
        form.addRow("y", self.y_combo)
        form.addRow("hue (optional)", self.hue_combo)

        layout.addLayout(form)
        
        # Groups section
        layout.addWidget(QLabel("Groups (faceting, multi-select):"))
        self.group_list = QListWidget(self)
        self.group_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.group_list.setMaximumHeight(120)
        layout.addWidget(self.group_list)
        
        self.combo_count_label = QLabel("")
        layout.addWidget(self.combo_count_label)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        layout.addWidget(buttons)

        self.ds_combo.currentIndexChanged.connect(self._refresh_columns)
        self.group_list.itemSelectionChanged.connect(self._update_combo_count)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        self._refresh_columns()

    def _refresh_columns(self) -> None:
        ds_id = self.ds_combo.currentData()
        cols = self._ds_to_columns.get(ds_id, [])
        def fill(box: QComboBox, allow_blank: bool = False) -> None:
            box.clear()
            if allow_blank:
                box.addItem("(none)", "")
            for c in cols:
                box.addItem(c, c)
        fill(self.x_combo)
        fill(self.y_combo)
        fill(self.hue_combo, allow_blank=True)
        
        # Refresh group list
        self.group_list.clear()
        for c in cols:
            self.group_list.addItem(c)
        self._update_combo_count()
    
    def _update_combo_count(self) -> None:
        selected = [item.text() for item in self.group_list.selectedItems()]
        if not selected:
            self.combo_count_label.setText("")
        else:
            self.combo_count_label.setText(f"Selected {len(selected)} group column(s). Will compute cross-product.")

    def selection(self) -> Optional[dict]:
        if self.result() != QDialog.Accepted:
            return None
        groups = [item.text() for item in self.group_list.selectedItems()]
        return {
            "datasource_id": self.ds_combo.currentData(),
            "x": self.x_combo.currentData(),
            "y": self.y_combo.currentData(),
            "hue": self.hue_combo.currentData() or None,
            "groups": groups,
        }


class PlotSettingsDialog(QDialog):
    """Dialog to configure plot position and spanning in the grid.
    
    Note: Position and span changes are mutually exclusive - only one can be changed at a time.
    """
    
    def __init__(self, parent=None, *, max_rows: int, max_cols: int, current_row: int = 0, current_col: int = 0, 
                 current_rowspan: int = 1, current_colspan: int = 1):
        super().__init__(parent)
        self.setWindowTitle("Plot Settings")
        
        self._initial_row = current_row
        self._initial_col = current_col
        self._initial_rowspan = current_rowspan
        self._initial_colspan = current_colspan
        
        layout = QVBoxLayout(self)
        
        # Info label at top
        info_top = QLabel("Note: Change position OR span, not both at the same time.")
        info_top.setWordWrap(True)
        info_top.setStyleSheet("color: #2196F3; font-weight: bold; font-size: 10px;")
        layout.addWidget(info_top)
        
        # Position group
        pos_group = QGroupBox("Position (Swap with target cell)")
        pos_layout = QFormLayout()
        
        self.row_spin = QSpinBox(self)
        self.row_spin.setMinimum(0)
        self.row_spin.setMaximum(max_rows - 1)
        self.row_spin.setValue(current_row)
        pos_layout.addRow("Start Row:", self.row_spin)
        
        self.col_spin = QSpinBox(self)
        self.col_spin.setMinimum(0)
        self.col_spin.setMaximum(max_cols - 1)
        self.col_spin.setValue(current_col)
        pos_layout.addRow("Start Column:", self.col_spin)
        
        self.pos_note = QLabel("Will swap with plot at target cell (if spans match)")
        self.pos_note.setWordWrap(True)
        self.pos_note.setStyleSheet("color: gray; font-size: 9px;")
        pos_layout.addRow(self.pos_note)
        
        pos_group.setLayout(pos_layout)
        layout.addWidget(pos_group)
        
        # Span group
        span_group = QGroupBox("Span (Multi-cell)")
        span_layout = QFormLayout()
        
        self.rowspan_spin = QSpinBox(self)
        self.rowspan_spin.setMinimum(1)
        self.rowspan_spin.setMaximum(10)
        self.rowspan_spin.setValue(current_rowspan)
        span_layout.addRow("Rows to span:", self.rowspan_spin)
        
        self.colspan_spin = QSpinBox(self)
        self.colspan_spin.setMinimum(1)
        self.colspan_spin.setMaximum(10)
        self.colspan_spin.setValue(current_colspan)
        span_layout.addRow("Columns to span:", self.colspan_spin)
        
        self.span_note = QLabel("New rows/cols may be created if needed")
        self.span_note.setWordWrap(True)
        self.span_note.setStyleSheet("color: gray; font-size: 9px;")
        span_layout.addRow(self.span_note)
        
        span_group.setLayout(span_layout)
        layout.addWidget(span_group)
        
        # Connect signals to detect changes
        self.row_spin.valueChanged.connect(self._on_position_changed)
        self.col_spin.valueChanged.connect(self._on_position_changed)
        self.rowspan_spin.valueChanged.connect(self._on_span_changed)
        self.colspan_spin.valueChanged.connect(self._on_span_changed)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _on_position_changed(self) -> None:
        """Lock span controls when position changes."""
        pos_changed = (self.row_spin.value() != self._initial_row or 
                      self.col_spin.value() != self._initial_col)
        if pos_changed:
            self.rowspan_spin.setEnabled(False)
            self.colspan_spin.setEnabled(False)
    
    def _on_span_changed(self) -> None:
        """Lock position controls when span changes."""
        span_changed = (self.rowspan_spin.value() != self._initial_rowspan or 
                       self.colspan_spin.value() != self._initial_colspan)
        if span_changed:
            self.row_spin.setEnabled(False)
            self.col_spin.setEnabled(False)
    
    def _validate_and_accept(self) -> None:
        """Validate that only position OR span changed, not both."""
        pos_changed = (self.row_spin.value() != self._initial_row or 
                      self.col_spin.value() != self._initial_col)
        span_changed = (self.rowspan_spin.value() != self._initial_rowspan or 
                       self.colspan_spin.value() != self._initial_colspan)
        
        if pos_changed and span_changed:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, "Invalid Change",
                "Please change either position OR span, not both at the same time.\n\n"
                "Reset one of them to proceed."
            )
            return
        
        self.accept()
    
    def get_settings(self) -> Optional[dict]:
        if self.result() != QDialog.Accepted:
            return None
        
        pos_changed = (self.row_spin.value() != self._initial_row or 
                      self.col_spin.value() != self._initial_col)
        span_changed = (self.rowspan_spin.value() != self._initial_rowspan or 
                       self.colspan_spin.value() != self._initial_colspan)
        
        return {
            "row": self.row_spin.value(),
            "col": self.col_spin.value(),
            "rowspan": self.rowspan_spin.value(),
            "colspan": self.colspan_spin.value(),
            "position_changed": pos_changed,
            "span_changed": span_changed,
        }


