from __future__ import annotations

from typing import Iterable, Optional

import matplotlib.pyplot as plt
import pandas as pd

from plot_organizer.services.render_service import render_line_plot


def export_single(
    df: pd.DataFrame,
    x: str,
    y: str,
    hue: Optional[str],
    title: Optional[str],
    out_path: str,
    fmt: str = "png",
    width_in: float = 4.0,
    height_in: float = 3.0,
    dpi: int = 150,
) -> None:
    fig, _ = render_line_plot(df=df, x=x, y=y, hue=hue, title=title)
    fig.set_size_inches(width_in, height_in)
    fig.savefig(out_path, format=fmt, dpi=dpi)
    plt.close(fig)


