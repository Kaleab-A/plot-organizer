"""Test custom Y-axis limit control feature."""

import pandas as pd
import pytest
from PySide6.QtWidgets import QApplication

from plot_organizer.ui.grid_board import GridBoard, PlotTile
from plot_organizer.ui.dialogs import QuickPlotDialog


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_plot_tile_stores_ylim(qapp):
    """Test that PlotTile stores y-limits correctly."""
    tile = PlotTile()
    df = pd.DataFrame({
        'x': [1, 2, 3, 4, 5],
        'y': [10, 20, 30, 40, 50]
    })
    
    # Set plot with custom y-limits
    custom_ylim = (0.0, 100.0)
    tile.set_plot(df, 'x', 'y', ylim=custom_ylim)
    
    # Verify y-limits are stored
    assert tile._ylim == custom_ylim
    assert tile._ylim == (0.0, 100.0)


def test_plot_tile_no_ylim_by_default(qapp):
    """Test that PlotTile has no y-limits by default (auto-scale)."""
    tile = PlotTile()
    df = pd.DataFrame({
        'x': [1, 2, 3],
        'y': [10, 20, 30]
    })
    
    # Set plot without custom y-limits
    tile.set_plot(df, 'x', 'y')
    
    # Verify y-limits are None (auto-scale)
    assert tile._ylim is None


def test_plot_tile_clear_resets_ylim(qapp):
    """Test that clearing a plot resets y-limits."""
    tile = PlotTile()
    df = pd.DataFrame({
        'x': [1, 2, 3],
        'y': [10, 20, 30]
    })
    
    # Set plot with custom y-limits
    tile.set_plot(df, 'x', 'y', ylim=(0.0, 50.0))
    assert tile._ylim == (0.0, 50.0)
    
    # Clear plot
    tile.clear_plot()
    
    # Verify y-limits are reset
    assert tile._ylim is None


def test_custom_ylim_checkbox_enables_fields(qapp):
    """Test that checkbox enables/disables y-limit spinboxes."""
    ds_to_columns = {'ds1': ['x', 'y', 'group']}
    ds_names = {'ds1': 'Test Dataset'}
    
    dlg = QuickPlotDialog(ds_to_columns=ds_to_columns, ds_names=ds_names)
    
    # Initially disabled
    assert not dlg.custom_ylim_check.isChecked()
    assert not dlg.ymin_spin.isEnabled()
    assert not dlg.ymax_spin.isEnabled()
    
    # Enable custom limits
    dlg.custom_ylim_check.setChecked(True)
    assert dlg.ymin_spin.isEnabled()
    assert dlg.ymax_spin.isEnabled()
    
    # Disable again
    dlg.custom_ylim_check.setChecked(False)
    assert not dlg.ymin_spin.isEnabled()
    assert not dlg.ymax_spin.isEnabled()


def test_ylim_applied_to_multiple_plots(qapp):
    """Test that custom y-limits are applied to all plots in a set."""
    grid = GridBoard(rows=1, cols=3)
    df = pd.DataFrame({
        'x': [1, 2, 3, 1, 2, 3],
        'y': [10, 20, 30, 15, 25, 35],
        'group': ['A', 'A', 'A', 'B', 'B', 'B']
    })
    
    custom_ylim = (0.0, 100.0)
    
    # Create plots for each group with same y-limits
    for i, group in enumerate(['A', 'B']):
        tile = grid.tile_at(0, i)
        subset = df[df['group'] == group]
        tile.set_plot(subset, 'x', 'y', ylim=custom_ylim)
    
    # Verify all plots have the same y-limits
    for i in range(2):
        tile = grid.tile_at(0, i)
        assert tile._ylim == custom_ylim


def test_ylim_validation_in_dialog(qapp, monkeypatch):
    """Test that dialog validates y_min < y_max."""
    from unittest.mock import Mock
    
    # Mock QMessageBox.warning to avoid blocking on modal dialog
    mock_warning = Mock()
    monkeypatch.setattr('PySide6.QtWidgets.QMessageBox.warning', mock_warning)
    
    ds_to_columns = {'ds1': ['x', 'y']}
    ds_names = {'ds1': 'Test Dataset'}
    
    dlg = QuickPlotDialog(ds_to_columns=ds_to_columns, ds_names=ds_names)
    
    # Set invalid limits (min >= max)
    dlg.custom_ylim_check.setChecked(True)
    dlg.ymin_spin.setValue(100.0)
    dlg.ymax_spin.setValue(50.0)
    dlg.x_combo.setCurrentIndex(0)
    dlg.y_combo.setCurrentIndex(0)
    
    # Accept the dialog (should fail validation)
    dlg.accept()
    result = dlg.selection()
    
    # Should return None due to validation error
    assert result is None
    
    # Verify warning was shown
    assert mock_warning.called


def test_ylim_with_sem_plotting(qapp):
    """Test that custom y-limits work with SEM plots."""
    tile = PlotTile()
    df = pd.DataFrame({
        'x': [1, 1, 2, 2, 3, 3],
        'y': [10, 12, 20, 22, 30, 32],
        'subject': ['s1', 's2', 's1', 's2', 's1', 's2']
    })
    
    custom_ylim = (-10.0, 50.0)
    tile.set_plot(df, 'x', 'y', sem_column='subject', ylim=custom_ylim)
    
    # Verify y-limits are stored even with SEM
    assert tile._ylim == custom_ylim


def test_export_preserves_ylim(qapp):
    """Test that export service has access to stored y-limits."""
    tile = PlotTile()
    df = pd.DataFrame({
        'x': [1, 2, 3],
        'y': [10, 20, 30]
    })
    
    custom_ylim = (0.0, 100.0)
    tile.set_plot(df, 'x', 'y', ylim=custom_ylim)
    
    # Verify the tile stores the limits (export_service will use tile._ylim)
    assert tile._ylim is not None
    assert tile._ylim == custom_ylim
    
    # Verify the attribute exists and can be accessed (as export_service does)
    assert hasattr(tile, '_ylim')
    assert tile._ylim == (0.0, 100.0)

