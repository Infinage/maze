#include <algorithm>
#include <iostream>
#include <set>
#include <stack>
#include <vector>
#include <experimental/random>

using namespace std;

void printMaze(vector<vector<int>> &grid, int M, int N){
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < N; j++) {
            // 0 -> Empty
            if (grid[i][j] == 0)
                cout << "⬜";

            // 1 -> Travelled Path
            else if (grid[i][j] == 1)
                cout << "🟩";

            // 2 -> Obstacle
            else
                cout << "🟥";
        }
        cout << endl;
    }
}

bool checkCoord(vector<vector<int>> &grid, int M, int N, pair<int, int> coord) {
    int x = coord.first, y = coord.second;
    bool boundaryCheck = x > 0 && y > 0 && x < M - 1 && y < N - 1;
    if (!boundaryCheck) return false;
    else {
        int neighbourCounts = 0;
        for (int dx = -1; dx <= 1; dx++)
            for (int dy = -1; dy <= 1; dy++)
                if ((dx != 0 || dy != 0) && (grid[x + dx][y + dy] == 0))
                    neighbourCounts++;
        return neighbourCounts <= 2;
    }
}

void carveMaze(vector<vector<int>> &grid, int M, int N) {
    /*
     * Start walking simultaneously from 1, 1 and M - 2, N - 2
     * We would walk until these two paths meet
     * Make sure that we only visit a cell if it has utmost 3 colored neighbours (out of 8)
     */

    // Generator for random shuffle
    std::random_device random_dev;
    std::mt19937 generator(random_dev());

    // Directions that we can travel to
    vector<pair<int, int>> dirs({{-1, 0}, {0, -1}, {1, 0}, {0, 1}});

    // Start by marking the beginning and the destination as free
    grid[1][1] = 0, grid[M - 2][N - 2] = 0;

    stack<pair<int, int>> toVisit({{1, 1}, {M - 2, N - 2}});
    set<pair<int, int>> visited({{1, 1}, {M - 2, N - 2}});
    while (!toVisit.empty()) {
        printMaze(grid, M, N);
        pair<int, int> coord = toVisit.top();
        toVisit.pop();
        grid[coord.first][coord.second] = 0;
        shuffle(dirs.begin(), dirs.end(), generator);
        for (auto delta: dirs){
            pair<int, int> next = {coord.first + delta.first, coord.second + delta.second};
            if (visited.find(next) == visited.end() && checkCoord(grid, M, N, next)) {
                toVisit.push(next);
                visited.insert(next);
            }
        }
    }
}

int main(){
    int M, N;
    M = 5, N = 5;
    vector<vector<int>> grid(M, vector<int>(N, 2));
    carveMaze(grid, M, N);
    printMaze(grid, M, N);
}
