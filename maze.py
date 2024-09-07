"""
A Maze generator and solver using python.
Inspired by this repository: https://github.com/YeyoM/mazeSolver
"""

import random
import dataclasses
import enum
import collections
import DSU
import heapq
import math
import typing

class COLORS(enum.Enum):
    wall: str = "🧱"
    visited: str = "🟥"
    empty: str = "🟦"

    def __str__(self) -> str:
        return self.value

class Cell:

    @dataclasses.dataclass
    class Wall:
        up: bool = True
        down: bool = True
        left: bool = True
        right: bool = True

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.wall = Cell.Wall()
        self.visited = False

    def __repr__(self) -> str:
        return f"{int(self.wall.up)}{int(self.wall.down)}{int(self.wall.left)}{int(self.wall.right)}"

class Maze:
    def __init__(self, M: int, N: int) -> None:
        self.M, self.N = M, N
        self.grid: list[list[Cell]] = [[Cell(i, j) for j in range(N)] for i in range(M)]
        self.generate()
        self.add_multiple_paths()
        # self.solve()

    def break_wall(self, cx: int, cy: int, nx: int, ny: int) -> None:
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

    def has_wall(self, cx: int, cy: int, nx: int, ny: int) -> bool:
        # Down
        if cx < nx:
            assert self.grid[cx][cy].wall.down == self.grid[nx][ny].wall.up
            return self.grid[cx][cy].wall.down
        # Up
        elif cx > nx:
            assert self.grid[cx][cy].wall.up == self.grid[nx][ny].wall.down
            return self.grid[cx][cy].wall.up
        # Right
        elif cy < ny:
            assert self.grid[cx][cy].wall.right == self.grid[nx][ny].wall.left
            return self.grid[cx][cy].wall.right
        # Left
        else:
            assert self.grid[cx][cy].wall.left == self.grid[nx][ny].wall.right
            return self.grid[cx][cy].wall.left

    def get_neighbours(self, x: int, y: int) -> list[tuple[int, int]]:
        result: list[tuple[int, int]] = []
        for x_, y_ in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]:
            if 0 <= x_ < self.M and 0 <= y_ < self.N:
                result.append((x_, y_))
        return result

    def generate(self) -> None:
        # self.generate_DFS_BFS()
        self.generate_wilson()
        # self.generate_randomized_kruskal()
        # self.generate_randomized_prim()
        # self.generate_ellers()

    def generate_randomized_prim(self) -> None:
        """
        Step 1: Initialize the maze by choosing a random starting cell.

        Step 2: Mark the starting cell as part of the maze and add its neighboring cells
        to the frontier set.

        Step 3: While there are cells in the frontier set, perform the following steps:
            a. Randomly pop a cell from the frontier set.
            b. Select a random neighbor of the popped cell, that is already part of the maze and break the wall between them.
            c. Mark the selected frontier cell as part of the maze and add its neighboring cells into the frontier set
            if they are not already part of the maze.

        Step 4: Continue until there are no cells left in the frontier set
        """
        def add_frontiers(x: int, y: int, frontiers: set[tuple[int, int]]) -> None:
            for x_, y_ in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
                if 0 <= x_ < self.M and 0 <= y_ < self.N and (x_, y_) not in part_of_maze:
                    frontiers.add((x_, y_))

        sx, sy = random.randint(0, self.M - 1), random.randint(0, self.N - 1)
        part_of_maze: set[tuple[int, int]] = {(sx, sy)}
        frontiers: set[tuple[int, int]] = set()
        add_frontiers(sx, sy, frontiers)
        while frontiers:
            # Pick a random frontier
            cx, cy = random.choice(tuple(frontiers))
            frontiers.remove((cx, cy))

            # Pick a random neighbour already part of maze
            nx, ny = random.choice(list(filter(lambda x: x in part_of_maze, self.get_neighbours(cx, cy))))
            self.break_wall(cx, cy, nx, ny)

            # Add all the neighbouring cells not part of the maze for cx, cy
            # as frontiers themselves
            part_of_maze.add((cx, cy))
            add_frontiers(cx, cy, frontiers)

    def generate_ellers(self, horizontal_merge_prob: float = 0.5, vertical_merge_prob: float = 0.5) -> None:
        """
        Step 1: Iterate row wise.

        Step 2: Going from left to right (column wise), if the current cell and the
        next cell are in different sets, randomly decide to connect to the next cell.
        If they connect, merge the cells sets together.

        Step 4: Initialize the next row. For each set in the current row, connect
        downward for at least one cell per set, adding that cell to the set it connected from.

        Step 5: Move to the next row and repeat steps 2 through 4.

        Step 6: When on the last row, repeat step 3 but remove the randomness,
        always connecting to the next cell if it's in a different set.
        Don't make any downward connections.
        """
        # DSU to keep track of which set each cell belongs to
        dsu: DSU.DisjointSet[tuple[int, int]] = DSU.DisjointSet(self.M, self.N)
        for i in range(self.M):

            # For all rows except the last
            if i < self.M - 1:
                # Iterate from left to right, keeping track of set each cell drops into
                groups: collections.defaultdict[tuple[int, int], list[tuple[int, int]]] = collections.defaultdict(list)
                for j in range(self.N):
                    # If current cell and next cell and part of diff sets, randomly choose to join them
                    if j + 1 < self.N and dsu.get_ultimate_parent((i, j)) != dsu.get_ultimate_parent((i, j + 1)) and random.random() < horizontal_merge_prob:
                        dsu.union((i, j), (i, j + 1))
                        self.break_wall(i, j, i, j + 1)
                    groups[dsu.get_ultimate_parent((i, j))].append((i, j))

                # Make sure that from each group atleast one cell has a open door downwards
                for group in groups.values():
                    random.shuffle(group)
                    cx, cy = group.pop()

                    # Mandatorily ensure atleast one cell has opening downwards
                    self.break_wall(cx, cy, cx + 1, cy)
                    dsu.union((cx, cy), (cx + 1, cy))

                    # Randomly break wall downwards for same group
                    for cx, cy in group:
                        if random.random() < vertical_merge_prob:
                            self.break_wall(cx, cy, cx + 1, cy)
                            dsu.union((cx, cy), (cx + 1, cy))

            # For the last row, ensure that all disjoint sets are connected
            else:
                for j in range(self.N - 1):
                    # If disjoint, no randomness simply join them together
                    if dsu.get_ultimate_parent((i, j)) != dsu.get_ultimate_parent((i, j + 1)):
                        dsu.union((i, j), (i, j + 1))
                        self.break_wall(i, j, i, j + 1)

    def generate_randomized_kruskal(self) -> None:
        """
        Step 1: Initialize a Disjoint Set Union (DSU) structure to keep track of which
        set each cell belongs to.

        Step 2: Create a list of all potential edges (connections) between adjacent cells
        in the grid.

        Step 3: Randomly shuffle the list of edges to ensure a random selection order.

        Step 4: While there are edges remaining in the list, perform the following steps:
            a. Pop an edge from the list.
            b. Check if the cells connected by this edge belong to different sets.
            c. If they belong to different sets, break the wall between the two cells and
            merge their sets in the DSU.
            d. If they belong to the same set, discard the edge without breaking the wall
            to avoid creating loops.

        Step 5: Continue until all edges have been processed
        """
        dsu: DSU.DisjointSet[tuple[int, int]] = DSU.DisjointSet(self.M, self.N)
        # Store all the edges that could be removed
        edges: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for x in range(self.M):
            for y in range(self.N):
                for x_, y_ in [(x + 1, y), (x, y + 1)]:
                    if 0 <= x_ < self.M and 0 <= y_ < self.N:
                        edges.append(((x, y), (x_, y_)))

        # Randomly pop edges
        random.shuffle(edges)
        while edges:
            (cx, cy), (nx, ny) = edges.pop()
            # We only remove the wall between the cells 
            # if they are not already part of same `set`
            # This is done so that the maze doesn't have
            # any loops
            if dsu.union((cx, cy), (nx, ny)):
                self.break_wall(cx, cy, nx, ny)

    def generate_wilson(self) -> None:
        """
        Step 1: Choose a random cell and mark it as part of the maze.

        Step 2: Create a set of all unvisited cells.

        Step 3: While there are unvisited cells, perform the following steps:
            a. Select a random unvisited cell and start a random walk until you reach
            a cell that is already part of the maze.
            b. Track the path taken during the random walk to detect loops and prevent
            revisiting the same cell within the current walk.
            c. Once the walk reaches a cell that is part of the maze, carve a path
            from the start of the walk to the end by breaking walls between consecutive cells.
            d. Add all cells in the current walk to the maze and remove them from the
            unvisited set.
            e. Note that by keep track of the latest visited node for each cell in the walk until
            we reach a node already part of maze, we can carve path without loops

        Step 4: Continue until there are no unvisited cells left
        """
        part_of_maze: set[tuple[int, int]] = {(random.randint(0, self.M - 1), random.randint(0, self.N - 1))}
        unvisited: set[tuple[int, int]] = {(i, j) for i in range(self.M) for j in range(self.N) if (i, j) not in part_of_maze}
        while unvisited:
            # Pick a random coord and continue visiting random neighbours
            # until we visit a node that is already part of the maze
            sx, sy = cx, cy = next(iter(unvisited))
            visited: dict[tuple[int, int], tuple[int, int]] = {}
            while (cx, cy) not in part_of_maze:
                nx, ny = random.choice(self.get_neighbours(cx, cy))
                visited[(cx, cy)] = (nx, ny)
                cx, cy = nx, ny

            # Starting from sx, sy - visit the final node part
            # of the maze clearing all walls in between
            cx, cy = sx, sy
            while (cx, cy) not in part_of_maze:
                unvisited.remove((cx, cy))
                part_of_maze.add((cx, cy))
                nx, ny = visited[(cx, cy)]

                # Break the wall between these two points
                self.break_wall(cx, cy, nx, ny)

                cx, cy = nx, ny

    def generate_DFS_BFS(self, split_percent: float = 0.5) -> None:
        """
        Step 1: Carve a path along the maze randomly going the DFS or BFS way

        Step 2: Neighbours are picked randomly. Keep nodes on a deque without removing
        it until there are unvisited neighbours to it.

        Step 3: Keep iterating until there are elements left to visit.
        """
        unvisited: set[tuple[int, int]] = {(i, j) for j in range(self.N) for i in range(self.M)}
        to_visit: collections.deque[tuple[int, int]] = collections.deque([(random.randint(0, self.M - 1), random.randint(0, self.N - 1))])
        unvisited.remove(to_visit[-1])
        while to_visit:
            cx, cy = to_visit[-1]
            unvisited_neighbours: list[tuple[int, int]] = list(filter(lambda x: x in unvisited, self.get_neighbours(cx, cy)))
            if not unvisited_neighbours:
                to_visit.pop()
            else:
                # Randomly pick an unvisited neighbour
                nx, ny = random.choice(unvisited_neighbours)
                unvisited.remove((nx, ny))

                # Randomly switch between DFS / BFS
                if random.random() < split_percent:
                    to_visit.append((nx, ny))
                else:
                    to_visit.appendleft((nx, ny))

                # Break the wall between these two points
                self.break_wall(cx, cy, nx, ny)

    def add_multiple_paths(self, trials: int|None = None) -> None:
        """
        Randomly selects a cell and tries to break down a wall in an attempt to create
        additional paths to the existing single path maze solution
        """
        if not trials:
            trials = int(0.1 * self.M * self.N)

        assert trials <= self.M * self.N
        while trials:
            cx, cy = random.randint(0, self.M - 1), random.randint(0, self.N - 1)
            neighbours_with_walls = list(filter(lambda x: self.has_wall(x[0], x[1], cx, cy), self.get_neighbours(cx, cy)))
            if neighbours_with_walls:
                nx, ny = random.choice(neighbours_with_walls)
                self.break_wall(cx, cy, nx, ny)
                trials -= 1

    def solve(self) -> None:
        # self.solve_DFS_BFS()
        # self.solve_dijkstra()
        self.solve_a_star()
        # self.solve_dead_end_filling()

    def solve_DFS_BFS(self, mode: str = "BFS") -> None:
        # Source, destination
        source, destination = self.grid[0][0], self.grid[self.M - 1][self.N - 1]

        # While to_visit not empty keep visiting all unvisited neighbours
        # stopping if we encounter the destination node
        to_visit: collections.deque[Cell] = collections.deque([source])
        prev_visited: dict[Cell, Cell] = {source: source}
        while to_visit:
            curr = to_visit.pop() if mode == "DFS" else to_visit.popleft()
            if (curr.x, curr.y) == (self.M - 1, self.N - 1):
                break
            else:
                neighbours: list[Cell] = []
                if not curr.wall.down:
                    neighbours.append(self.grid[curr.x + 1][curr.y])
                if not curr.wall.up:
                    neighbours.append(self.grid[curr.x - 1][curr.y])
                if not curr.wall.left:
                    neighbours.append(self.grid[curr.x][curr.y - 1])
                if not curr.wall.right:
                    neighbours.append(self.grid[curr.x][curr.y + 1])
                for neighbour in neighbours:
                    if neighbour not in prev_visited:
                        to_visit.append(neighbour)
                        prev_visited[neighbour] = curr

        # Mark the shortest path from destination to source as visited
        curr = destination
        curr.visited = True
        while curr != source:
            curr = prev_visited[curr]
            curr.visited = True

    def solve_dijkstra(self) -> None:
        """
        This algorithm only makes sense when there are multiple paths between source and destination.
        Would still work for unique paths but would function the same as a BFS and would be overkill (slower due to log N ops)

        Step 1: Assign distances from source to all remaining nodes as infinity
        Step 2: Initialize a heap with node value as source, we can reach source at a distance of 0
        Step 3: Iterate through all possible neighbours of curr node that could be visited, add to the heap only if the cost + 1 is lesser than the existing path already discovered.
        Step 4: Repeat until destination is reached.
        """
        source, destination = (0, 0), (self.M - 1, self.N - 1)
        heap: list[tuple[float, tuple[int, int]]] = [(0, source)]
        distances: collections.defaultdict[tuple[int, int], float] = collections.defaultdict(lambda: math.inf, {source: 0})
        prev_visited: dict[tuple[int, int], tuple[int, int]] = {}
        while heap:
            cost, (cx, cy) = heapq.heappop(heap)
            neighbours_without_walls = list(filter(lambda x: not self.has_wall(x[0], x[1], cx, cy), self.get_neighbours(cx, cy)))
            for (nx, ny) in neighbours_without_walls:
                if distances[(nx, ny)] > cost + 1:
                    distances[(nx, ny)] = cost + 1
                    prev_visited[(nx, ny)] = (cx, cy)
                    heapq.heappush(heap, (cost + 1, (nx, ny)))
            if (cx, cy) == destination:
                break

        # Mark the shortest path from destination to source as visited
        cx, cy = destination
        self.grid[cx][cy].visited = True
        while (cx, cy) != source:
            cx, cy = prev_visited[(cx, cy)]
            self.grid[cx][cy].visited = True

    def solve_a_star(self) -> None:
        """
        Same as dijkstra but uses a hueristic to find the destination quicker.
        While dijkstra keeps track of just the cost to reach curr from source,
        A* keeps track of approx cost from curr node to destination.
        Each time we pick the node with better sum of `G + H` (cost from source + cost to dest)

        Heuristic = approximation
        Video explanation: https://www.youtube.com/watch?v=ySN5Wnu88nE (computerphile)
        """

        source, destination = (0, 0), (self.M - 1, self.N - 1)

        # Using manhattan distance for heuristic calculation (H value)
        dist: typing.Callable[[tuple[int, int], tuple[int, int]], float] = lambda x, y: abs(x[0] - y[0]) + abs(x[1] - y[1])

        # Same as dijkstra but include cost to destination as well
        distances: collections.defaultdict[tuple[int, int], float] = collections.defaultdict(lambda: math.inf, {source: 0})
        prev_visited: dict[tuple[int, int], tuple[int, int]] = dict()
        heap: list[tuple[float, float, tuple[int, int]]] = [(dist(source, destination), 0, source)]
        while heap:
            heuristic, cost, (cx, cy) = heapq.heappop(heap)
            neighbours_without_walls = list(filter(lambda x: not self.has_wall(x[0], x[1], cx, cy), self.get_neighbours(cx, cy)))
            for (nx, ny) in neighbours_without_walls:
                if distances[(nx, ny)] > cost + 1:
                    distances[(nx, ny)] = cost + 1
                    prev_visited[(nx, ny)] = (cx, cy)
                    heapq.heappush(heap, (dist((nx, ny), destination) + cost + 1, cost + 1, (nx, ny)))
            if (cx, cy) == destination:
                break

        # Mark the shortest path from destination to source as visited
        cx, cy = destination
        self.grid[cx][cy].visited = True
        while (cx, cy) != source:
            cx, cy = prev_visited[(cx, cy)]
            self.grid[cx][cy].visited = True

    def solve_dead_end_filling(self) -> None:
        """"
        Step 1. Identify Dead-Ends:
           - Traverse through the maze grid and identify all cells that are dead-ends.
           - A dead-end is defined as a cell surrounded by walls on three sides.
           - Exclude the source and destination cells from being marked as dead-ends.

        Step 2. Fill Non-Path Cells:
           - For each identified dead-end, trace back towards the nearest junction (a cell with more than one open path).
           - As you trace back, mark each cell as a non-path cell until you reach the junction.
           - This step effectively "fills in" dead-end paths that cannot lead to the destination.

        Step 3. Mark Valid Path Cells:
           - After processing all dead-ends, mark only the cells that are not part of the non-path set as valid path cells.
           - These cells are considered part of the solution and will be marked as visited.
       """

        source, destination = (0, 0), (self.M - 1, self.N - 1)

        # Check if the cell is a deadend (surrounded by wall on 3 sides)
        is_deadend: typing.Callable[[Cell], bool] = lambda x: sum((x.wall.up, x.wall.down, x.wall.left, x.wall.right)) == 3
        deadends: list[tuple[int, int]] = [(i, j) for i in range(self.M) for j in range(self.N) if is_deadend(self.grid[i][j]) and (i, j) != source and (i, j) != destination]

        # While there are deadends, pop from deadends and start filling until a first junction is hit
        non_path: set[tuple[int, int]] = set()
        while deadends:
            cx, cy = deadends.pop()
            neighbours = list(filter(lambda x: not self.has_wall(cx, cy, x[0], x[1]) and x not in non_path, self.get_neighbours(cx, cy)))
            non_path.add((cx, cy))
            while len(neighbours) == 1:
                non_path.add((cx, cy))
                cx, cy = neighbours.pop()
                if (cx, cy) != source and (cx, cy) != destination:
                    neighbours = list(filter(lambda x: not self.has_wall(cx, cy, x[0], x[1]) and x not in non_path, self.get_neighbours(cx, cy)))

        # Color only cells that are not in non path
        for i in range(self.M):
            for j in range(self.N):
                if (i, j) not in non_path:
                    self.grid[i][j].visited = True

    @property
    def board(self) -> list[list[str]]:
        """
        Logic to convert the maze into a more print friendly version
        """
        results: list[list[str]] = [[]]
        for i in range(2 * self.M + 1):
            for j in range(2 * self.N + 1):
                # If both are even, definitely wall
                if i % 2 == 0 and j % 2 == 0:
                    results[-1].append(COLORS.wall.value)
                # If both are odd definitely free cell
                elif i % 2 == 1 and j % 2 == 1:
                    results[-1].append(COLORS.visited.value if self.grid[i // 2][j // 2].visited else COLORS.empty.value)
                else:
                    # Horizontal wall
                    if i % 2 == 0:
                        (ux, uy), (lx, ly) = ((i + 1) // 2, j // 2), ((i - 1) // 2, j // 2)
                        upper_cell_lower_wall = self.grid[lx][ly].wall.down if 0 <= lx < self.M else True
                        lower_cell_upper_wall = self.grid[ux][uy].wall.up if 0 <= ux < self.M else True
                        assert upper_cell_lower_wall == lower_cell_upper_wall, "walls not updated correctly"
                        results[-1].append(COLORS.wall.value if upper_cell_lower_wall else COLORS.visited.value if self.grid[lx][ly].visited and self.grid[ux][uy].visited else COLORS.empty.value)
                    # Vertical wall
                    else:
                        (rx, ry), (lx, ly) = (i // 2, (j + 1) // 2), (i // 2, (j - 1) // 2)
                        right_cell_left_wall = self.grid[rx][ry].wall.left if 0 <= ry < self.N else True
                        left_cell_right_wall = self.grid[lx][ly].wall.right if 0 <= ly < self.N else True
                        assert right_cell_left_wall == left_cell_right_wall, "walls not updated correctly"
                        results[-1].append(COLORS.wall.value if right_cell_left_wall else COLORS.visited.value if self.grid[lx][ly].visited and self.grid[rx][ry].visited else COLORS.empty.value)
            results.append([])

        # Remove the last empty list we would have added
        results.pop()

        return results

    def print(self) -> None:
        """
        Logic to print the maze to the console
        """
        display_matrix: list[list[str]] = self.board
        for i in range(len(display_matrix)):
            for j in range(len(display_matrix[0])):
                print(display_matrix[i][j], end="")
            print()

# +++++++++++++++++ MAIN FUNCTION +++++++++++++++++ #

if __name__ == "__main__":
    maze = Maze(20, 15)
    maze.print()
