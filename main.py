"""
A Maze generator and solver using python.
Inspired by this repository: https://github.com/YeyoM/mazeSolver
"""

import random
import dataclasses
import enum

class COLORS(enum.Enum):
    wall: str = "🧱"
    visited: str = "🟥"
    empty: str = "🟩"

    def __str__(self) -> str:
        return self.value

@dataclasses.dataclass
class Wall:
    up: bool = True
    down: bool = True
    left: bool = True
    right: bool = True

class Cell:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.wall = Wall()
        self.visited = False

class Maze:
    def __init__(self, M: int, N: int) -> None:
        self.M, self.N = M, N
        self.grid: list[list[Cell]] = [[Cell(i, j) for j in range(N)] for i in range(M)]

    def print(self) -> None:
        for i in range(2 * self.M + 1):
            for j in range(2 * self.N + 1):
                # If both are even, definitely wall
                if i % 2 == 0 and j % 2 == 0:
                    print(COLORS.wall, end="")
                # If both are odd definitely free cell
                elif i % 2 == 1 and j % 2 == 1:
                    print(COLORS.visited if self.grid[i // 2][j // 2].visited else COLORS.empty, end="")
                else:
                    # Horizontal wall
                    if i % 2 == 0:
                        (ux, uy), (lx, ly) = ((i + 1) // 2, j // 2), ((i - 1) // 2, j // 2)
                        upper_cell_lower_wall = self.grid[lx][ly].wall.down if 0 <= lx < self.M else True
                        lower_cell_upper_wall = self.grid[ux][uy].wall.down if 0 <= ux < self.M else True
                        assert upper_cell_lower_wall == lower_cell_upper_wall, "walls not updated correctly"
                        print(COLORS.wall if upper_cell_lower_wall else COLORS.visited if self.grid[lx][ly].visited else COLORS.empty, end="")
                    # Vertical wall
                    else:
                        (rx, ry), (lx, ly) = (i // 2, (j + 1) // 2), (i // 2, (j - 1) // 2)
                        right_cell_left_wall = self.grid[rx][ry].wall.down if 0 <= ry < self.N else True
                        left_cell_right_wall = self.grid[lx][ly].wall.down if 0 <= ly < self.N else True
                        assert right_cell_left_wall == left_cell_right_wall, "walls not updated correctly"
                        print(COLORS.wall if right_cell_left_wall else COLORS.visited if self.grid[lx][ly].visited else COLORS.empty, end="")
            print()

    def carve(self) -> None:
        pass

# +++++++++++++++++ MAIN FUNCTION +++++++++++++++++ #

if __name__ == "__main__":
    maze = Maze(5, 5)
    maze.print()
