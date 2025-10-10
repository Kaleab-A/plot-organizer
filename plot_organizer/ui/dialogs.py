from __future__ import annotations

from typing import Dict, List, Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QDialogButtonBox,
    QComboBox,
)


class QuickPlotDialog(QDialog):
    def __init__(self, parent=None, *, ds_to_columns: Dict[str, List[str]], ds_names: Dict[str, str]):
        super().__init__(parent)
        self.setWindowTitle("Quick Plot")
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
        form.addRow("hue", self.hue_combo)

        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        layout.addWidget(buttons)

        self.ds_combo.currentIndexChanged.connect(self._refresh_columns)
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

    def selection(self) -> Optional[dict]:
        if self.result() != QDialog.Accepted:
            return None
        return {
            "datasource_id": self.ds_combo.currentData(),
            "x": self.x_combo.currentData(),
            "y": self.y_combo.currentData(),
            "hue": self.hue_combo.currentData() or None,
        }


