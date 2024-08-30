"""
A Maze generator and solver using python.
Inspired by this repository: https://github.com/YeyoM/mazeSolver
"""

import random
import dataclasses
import enum
import collections

class COLORS(enum.Enum):
    wall: str = "🧱"
    visited: str = "🟥"
    empty: str = "🟦"

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

    def __repr__(self) -> str:
        return f"{int(self.wall.up)}{int(self.wall.down)}{int(self.wall.left)}{int(self.wall.right)}"

class Maze:
    def __init__(self, M: int, N: int) -> None:
        self.M, self.N = M, N
        self.grid: list[list[Cell]] = [[Cell(i, j) for j in range(N)] for i in range(M)]
        self.carve()

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
                        lower_cell_upper_wall = self.grid[ux][uy].wall.up if 0 <= ux < self.M else True
                        assert upper_cell_lower_wall == lower_cell_upper_wall, "walls not updated correctly"
                        print(COLORS.wall if upper_cell_lower_wall else COLORS.visited if self.grid[lx][ly].visited else COLORS.empty, end="")
                    # Vertical wall
                    else:
                        (rx, ry), (lx, ly) = (i // 2, (j + 1) // 2), (i // 2, (j - 1) // 2)
                        right_cell_left_wall = self.grid[rx][ry].wall.left if 0 <= ry < self.N else True
                        left_cell_right_wall = self.grid[lx][ly].wall.right if 0 <= ly < self.N else True
                        assert right_cell_left_wall == left_cell_right_wall, "walls not updated correctly"
                        print(COLORS.wall if right_cell_left_wall else COLORS.visited if self.grid[lx][ly].visited else COLORS.empty, end="")
            print()

    def carve(self) -> None:
        """
        Carve a path along the maze randomly going the DFS or BFS way, neighbours
        are picked randomly as well. Keep nodes on a deque until there are unvisited neighbours to it.
        Keep iterating until there are elements left to visit.
        """
        def get_neighbours(x: int, y: int) -> list[tuple[int, int]]:
            result: list[tuple[int, int]] = []
            for x_, y_ in ((x, y - 1), (x, y + 1), (x + 1, y), (x - 1, y)):
                if (x_, y_) in unvisited:
                    result.append((x_, y_))
            return result

        unvisited: set[tuple[int, int]] = {(i, j) for j in range(self.N) for i in range(self.M)}
        to_visit: collections.deque[tuple[int, int]] = collections.deque([(random.randint(0, self.M - 1), random.randint(0, self.N - 1))])
        unvisited.remove(to_visit[-1])
        while to_visit:
            cx, cy = to_visit[-1]
            unvisited_neighbours: list[tuple[int, int]] = get_neighbours(cx, cy)
            if not unvisited_neighbours:
                to_visit.pop()
            else:
                # Randomly pick an unvisited neighbour
                nx, ny = random.choice(unvisited_neighbours)
                unvisited.remove((nx, ny))

                # Randomly switch between DFS / BFS
                if random.random() < 0.5:
                    to_visit.append((nx, ny))
                else:
                    to_visit.appendleft((nx, ny))

                # Down
                if cx < nx:
                    self.grid[cx][cy].wall.down = self.grid[nx][ny].wall.up = False
                # Up
                elif cx > nx:
                    self.grid[cx][cy].wall.up = self.grid[nx][ny].wall.down = False
                # Right
                elif cy < ny:
                    self.grid[cx][cy].wall.right = self.grid[nx][ny].wall.left = False
                # Left
                else:
                    self.grid[cx][cy].wall.left = self.grid[nx][ny].wall.right = False

# +++++++++++++++++ MAIN FUNCTION +++++++++++++++++ #

if __name__ == "__main__":
    maze = Maze(10, 10)
    maze.print()
