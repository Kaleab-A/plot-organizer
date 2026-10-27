from __future__ import annotations

from typing import Any, Optional

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


def draw_hue_legend(
    ax,
    hue_colors: Optional[dict[str, str]] = None,
    style_line: bool = True,
    style_marker: bool = False,
) -> None:
    """Draw the hue legend on ax.

    With a shared hue_colors map (grouped plot sets), the legend lists every
    label in the map, including categories absent from this subplot, so one
    legend can describe the whole set. Without a map, the legend is built from
    the artists drawn on ax.
    """
    if not hue_colors:
        ax.legend(loc="best", fontsize="small")
        return

    from matplotlib.lines import Line2D

    show_marker = style_marker or not style_line
    handles = [
        Line2D(
            [], [],
            color=color,
            linestyle="-" if style_line else "none",
            marker="o" if show_marker else None,
            label=label,
        )
        for label, color in hue_colors.items()
    ]
    ax.legend(handles=handles, loc="best", fontsize="small")
