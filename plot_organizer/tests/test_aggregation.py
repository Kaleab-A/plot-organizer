from __future__ import annotations

import pandas as pd
import pytest


def test_aggregation_logic():
    """Test that duplicate (x, hue) combinations are averaged correctly."""
    # Create test data with duplicate x values
    df = pd.DataFrame({
        "x": [1, 1, 1, 2, 2, 3],
        "y": [10, 20, 30, 40, 60, 100],
        "hue": ["A", "A", "B", "A", "B", "A"]
    })
    
    # Test no hue: aggregate by x only
    agg_no_hue = df.groupby("x", as_index=False)["y"].mean()
    assert len(agg_no_hue) == 3
    assert agg_no_hue[agg_no_hue["x"] == 1]["y"].values[0] == 20.0  # (10+20+30)/3
    assert agg_no_hue[agg_no_hue["x"] == 2]["y"].values[0] == 50.0  # (40+60)/2
    assert agg_no_hue[agg_no_hue["x"] == 3]["y"].values[0] == 100.0
    
    # Test with hue: aggregate by (x, hue) pairs
    for hue_val, sub in df.groupby("hue"):
        agg_sub = sub.groupby("x", as_index=False)["y"].mean()
        if hue_val == "A":
            assert len(agg_sub) == 3
            assert agg_sub[agg_sub["x"] == 1]["y"].values[0] == 15.0  # (10+20)/2
            assert agg_sub[agg_sub["x"] == 2]["y"].values[0] == 40.0
            assert agg_sub[agg_sub["x"] == 3]["y"].values[0] == 100.0
        elif hue_val == "B":
            assert len(agg_sub) == 2
            assert agg_sub[agg_sub["x"] == 1]["y"].values[0] == 30.0
            assert agg_sub[agg_sub["x"] == 2]["y"].values[0] == 60.0


def test_no_duplicates():
    """Test that data without duplicates remains unchanged."""
    df = pd.DataFrame({
        "x": [1, 2, 3],
        "y": [10, 20, 30],
    })
    
    agg_df = df.groupby("x", as_index=False)["y"].mean()
    assert len(agg_df) == 3
    assert list(agg_df["x"]) == [1, 2, 3]
    assert list(agg_df["y"]) == [10, 20, 30]


def test_all_duplicates():
    """Test when all x values are the same."""
    df = pd.DataFrame({
        "x": [5, 5, 5, 5],
        "y": [10, 20, 30, 40],
    })
    
    agg_df = df.groupby("x", as_index=False)["y"].mean()
    assert len(agg_df) == 1
    assert agg_df["x"].values[0] == 5
    assert agg_df["y"].values[0] == 25.0  # (10+20+30+40)/4

