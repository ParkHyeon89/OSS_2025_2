"""
Core game logic for Minesweeper.

This module contains pure domain logic without any pygame or pixel-level
concerns. It defines:
- CellState: the state of a single cell
- Cell: a cell positioned by (col,row) with an attached CellState
- Board: grid management, mine placement, adjacency computation, reveal/flag

The Board exposes imperative methods that the presentation layer (run.py)
can call in response to user inputs, and does not know anything about
rendering, timing, or input devices.
"""

import random
from typing import List, Tuple


class CellState:
    """Mutable state of a single cell.

    Attributes:
        is_mine: Whether this cell contains a mine.
        is_revealed: Whether the cell has been revealed to the player.
        is_flagged: Whether the player flagged this cell as a mine.
        adjacent: Number of adjacent mines in the 8 neighboring cells.
    """

    def __init__(self, is_mine: bool = False, is_revealed: bool = False, is_flagged: bool = False, adjacent: int = 0):
        self.is_mine = is_mine
        self.is_revealed = is_revealed
        self.is_flagged = is_flagged
        self.adjacent = adjacent


class Cell:
    """Logical cell positioned on the board by column and row."""

    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row
        self.state = CellState()


class Board:
    """Minesweeper board state and rules.

    Responsibilities:
    - Generate and place mines with first-click safety
    - Compute adjacency counts for every cell
    - Reveal cells (iterative flood fill when adjacent == 0)
    - Toggle flags, check win/lose conditions
    """

    def __init__(self, cols: int, rows: int, mines: int):
        self.cols = cols
        self.rows = rows
        self.num_mines = mines
        self.cells: List[Cell] = [Cell(c, r) for r in range(rows) for c in range(cols)]
        self._mines_placed = False
        self.revealed_count = 0
        self.game_over = False
        self.win = False

    def index(self, col: int, row: int) -> int:
        """Return the flat list index for (col,row)."""
        return row * self.cols + col

    def is_inbounds(self, col: int, row: int) -> bool:
        return 0 <= col < self.cols and 0 <= row < self.rows

    def neighbors(self, col: int, row: int) -> List[Tuple[int, int]]:
        deltas = [
            (-1, -1), (0, -1), (1, -1),
            (-1,  0),           (1, 0),
            (-1,  1), (0, 1),  (1, 1),
        ]
        results = []
        for dx, dy in deltas:
            nc, nr = col + dx, row + dy
            if self.is_inbounds(nc, nr):
                results.append((nc, nr))
        return results
    
    def place_mines(self, safe_col: int, safe_row: int) -> None:

        all_positions = [(c, r) for r in range(self.rows) for c in range(self.cols)]

        forbidden = {(safe_col, safe_row)} | set(self.neighbors(safe_col, safe_row))

        pool = [p for p in all_positions if p not in forbidden]
        random.shuffle(pool)

        for i in range(self.num_mines):
            c, r = pool[i]
            self.cells[self.index(c, r)].state.is_mine = True

        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.cells[self.index(c, r)].state
                if cell.is_mine:
                    continue
                count = 0
                for nc, nr in self.neighbors(c, r):
                    if self.cells[self.index(nc, nr)].state.is_mine:
                        count += 1
                cell.adjacent = count

        self._mines_placed = True

    def reveal(self, col: int, row: int) -> None:
        if not self.is_inbounds(col, row) or self.game_over:
            return

        cell = self.cells[self.index(col, row)].state

        if cell.is_revealed:
            return

        if not self._mines_placed:
            self.place_mines(col, row)

        if cell.is_flagged:
            return

        if cell.is_mine:
            cell.is_revealed = True
            self.game_over = True
            self._reveal_all_mines()
            return

        to_visit = [(col, row)]
        while to_visit:
            c, r = to_visit.pop()
            curr = self.cells[self.index(c, r)].state

            if curr.is_revealed or curr.is_flagged:
                continue

            curr.is_revealed = True
            self.revealed_count += 1

            if curr.adjacent == 0:
                for nc, nr in self.neighbors(c, r):
                    neigh = self.cells[self.index(nc, nr)].state
                    if not neigh.is_revealed and not neigh.is_flagged and not neigh.is_mine:
                        to_visit.append((nc, nr))

        self._check_win()

    def toggle_flag(self, col: int, row: int) -> None:
        if not self.is_inbounds(col, row):
            return

        cell = self.cells[self.index(col, row)].state

        if cell.is_revealed:
            return

        cell.is_flagged = not cell.is_flagged

    def flagged_count(self) -> int:
        # TODO: Return current number of flagged cells.
        pass

    def _reveal_all_mines(self) -> None:
        """Reveal all mines; called on game over."""
        for cell in self.cells:
            if cell.state.is_mine:
                cell.state.is_revealed = True

    def _check_win(self) -> None:
        """Set win=True when all non-mine cells have been revealed."""
        total_cells = self.cols * self.rows
        if self.revealed_count == total_cells - self.num_mines and not self.game_over:
            self.win = True
            for cell in self.cells:
                if not cell.state.is_revealed and not cell.state.is_mine:
                    cell.state.is_revealed = True
