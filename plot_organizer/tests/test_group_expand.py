from __future__ import annotations

import pandas as pd

from plot_organizer.services import expand_groups


def test_expand_groups_basic():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "y", "x"]})
    combos = expand_groups(df, ["a", "b"])
    # uniques: a -> [1,2], b -> ["x","y"] => 4 combos
    assert len(combos) == 4
    assert {tuple(sorted(d.items())) for d in combos} == {
        (('a', 1), ('b', 'x')),
        (('a', 1), ('b', 'y')),
        (('a', 2), ('b', 'x')),
        (('a', 2), ('b', 'y')),
    }


