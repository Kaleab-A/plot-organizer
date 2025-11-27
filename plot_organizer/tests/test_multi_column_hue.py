"""Tests for multi-column hue functionality."""
from __future__ import annotations

import pandas as pd
import pytest
from PySide6.QtWidgets import QApplication

from plot_organizer.ui.grid_board import PlotTile
from plot_organizer.services.plot_service import shared_limits_with_sem


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_multi_column_hue_basic(qapp):
    """Test that multi-column hue creates composite labels."""
    df = pd.DataFrame({
        'x': [1, 1, 2, 2, 3, 3] * 4,
        'y': [10, 12, 15, 17, 20, 22] * 4,
        'species': ['A', 'A', 'A', 'A', 'A', 'A', 
                    'B', 'B', 'B', 'B', 'B', 'B'] * 2,
        'gender': ['male', 'female'] * 12,
    })
    
    tile = PlotTile()
    tile.set_plot(df, x='x', y='y', hue=['species', 'gender'])
    
    # Get the axes and check that we have a legend
    ax = tile.figure.axes[0]
    legend = ax.get_legend()
    
    assert legend is not None, "Legend should be present with multi-column hue"
    
    # Check that legend labels have the expected format
    labels = [text.get_text() for text in legend.get_texts()]
    
    # Should have 4 combinations: A+male, A+female, B+male, B+female
    assert len(labels) == 4, f"Expected 4 legend entries, got {len(labels)}"
    
    # Check format: "species=A, gender=male"
    expected_labels = [
        'species=A, gender=female',
        'species=A, gender=male',
        'species=B, gender=female',
        'species=B, gender=male',
    ]
    
    # Sort both lists for comparison (order may vary)
    assert sorted(labels) == sorted(expected_labels), f"Labels don't match. Got: {labels}"


def test_single_column_hue_backward_compat(qapp):
    """Test that single string hue still works (backward compatibility)."""
    df = pd.DataFrame({
        'x': [1, 2, 3, 1, 2, 3],
        'y': [10, 15, 20, 12, 17, 22],
        'group': ['A', 'A', 'A', 'B', 'B', 'B'],
    })
    
    tile = PlotTile()
    tile.set_plot(df, x='x', y='y', hue='group')
    
    ax = tile.figure.axes[0]
    legend = ax.get_legend()
    
    assert legend is not None
    labels = [text.get_text() for text in legend.get_texts()]
    
    # Should have 2 groups
    assert len(labels) == 2
    assert set(labels) == {'A', 'B'}


def test_no_hue(qapp):
    """Test that no hue works correctly."""
    df = pd.DataFrame({
        'x': [1, 2, 3],
        'y': [10, 15, 20],
    })
    
    tile = PlotTile()
    tile.set_plot(df, x='x', y='y', hue=None)
    
    ax = tile.figure.axes[0]
    legend = ax.get_legend()
    
    # Should have no legend
    assert legend is None


def test_empty_hue_list(qapp):
    """Test that empty hue list works like no hue."""
    df = pd.DataFrame({
        'x': [1, 2, 3],
        'y': [10, 15, 20],
    })
    
    tile = PlotTile()
    tile.set_plot(df, x='x', y='y', hue=[])
    
    ax = tile.figure.axes[0]
    legend = ax.get_legend()
    
    # Should have no legend
    assert legend is None


def test_multi_column_hue_with_sem(qapp):
    """Test multi-column hue with SEM column."""
    df = pd.DataFrame({
        'x': [1, 1, 1, 2, 2, 2] * 4,
        'y': [10, 11, 12, 20, 21, 22] * 4,
        'subject': [1, 2, 3, 1, 2, 3] * 4,
        'condition': ['A', 'A', 'A', 'A', 'A', 'A',
                      'B', 'B', 'B', 'B', 'B', 'B'] * 2,
        'treatment': ['drug', 'placebo'] * 12,
    })
    
    tile = PlotTile()
    tile.set_plot(df, x='x', y='y', hue=['condition', 'treatment'], sem_column='subject')
    
    ax = tile.figure.axes[0]
    legend = ax.get_legend()
    
    assert legend is not None
    labels = [text.get_text() for text in legend.get_texts()]
    
    # Should have 4 combinations
    assert len(labels) == 4


def test_shared_limits_with_multi_column_hue():
    """Test that shared_limits_with_sem works with multi-column hue."""
    df = pd.DataFrame({
        'x': [1, 2, 3] * 8,
        'y': [10, 20, 30] * 8,
        'group': ['G1'] * 12 + ['G2'] * 12,
        'species': ['A', 'A', 'A', 'B', 'B', 'B'] * 4,
        'gender': ['male', 'female'] * 12,
    })
    
    filter_queries = [{'group': 'G1'}, {'group': 'G2'}]
    
    xlim, ylim = shared_limits_with_sem(
        df, filter_queries, x='x', y='y', 
        sem_column=None, hue=['species', 'gender']
    )
    
    # Should compute limits correctly
    assert xlim[0] <= 1 and xlim[1] >= 3
    assert ylim[0] <= 10 and ylim[1] >= 30


def test_multi_column_hue_three_columns(qapp):
    """Test multi-column hue with three columns."""
    df = pd.DataFrame({
        'x': [1, 2, 3] * 8,
        'y': [10, 20, 30] * 8,
        'col1': ['A', 'A', 'A', 'A', 'B', 'B', 'B', 'B'] * 3,
        'col2': ['X', 'X', 'Y', 'Y'] * 6,
        'col3': ['P', 'Q'] * 12,
    })
    
    tile = PlotTile()
    tile.set_plot(df, x='x', y='y', hue=['col1', 'col2', 'col3'])
    
    ax = tile.figure.axes[0]
    legend = ax.get_legend()
    
    assert legend is not None
    labels = [text.get_text() for text in legend.get_texts()]
    
    # Should have multiple combinations
    assert len(labels) > 0
    
    # Check format includes all three columns
    for label in labels:
        assert 'col1=' in label
        assert 'col2=' in label
        assert 'col3=' in label
        assert label.count('=') == 3  # Three key-value pairs
        assert label.count(',') == 2   # Two commas separating them


def test_multi_column_hue_preserves_original(qapp):
    """Test that multi-column hue doesn't modify the original dataframe."""
    df = pd.DataFrame({
        'x': [1, 2, 3],
        'y': [10, 20, 30],
        'species': ['A', 'A', 'B'],
        'gender': ['male', 'female', 'male'],
    })
    
    original_columns = df.columns.tolist()
    
    tile = PlotTile()
    tile.set_plot(df, x='x', y='y', hue=['species', 'gender'])
    
    # Original dataframe should be unchanged
    assert df.columns.tolist() == original_columns
    assert '__composite_hue__' not in df.columns


def test_multi_column_hue_with_filter(qapp):
    """Test multi-column hue works with filter_query."""
    df = pd.DataFrame({
        'x': [1, 2, 3] * 4,
        'y': [10, 20, 30] * 4,
        'group': ['G1', 'G1', 'G1', 'G2', 'G2', 'G2'] * 2,
        'species': ['A', 'B'] * 6,
        'gender': ['male', 'female'] * 6,
    })
    
    tile = PlotTile()
    tile.set_plot(
        df, x='x', y='y', 
        hue=['species', 'gender'],
        filter_query={'group': 'G1'}
    )
    
    ax = tile.figure.axes[0]
    legend = ax.get_legend()
    
    assert legend is not None
    labels = [text.get_text() for text in legend.get_texts()]
    
    # Should only show combinations from G1 group
    assert len(labels) > 0
    for label in labels:
        assert 'species=' in label
        assert 'gender=' in label

