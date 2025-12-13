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
    QDoubleSpinBox,
    QRadioButton,
    QButtonGroup,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QCheckBox,
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
        self.sem_combo = QComboBox(self)
        self.sem_combo.addItem("(none)", "")
        
        form.addRow("x", self.x_combo)
        form.addRow("y", self.y_combo)
        form.addRow("SEM column (optional)", self.sem_combo)
        
        # Add checkbox for pre-computed SEM
        self.precomputed_sem_check = QCheckBox("Pre-computed SEM", self)
        self.precomputed_sem_check.setChecked(False)
        form.addRow("", self.precomputed_sem_check)
        
        # Add info label about SEM
        self.sem_info = QLabel("SEM column: Groups data before averaging, then computes mean ± SEM as shaded region")
        self.sem_info.setWordWrap(True)
        self.sem_info.setStyleSheet("color: gray; font-size: 9px;")
        form.addRow("", self.sem_info)
        
        # Update info label when checkbox changes
        self.precomputed_sem_check.stateChanged.connect(self._update_sem_info)
        
        # Hue section (multi-select)
        layout.addWidget(QLabel("Hue columns (multi-select, optional):"))
        self.hue_list = QListWidget(self)
        self.hue_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.hue_list.setMaximumHeight(100)
        layout.addWidget(self.hue_list)
        
        self.hue_count_label = QLabel("")
        layout.addWidget(self.hue_count_label)
        
        # Plot style section
        style_label = QLabel("Plot Style:")
        style_label.setStyleSheet("font-weight: bold;")
        form.addRow(style_label)
        
        self.style_line_check = QCheckBox("Line", self)
        self.style_line_check.setChecked(True)  # Default: line
        self.style_marker_check = QCheckBox("Markers", self)
        self.style_marker_check.setChecked(False)  # Default: no markers
        
        style_layout = QHBoxLayout()
        style_layout.addWidget(self.style_line_check)
        style_layout.addWidget(self.style_marker_check)
        form.addRow("", style_layout)

        layout.addLayout(form)
        
        # Groups section
        layout.addWidget(QLabel("Groups (faceting, multi-select):"))
        self.group_list = QListWidget(self)
        self.group_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.group_list.setMaximumHeight(120)
        layout.addWidget(self.group_list)
        
        self.combo_count_label = QLabel("")
        layout.addWidget(self.combo_count_label)
        
        # Y-axis limits section
        ylim_group = QGroupBox("Y-axis Limits (optional)")
        ylim_layout = QVBoxLayout()
        
        # Checkbox to enable custom y-limits
        self.custom_ylim_check = QCheckBox("Use custom Y-axis limits", self)
        self.custom_ylim_check.setChecked(False)
        ylim_layout.addWidget(self.custom_ylim_check)
        
        # Y-axis min/max fields
        ylim_form = QFormLayout()
        self.ymin_spin = QDoubleSpinBox(self)
        self.ymin_spin.setMinimum(-1e9)
        self.ymin_spin.setMaximum(1e9)
        self.ymin_spin.setValue(0.0)
        self.ymin_spin.setDecimals(6)
        self.ymin_spin.setEnabled(False)
        ylim_form.addRow("Y-axis min:", self.ymin_spin)
        
        self.ymax_spin = QDoubleSpinBox(self)
        self.ymax_spin.setMinimum(-1e9)
        self.ymax_spin.setMaximum(1e9)
        self.ymax_spin.setValue(1.0)
        self.ymax_spin.setDecimals(6)
        self.ymax_spin.setEnabled(False)
        ylim_form.addRow("Y-axis max:", self.ymax_spin)
        
        ylim_layout.addLayout(ylim_form)
        
        # Info label
        ylim_info = QLabel("Applied to all plots in this set")
        ylim_info.setWordWrap(True)
        ylim_info.setStyleSheet("color: gray; font-size: 9px;")
        ylim_layout.addWidget(ylim_info)
        
        ylim_group.setLayout(ylim_layout)
        layout.addWidget(ylim_group)
        
        # Connect checkbox to enable/disable spinboxes
        self.custom_ylim_check.stateChanged.connect(self._toggle_ylim_fields)
        
        # Reference lines section
        ref_lines_group = QGroupBox("Reference Lines (optional)")
        ref_lines_layout = QVBoxLayout()
        
        # Horizontal lines
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Horizontal (y-values, comma-separated):"))
        self.hlines_input = QLineEdit(self)
        self.hlines_input.setPlaceholderText("e.g., 0, 50, 100")
        h_layout.addWidget(self.hlines_input)
        ref_lines_layout.addLayout(h_layout)
        
        # Vertical lines
        v_layout = QHBoxLayout()
        v_layout.addWidget(QLabel("Vertical (x-values, comma-separated):"))
        self.vlines_input = QLineEdit(self)
        self.vlines_input.setPlaceholderText("e.g., 10, 20, 30")
        v_layout.addWidget(self.vlines_input)
        ref_lines_layout.addLayout(v_layout)
        
        ref_lines_group.setLayout(ref_lines_layout)
        layout.addWidget(ref_lines_group)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        layout.addWidget(buttons)

        self.ds_combo.currentIndexChanged.connect(self._refresh_columns)
        self.group_list.itemSelectionChanged.connect(self._update_combo_count)
        self.hue_list.itemSelectionChanged.connect(self._update_hue_count)
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
        fill(self.sem_combo, allow_blank=True)
        
        # Refresh group list
        self.group_list.clear()
        for c in cols:
            self.group_list.addItem(c)
        self._update_combo_count()
        
        # Refresh hue list
        self.hue_list.clear()
        for c in cols:
            self.hue_list.addItem(c)
        self._update_hue_count()
    
    def _update_combo_count(self) -> None:
        selected = [item.text() for item in self.group_list.selectedItems()]
        if not selected:
            self.combo_count_label.setText("")
        else:
            self.combo_count_label.setText(f"Selected {len(selected)} group column(s). Will compute cross-product.")
    
    def _update_hue_count(self) -> None:
        selected = [item.text() for item in self.hue_list.selectedItems()]
        if not selected:
            self.hue_count_label.setText("")
        else:
            self.hue_count_label.setText(f"Selected {len(selected)} hue column(s). Will combine values for legend.")
    
    def _update_sem_info(self) -> None:
        """Update SEM info label based on checkbox state."""
        if self.precomputed_sem_check.isChecked():
            self.sem_info.setText("SEM column: Uses pre-computed SEM values from selected column")
        else:
            self.sem_info.setText("SEM column: Groups data before averaging, then computes mean ± SEM as shaded region")
    
    def _toggle_ylim_fields(self) -> None:
        """Enable/disable Y-axis limit spinboxes based on checkbox state."""
        enabled = self.custom_ylim_check.isChecked()
        self.ymin_spin.setEnabled(enabled)
        self.ymax_spin.setEnabled(enabled)

    def selection(self) -> Optional[dict]:
        if self.result() != QDialog.Accepted:
            return None
        groups = [item.text() for item in self.group_list.selectedItems()]
        hue_cols = [item.text() for item in self.hue_list.selectedItems()]
        x = self.x_combo.currentData()
        y = self.y_combo.currentData()
        sem = self.sem_combo.currentData() or None
        
        # Validate SEM column doesn't conflict with other columns
        if sem:
            used_cols = {x, y}
            used_cols.update(hue_cols)
            used_cols.update(groups)
            
            if sem in used_cols:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self, "Invalid SEM Column",
                    f"SEM column '{sem}' is already used as x, y, hue, or group.\n"
                    "Please select a different column."
                )
                return None
        
        # Validate hue columns don't conflict with x, y, or groups
        conflict_cols = {x, y}
        conflict_cols.update(groups)
        if sem:
            conflict_cols.add(sem)
        
        hue_conflicts = set(hue_cols) & conflict_cols
        if hue_conflicts:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, "Invalid Hue Columns",
                f"Hue column(s) {hue_conflicts} already used as x, y, group, or SEM.\n"
                "Please select different columns."
            )
            return None
        
        # Parse reference lines
        hlines = self._parse_numbers(self.hlines_input.text())
        vlines = self._parse_numbers(self.vlines_input.text())
        
        # Get custom y-limits if enabled
        y_min = None
        y_max = None
        if self.custom_ylim_check.isChecked():
            y_min = self.ymin_spin.value()
            y_max = self.ymax_spin.value()
            # Validate that min < max
            if y_min >= y_max:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self, "Invalid Y-limits",
                    f"Y-axis min ({y_min}) must be less than Y-axis max ({y_max})."
                )
                return None
        
        return {
            "datasource_id": self.ds_combo.currentData(),
            "x": x,
            "y": y,
            "hue": hue_cols if hue_cols else None,
            "sem_column": sem,
            "sem_precomputed": self.precomputed_sem_check.isChecked(),
            "groups": groups,
            "hlines": hlines,
            "vlines": vlines,
            "style_line": self.style_line_check.isChecked(),
            "style_marker": self.style_marker_check.isChecked(),
            "y_min": y_min,
            "y_max": y_max,
        }
    
    def _parse_numbers(self, text: str) -> list[float]:
        """Parse comma-separated numbers from text input.
        
        Returns empty list if parsing fails or text is empty.
        """
        if not text or not text.strip():
            return []
        
        numbers = []
        for part in text.split(','):
            part = part.strip()
            if not part:
                continue
            try:
                numbers.append(float(part))
            except ValueError:
                # Skip invalid values silently
                continue
        
        return numbers


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
        
        # Connect signals to detect changes (use Qt.QueuedConnection to avoid recursion)
        from PySide6.QtCore import Qt as QtCore
        self.row_spin.valueChanged.connect(self._on_position_changed, QtCore.QueuedConnection)
        self.col_spin.valueChanged.connect(self._on_position_changed, QtCore.QueuedConnection)
        self.rowspan_spin.valueChanged.connect(self._on_span_changed, QtCore.QueuedConnection)
        self.colspan_spin.valueChanged.connect(self._on_span_changed, QtCore.QueuedConnection)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _on_position_changed(self) -> None:
        """Lock span controls when position changes."""
        if not hasattr(self, '_updating'):
            self._updating = False
        if self._updating:
            return
        self._updating = True
        
        pos_changed = (self.row_spin.value() != self._initial_row or 
                      self.col_spin.value() != self._initial_col)
        if pos_changed:
            self.rowspan_spin.setEnabled(False)
            self.colspan_spin.setEnabled(False)
        
        self._updating = False
    
    def _on_span_changed(self) -> None:
        """Lock position controls when span changes."""
        if not hasattr(self, '_updating'):
            self._updating = False
        if self._updating:
            return
        self._updating = True
        
        span_changed = (self.rowspan_spin.value() != self._initial_rowspan or 
                       self.colspan_spin.value() != self._initial_colspan)
        if span_changed:
            self.row_spin.setEnabled(False)
            self.col_spin.setEnabled(False)
        
        self._updating = False
    
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


class ExportDialog(QDialog):
    """Dialog to configure grid export settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Grid")
        
        layout = QVBoxLayout(self)
        
        # Format group
        format_group = QGroupBox("Export Format")
        format_layout = QVBoxLayout()
        
        self.format_group = QButtonGroup(self)
        self.pdf_radio = QRadioButton("PDF (vector)")
        self.svg_radio = QRadioButton("SVG (vector)")
        self.eps_radio = QRadioButton("EPS (vector)")
        self.png_radio = QRadioButton("PNG (raster)")
        
        self.format_group.addButton(self.pdf_radio, 0)
        self.format_group.addButton(self.svg_radio, 1)
        self.format_group.addButton(self.eps_radio, 2)
        self.format_group.addButton(self.png_radio, 3)
        
        self.pdf_radio.setChecked(True)
        
        format_layout.addWidget(self.pdf_radio)
        format_layout.addWidget(self.svg_radio)
        format_layout.addWidget(self.eps_radio)
        format_layout.addWidget(self.png_radio)
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # Size group
        size_group = QGroupBox("Page Size")
        size_layout = QFormLayout()
        
        # Preset selector
        self.preset_combo = QComboBox(self)
        self.preset_combo.addItem("A4 (8.27 × 11.69 inches)", "a4")
        self.preset_combo.addItem("Letter (8.5 × 11 inches)", "letter")
        self.preset_combo.addItem("Custom", "custom")
        size_layout.addRow("Preset:", self.preset_combo)
        
        # Custom dimensions
        self.width_spin = QDoubleSpinBox(self)
        self.width_spin.setMinimum(1.0)
        self.width_spin.setMaximum(100.0)
        self.width_spin.setValue(11.0)
        self.width_spin.setSuffix(" inches")
        self.width_spin.setEnabled(False)
        size_layout.addRow("Width:", self.width_spin)
        
        self.height_spin = QDoubleSpinBox(self)
        self.height_spin.setMinimum(1.0)
        self.height_spin.setMaximum(100.0)
        self.height_spin.setValue(8.5)
        self.height_spin.setSuffix(" inches")
        self.height_spin.setEnabled(False)
        size_layout.addRow("Height:", self.height_spin)
        
        size_group.setLayout(size_layout)
        layout.addWidget(size_group)
        
        # DPI group (for PNG only)
        self.dpi_group = QGroupBox("Resolution (PNG only)")
        dpi_layout = QFormLayout()
        
        self.dpi_spin = QSpinBox(self)
        self.dpi_spin.setMinimum(72)
        self.dpi_spin.setMaximum(600)
        self.dpi_spin.setValue(150)
        self.dpi_spin.setSuffix(" DPI")
        self.dpi_spin.setEnabled(False)
        dpi_layout.addRow("DPI:", self.dpi_spin)
        
        self.dpi_group.setLayout(dpi_layout)
        layout.addWidget(self.dpi_group)
        
        # Connect signals
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        self.png_radio.toggled.connect(self._on_format_changed)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _on_preset_changed(self) -> None:
        """Handle preset selection changes."""
        preset = self.preset_combo.currentData()
        if preset == "a4":
            self.width_spin.setValue(8.27)
            self.height_spin.setValue(11.69)
            self.width_spin.setEnabled(False)
            self.height_spin.setEnabled(False)
        elif preset == "letter":
            self.width_spin.setValue(8.5)
            self.height_spin.setValue(11.0)
            self.width_spin.setEnabled(False)
            self.height_spin.setEnabled(False)
        else:  # custom
            self.width_spin.setEnabled(True)
            self.height_spin.setEnabled(True)
    
    def _on_format_changed(self) -> None:
        """Enable/disable DPI based on format."""
        self.dpi_spin.setEnabled(self.png_radio.isChecked())
    
    def get_settings(self) -> Optional[dict]:
        if self.result() != QDialog.Accepted:
            return None
        
        # Determine format
        if self.pdf_radio.isChecked():
            fmt = "pdf"
        elif self.svg_radio.isChecked():
            fmt = "svg"
        elif self.eps_radio.isChecked():
            fmt = "eps"
        else:
            fmt = "png"
        
        return {
            "format": fmt,
            "width": self.width_spin.value(),
            "height": self.height_spin.value(),
            "dpi": self.dpi_spin.value() if fmt == "png" else 150,
        }


class ErrorMarkerDialog(QDialog):
    """Dialog to add a single error bar marker to a plot."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Error Marker")
        
        layout = QVBoxLayout(self)
        
        # Info label
        info = QLabel("Create an error bar marker annotation. At least one error bar (X or Y) is required.")
        info.setWordWrap(True)
        info.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(info)
        
        # Form for marker parameters
        form = QFormLayout()
        
        # Position fields
        pos_group = QGroupBox("Position (auto-computed if blank)")
        pos_layout = QFormLayout()
        
        self.x_input = QLineEdit(self)
        self.x_input.setPlaceholderText("Auto-positioned, or integer 0,1,2... for vertical bars")
        pos_layout.addRow("X position:", self.x_input)
        
        self.y_input = QLineEdit(self)
        self.y_input.setPlaceholderText("Auto-positioned, or integer 0,1,2... for horizontal bars")
        pos_layout.addRow("Y position:", self.y_input)
        
        pos_group.setLayout(pos_layout)
        layout.addWidget(pos_group)
        
        # Error bar fields
        err_group = QGroupBox("Error Bars (at least one required)")
        err_layout = QFormLayout()
        
        self.xerr_input = QLineEdit(self)
        self.xerr_input.setPlaceholderText("Leave blank for no X error")
        err_layout.addRow("X error (±):", self.xerr_input)
        
        self.yerr_input = QLineEdit(self)
        self.yerr_input.setPlaceholderText("Leave blank for no Y error")
        err_layout.addRow("Y error (±):", self.yerr_input)
        
        err_group.setLayout(err_layout)
        layout.addWidget(err_group)
        
        # Style fields
        style_group = QGroupBox("Appearance")
        style_layout = QFormLayout()
        
        # Marker shape selector
        self.marker_combo = QComboBox(self)
        self.marker_combo.addItem("Triangle Down (v)", "v")
        self.marker_combo.addItem("Triangle Up (^)", "^")
        self.marker_combo.addItem("Circle (o)", "o")
        self.marker_combo.addItem("Square (s)", "s")
        self.marker_combo.addItem("Diamond (D)", "D")
        self.marker_combo.addItem("Star (*)", "*")
        self.marker_combo.addItem("X mark (x)", "x")
        self.marker_combo.addItem("Plus (+)", "+")
        self.marker_combo.addItem("Triangle Left (<)", "<")
        self.marker_combo.addItem("Triangle Right (>)", ">")
        style_layout.addRow("Marker shape:", self.marker_combo)
        
        # Color picker
        color_layout = QHBoxLayout()
        self.color_input = QLineEdit(self)
        self.color_input.setText("red")
        self.color_input.setPlaceholderText("e.g., red, #FF0000, blue")
        color_layout.addWidget(self.color_input)
        
        self.color_button = QPushButton("Choose Color", self)
        self.color_button.clicked.connect(self._choose_color)
        color_layout.addWidget(self.color_button)
        
        style_layout.addRow("Color:", color_layout)
        
        # Label field
        self.label_input = QLineEdit(self)
        self.label_input.setPlaceholderText("Optional legend label")
        style_layout.addRow("Label:", self.label_input)
        
        style_group.setLayout(style_layout)
        layout.addWidget(style_group)
        
        # Info about fixed parameters
        fixed_info = QLabel("Fixed: size=8, capsize=3.5")
        fixed_info.setWordWrap(True)
        fixed_info.setStyleSheet("color: gray; font-size: 9px; font-style: italic;")
        layout.addWidget(fixed_info)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _choose_color(self) -> None:
        """Open color picker dialog."""
        from PySide6.QtWidgets import QColorDialog
        from PySide6.QtGui import QColor
        
        # Parse current color
        current_text = self.color_input.text()
        current_color = QColor(current_text) if current_text else QColor("red")
        
        color = QColorDialog.getColor(current_color, self, "Choose Marker Color")
        if color.isValid():
            self.color_input.setText(color.name())
    
    def _validate_and_accept(self) -> None:
        """Validate input before accepting."""
        from PySide6.QtWidgets import QMessageBox
        
        # Check that at least one error bar is provided
        xerr_text = self.xerr_input.text().strip()
        yerr_text = self.yerr_input.text().strip()
        
        if not xerr_text and not yerr_text:
            QMessageBox.warning(
                self, "Missing Error Bar",
                "At least one error bar (X or Y) is required."
            )
            return
        
        # Try to parse the error bars
        try:
            if xerr_text:
                float(xerr_text)
            if yerr_text:
                float(yerr_text)
        except ValueError:
            QMessageBox.warning(
                self, "Invalid Number",
                "Error bar values must be valid numbers."
            )
            return
        
        # Try to parse position values if provided
        x_text = self.x_input.text().strip()
        y_text = self.y_input.text().strip()
        
        try:
            if x_text:
                float(x_text)
            if y_text:
                float(y_text)
        except ValueError:
            QMessageBox.warning(
                self, "Invalid Number",
                "Position values must be valid numbers."
            )
            return
        
        # Validate color
        color_text = self.color_input.text().strip()
        if not color_text:
            QMessageBox.warning(
                self, "Missing Color",
                "Color is required."
            )
            return
        
        self.accept()
    
    def get_marker(self) -> Optional[dict]:
        """Get the marker dictionary."""
        if self.result() != QDialog.Accepted:
            return None
        
        marker = {}
        
        # Position values (None if not provided)
        x_text = self.x_input.text().strip()
        y_text = self.y_input.text().strip()
        
        if x_text:
            marker['x'] = float(x_text)
        else:
            marker['x'] = None
        
        if y_text:
            marker['y'] = float(y_text)
        else:
            marker['y'] = None
        
        # Error bar values
        xerr_text = self.xerr_input.text().strip()
        yerr_text = self.yerr_input.text().strip()
        
        if xerr_text:
            marker['xerr'] = float(xerr_text)
        else:
            marker['xerr'] = None
        
        if yerr_text:
            marker['yerr'] = float(yerr_text)
        else:
            marker['yerr'] = None
        
        # Marker shape
        marker['marker'] = self.marker_combo.currentData()
        
        # Color
        marker['color'] = self.color_input.text().strip()
        
        # Label (optional)
        label_text = self.label_input.text().strip()
        if label_text:
            marker['label'] = label_text
        else:
            marker['label'] = None
        
        return marker


class ErrorMarkersManagerDialog(QDialog):
    """Dialog to view, edit, and delete error markers."""
    
    def __init__(self, parent=None, markers: list[dict] = None):
        super().__init__(parent)
        self.setWindowTitle("Manage Error Markers")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self._markers = markers.copy() if markers else []
        
        layout = QVBoxLayout(self)
        
        # Info label
        info = QLabel(f"Current markers: {len(self._markers)}")
        layout.addWidget(info)
        
        # List widget to show markers
        self.marker_list = QListWidget(self)
        self._refresh_list()
        layout.addWidget(self.marker_list)
        
        # Buttons for managing markers
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Marker", self)
        self.add_button.clicked.connect(self._add_marker)
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit Selected", self)
        self.edit_button.clicked.connect(self._edit_marker)
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete Selected", self)
        self.delete_button.clicked.connect(self._delete_marker)
        button_layout.addWidget(self.delete_button)
        
        layout.addLayout(button_layout)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _refresh_list(self) -> None:
        """Refresh the list widget with current markers."""
        self.marker_list.clear()
        for i, marker in enumerate(self._markers):
            # Format marker info for display
            parts = []
            
            if marker.get('x') is not None:
                parts.append(f"x={marker['x']:.3f}")
            else:
                parts.append("x=auto")
            
            if marker.get('y') is not None:
                parts.append(f"y={marker['y']:.3f}")
            else:
                parts.append("y=auto")
            
            if marker.get('xerr') is not None:
                parts.append(f"xerr=±{marker['xerr']:.3f}")
            
            if marker.get('yerr') is not None:
                parts.append(f"yerr=±{marker['yerr']:.3f}")
            
            parts.append(f"marker={marker.get('marker', 'v')}")
            parts.append(f"color={marker.get('color', 'red')}")
            
            if marker.get('label'):
                parts.append(f"label='{marker['label']}'")
            
            display_text = ", ".join(parts)
            self.marker_list.addItem(f"{i+1}. {display_text}")
    
    def _add_marker(self) -> None:
        """Add a new marker."""
        dialog = ErrorMarkerDialog(self)
        dialog.exec()
        marker = dialog.get_marker()
        
        if marker:
            self._markers.append(marker)
            self._refresh_list()
    
    def _edit_marker(self) -> None:
        """Edit the selected marker."""
        from PySide6.QtWidgets import QMessageBox
        
        selected_items = self.marker_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a marker to edit.")
            return
        
        index = self.marker_list.row(selected_items[0])
        marker = self._markers[index]
        
        # Create dialog pre-filled with current values
        dialog = ErrorMarkerDialog(self)
        if marker.get('x') is not None:
            dialog.x_input.setText(str(marker['x']))
        if marker.get('y') is not None:
            dialog.y_input.setText(str(marker['y']))
        if marker.get('xerr') is not None:
            dialog.xerr_input.setText(str(marker['xerr']))
        if marker.get('yerr') is not None:
            dialog.yerr_input.setText(str(marker['yerr']))
        
        # Set marker shape
        marker_shape = marker.get('marker', 'v')
        index = dialog.marker_combo.findData(marker_shape)
        if index >= 0:
            dialog.marker_combo.setCurrentIndex(index)
        
        dialog.color_input.setText(marker.get('color', 'red'))
        if marker.get('label'):
            dialog.label_input.setText(marker['label'])
        
        dialog.exec()
        updated_marker = dialog.get_marker()
        
        if updated_marker:
            self._markers[index] = updated_marker
            self._refresh_list()
    
    def _delete_marker(self) -> None:
        """Delete the selected marker."""
        from PySide6.QtWidgets import QMessageBox
        
        selected_items = self.marker_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a marker to delete.")
            return
        
        index = self.marker_list.row(selected_items[0])
        del self._markers[index]
        self._refresh_list()
    
    def get_markers(self) -> Optional[list[dict]]:
        """Get the updated list of markers."""
        if self.result() != QDialog.Accepted:
            return None
        return self._markers


