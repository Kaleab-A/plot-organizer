from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QHBoxLayout,
)


class DataManagerDock(QDockWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__("Data Sources", parent)
        self.setObjectName("DataManagerDock")
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        host = QWidget(self)
        layout = QVBoxLayout(host)
        self.list_widget = QListWidget(host)
        layout.addWidget(self.list_widget)

        btn_row = QHBoxLayout()
        self.btn_add = QPushButton("Add CSV…", host)
        self.btn_remove = QPushButton("Remove", host)
        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_remove)
        layout.addLayout(btn_row)

        self.setWidget(host)

    def add_source(self, ds_id: str, name: str) -> None:
        item = QListWidgetItem(name)
        item.setData(Qt.UserRole, ds_id)
        self.list_widget.addItem(item)

    def remove_selected(self) -> Optional[str]:
        item = self.list_widget.currentItem()
        if not item:
            return None
        ds_id = item.data(Qt.UserRole)
        row = self.list_widget.row(item)
        self.list_widget.takeItem(row)
        return ds_id


