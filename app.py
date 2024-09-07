import argparse
import curses
import maze as mz

def main(stdscr: curses.window) -> None:

    def render(spl_cells: set[tuple[int, int]], color: str) -> None:
        stdscr.clear()
        for i in range(X):
            for j in range(Y):
                stdscr.addstr(i, j, display_matrix[i][j] if (i, j) not in spl_cells else color)
        stdscr.refresh()

    # There is no proper typing support in curses for mypy
    # This is added merely for type hint support and never gets executed
    if not stdscr:
        stdscr = curses.initscr()

    curses.curs_set(0)

    # Initialize the maze
    maze = mz.Maze(25, 50)


    display_matrix: list[list[str]] = maze.board
    X, Y = len(display_matrix), len(display_matrix[0])
    CURR, DEST = (1, 1), (X - 2, Y - 2)
    render({CURR, DEST}, mz.COLORS.visited.value)

    while CURR != DEST:
        ch = stdscr.getch()
        if ch == curses.KEY_DOWN:
            NEXT = (CURR[0] + 1, CURR[1])
        elif ch == curses.KEY_UP:
            NEXT = (CURR[0] - 1, CURR[1])
        elif ch == curses.KEY_LEFT:
            NEXT = (CURR[0], CURR[1] - 1)
        elif ch == curses.KEY_RIGHT:
            NEXT = (CURR[0], CURR[1] + 1)

        if display_matrix[NEXT[0]][NEXT[1]] != mz.COLORS.wall.value:
            CURR = NEXT
            render({CURR, DEST}, mz.COLORS.visited.value)

    render({DEST}, mz.COLORS.empty.value)
    ch = stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)
