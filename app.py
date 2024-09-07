import argparse
import curses
import maze as mz

def main(stdscr: curses.window) -> None:

    def render(spl_cells: set[tuple[int, int]], color: str) -> None:
        """
        Helper to render the board to screen
        """
        main_window.clear()
        for i in range(X):
            for j in range(Y):
                main_window.addstr(i, j, display_matrix[i][j] if (i, j) not in spl_cells else color)
        main_window.refresh()

    def display_overlay(screen: curses.window, options: list[str], prompt: str) -> str:
        """
        Helper function to display overlays on top of specified window.
        Waits until user enters a valid choice.
        """
        screen.clear()
        screen.addstr(0, 0, prompt)
        for idx, option in enumerate(options):
            screen.addstr(idx + 1, 0, f"{idx + 1}. {option}")
            screen.refresh()

        while True:
            ch = screen.getch()
            if ord('1') <= ch <= ord(str(len(options))):
                return options[ch - ord('1')]

    def start_game():
        """
        Initializes a new maze post prompt of maze configurations
        """
        # Show overlay for choosing the generator algorithm
        generator_options = ["wilson", "kruskal", "prim", "ellers", "backtracking"]
        allow_multiple_paths_option = ["Yes", "No"]

        maze_gen_algorithm = display_overlay(main_window, generator_options, "Choose a maze generator:")
        multiple_paths = display_overlay(main_window, allow_multiple_paths_option, "Allow multiple paths?")

        # Initialize the maze based on the selected algorithm and path option
        maze = mz.Maze(int((ROWS - PADDING_Y) * .45), int((COLS - PADDING_X) * .25), generator_algorithm=maze_gen_algorithm, multiple_paths=(multiple_paths == "Yes"))
        return maze

    def toggle_solution(solved: bool):
        """
        Solves the maze starting from user's current position.
        """
        nonlocal display_matrix # type: ignore
        if not solved:
            # Show overlay for choosing the generator algorithm
            solver_options = ["dijkstra", "a_star", "dead_end_filling"]
            maze_solver_algorithm = display_overlay(main_window, solver_options, "Choose a maze solver:")
            maze.solve(maze_solver_algorithm, (CURR[0] // 2, CURR[1] // 2), (maze.M - 1, maze.N - 1))
        else:
            maze.unsolve()

        # Refreshing out view
        display_matrix = maze.board

    # There is no proper typing support in curses for mypy
    # This is added merely for type hint support and never gets executed
    if not stdscr:
        stdscr = curses.initscr()

    # Hide cursor and set no delay to prevent overloading CPU
    curses.curs_set(False)
    stdscr.nodelay(False)

    # Get and define the screen dimensions
    ROWS, COLS = stdscr.getmaxyx()
    PADDING_X, PADDING_Y = 4, 6

    # Game would contain two windows - game / options and info
    main_window = curses.newwin(ROWS - PADDING_Y, COLS - PADDING_X, PADDING_Y // 2, PADDING_X // 2)
    info_window = curses.newwin(2, COLS - PADDING_X, ROWS - (PADDING_Y // 2), PADDING_X // 2)
    main_window.keypad(True)
    info_window.keypad(True)

    # Initialize the maze
    SOLVED = False
    maze = start_game()

    # Display game info / hints
    info_window.addstr(0, 0, "Use Arrow Keys to navigate, 'H' for Help, 'Q' to Quit.")
    info_window.refresh()

    # Some maze related data variables for rendering maze
    display_matrix: list[list[str]] = maze.board
    X, Y = len(display_matrix), len(display_matrix[0])
    CURR, DEST = (1, 1), (X - 2, Y - 2)
    render({CURR, DEST}, mz.COLORS.current.value)

    while CURR != DEST:
        ch = main_window.getch()

        if ch == curses.KEY_DOWN or ch == ord('j'):
            NEXT = (CURR[0] + 1, CURR[1])
        elif ch == curses.KEY_UP or ch == ord('k'):
            NEXT = (CURR[0] - 1, CURR[1])
        elif ch == curses.KEY_LEFT or ch == ord('h'):
            NEXT = (CURR[0], CURR[1] - 1)
        elif ch == curses.KEY_RIGHT or ch == ord('l'):
            NEXT = (CURR[0], CURR[1] + 1)
        elif ch == ord("H"):
            toggle_solution(SOLVED)
            SOLVED = not SOLVED
            NEXT = CURR
        elif ch == ord("Q"):
            break
        else:
            continue

        if display_matrix[NEXT[0]][NEXT[1]] != mz.COLORS.wall.value:
            CURR = NEXT
            render({CURR, DEST}, mz.COLORS.current.value)

    # Clear all display just the maze and prepare to quit
    maze.unsolve()
    display_matrix = maze.board
    render({DEST}, mz.COLORS.empty.value)
    info_window.clear()
    info_window.addstr(0, 0, "Press any key to close.")
    info_window.refresh()
    ch = main_window.getch()

if __name__ == "__main__":
    curses.wrapper(main)
