from __future__ import annotations

from typing import Any, Optional

import matplotlib
matplotlib.use("Agg")  # safe default; Qt backend is used in UI widgets
import matplotlib.pyplot as plt
import pandas as pd


def render_line_plot(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str] = None,
    title: Optional[str] = None,
    style_overrides: Optional[dict[str, Any]] = None,
    shared_xlim: Optional[tuple[float, float]] = None,
    shared_ylim: Optional[tuple[float, float]] = None,
):
    fig, ax = plt.subplots(figsize=(4, 3), constrained_layout=True)
    style = {"linewidth": 1.5}
    if style_overrides:
        style.update(style_overrides)

    if hue:
        for key, sub in df.groupby(hue):
            ax.plot(sub[x], sub[y], label=str(key), **style)
        ax.legend(loc="best")
    else:
        ax.plot(df[x], df[y], **style)

    if title:
        ax.set_title(title)

    if shared_xlim is not None:
        ax.set_xlim(shared_xlim)
    if shared_ylim is not None:
        ax.set_ylim(shared_ylim)

    ax.set_xlabel(x)
    ax.set_ylabel(y)
    return fig, ax


