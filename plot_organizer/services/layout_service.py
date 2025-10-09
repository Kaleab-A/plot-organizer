from __future__ import annotations

from typing import Optional

from plot_organizer.models import GridLayout


def create_grid(rows: int, cols: int) -> GridLayout:
    cells: dict[tuple[int, int], str | None] = {}
    for r in range(rows):
        for c in range(cols):
            cells[(r, c)] = None
    return GridLayout(rows=rows, cols=cols, cells=cells)


def add_row(grid: GridLayout) -> None:
    r = grid.rows
    for c in range(grid.cols):
        grid.cells[(r, c)] = None
    grid.rows += 1


def add_col(grid: GridLayout) -> None:
    c = grid.cols
    for r in range(grid.rows):
        grid.cells[(r, c)] = None
    grid.cols += 1


def move_plot(grid: GridLayout, src: tuple[int, int], dst: tuple[int, int]) -> None:
    grid.cells[src], grid.cells[dst] = grid.cells.get(dst), grid.cells.get(src)


def place_plot(grid: GridLayout, coord: tuple[int, int], instance_id: str | None) -> None:
    grid.cells[coord] = instance_id


