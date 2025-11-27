from __future__ import annotations

import pandas as pd
import pytest

from plot_organizer.services import expand_groups, shared_limits


def test_expand_groups_no_groups():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    combos = expand_groups(df, [])
    assert len(combos) == 1
    assert combos[0] == {}


def test_expand_groups_single_column():
    df = pd.DataFrame({"cat": ["A", "B", "A", "C"], "val": [1, 2, 3, 4]})
    combos = expand_groups(df, ["cat"])
    assert len(combos) == 3
    assert {"cat": "A"} in combos
    assert {"cat": "B"} in combos
    assert {"cat": "C"} in combos


def test_expand_groups_two_columns():
    df = pd.DataFrame({
        "cat1": ["A", "A", "B", "B"],
        "cat2": ["X", "Y", "X", "Y"],
        "val": [1, 2, 3, 4]
    })
    combos = expand_groups(df, ["cat1", "cat2"])
    assert len(combos) == 4
    assert {"cat1": "A", "cat2": "X"} in combos
    assert {"cat1": "A", "cat2": "Y"} in combos
    assert {"cat1": "B", "cat2": "X"} in combos
    assert {"cat1": "B", "cat2": "Y"} in combos


def test_expand_groups_exceeds_limit():
    # Create a dataframe that would generate > 100 combinations
    df = pd.DataFrame({
        "cat1": list(range(20)) * 5,
        "cat2": [i % 10 for i in range(100)],
        "val": range(100)
    })
    with pytest.raises(ValueError, match="Too many combinations"):
        expand_groups(df, ["cat1", "cat2"])


def test_shared_limits_basic():
    df1 = pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]})
    df2 = pd.DataFrame({"x": [4, 5, 6], "y": [5, 15, 25]})
    (xmin, xmax), (ymin, ymax) = shared_limits([df1, df2], "x", "y")
    assert xmin == 1.0
    assert xmax == 6.0
    assert ymin == 5.0
    assert ymax == 30.0


def test_shared_limits_with_empty():
    df1 = pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]})
    df_empty = pd.DataFrame({"x": [], "y": []})
    (xmin, xmax), (ymin, ymax) = shared_limits([df1, df_empty], "x", "y")
    assert xmin == 1.0
    assert xmax == 3.0
    assert ymin == 10.0
    assert ymax == 30.0

