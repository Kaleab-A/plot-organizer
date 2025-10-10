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


