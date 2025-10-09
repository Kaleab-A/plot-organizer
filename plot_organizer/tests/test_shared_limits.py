from __future__ import annotations

import pandas as pd

from plot_organizer.services import shared_limits


def test_shared_limits_numeric():
    df1 = pd.DataFrame({"x": [0, 1, 2], "y": [10, 20, 30]})
    df2 = pd.DataFrame({"x": [2, 3, 4], "y": [5, 15, 25]})
    (xmin, xmax), (ymin, ymax) = shared_limits([df1, df2], "x", "y")
    assert (xmin, xmax) == (0.0, 4.0)
    assert (ymin, ymax) == (5.0, 30.0)


