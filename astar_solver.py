# -*- coding: utf-8 -*-
"""
astar_solver.py
Cài đặt thuật toán A* Search để giải Sudoku 9x9.

Ý tưởng áp dụng A* vào Sudoku:
    - f(n) = g(n) + h(n)
        + g(n) = số ô đã điền (chi phí từ gốc)
        + h(n) = số ô trống còn lại (heuristic admissible)
    - Frontier: Priority Queue theo f(n).
    - A* đảm bảo OPTIMAL nếu h(n) admissible & consistent.
    - Dead-end detection: h = ∞ nếu có ô trống không có candidate.
"""

import copy
import heapq
from sudoku_utils import is_valid, find_empty_cells, SIZE, candidates_for_cell


class SearchStep:
    def __init__(self, board, row, col, value, action_type, depth, f_value, g_value, h_value):
        self.board = copy.deepcopy(board)
        self.row = row
        self.col = col
        self.value = value
        self.action_type = action_type
        self.depth = depth
        self.f_value = f_value
        self.g_value = g_value
        self.h_value = h_value


class AStarSolver:
    """
    A* Search áp dụng cho Sudoku.
    f(n) = g(n) + h(n), g = ô đã điền, h = ô trống.
    """

    def __init__(self, puzzle):
        self.puzzle = copy.deepcopy(puzzle)
        self.steps = []
        self.nodes_expanded = 0

    def _heuristic(self, board):
        empties = find_empty_cells(board)
        if not empties:
            return 0
        for r, c in empties:
            if not candidates_for_cell(board, r, c):
                return float('inf')
        return len(empties)

    def solve(self):
        initial = copy.deepcopy(self.puzzle)
        h0 = self._heuristic(initial)
        if h0 == 0:
            return initial, self.steps, self._stats(0)

        num_given = sum(1 for r in range(SIZE) for c in range(SIZE) if initial[r][c] != 0)
        g0 = num_given
        f0 = g0 + h0

        counter = 0
        frontier = [(f0, h0, counter, initial, g0)]
        explored = set()
        max_frontier = 1

        while frontier:
            f_val, h_val, _, board, g_val = heapq.heappop(frontier)
            if h_val == float('inf'):
                continue

            state_key = self._board_key(board)
            if state_key in explored:
                continue
            explored.add(state_key)
            self.nodes_expanded += 1

            empties = find_empty_cells(board)
            if not empties:
                self.steps.append(SearchStep(board, -1, -1, 0, 'solved', g_val, f_val, g_val, 0))
                return board, self.steps, self._stats(max_frontier)

            empties.sort(key=lambda rc: len(candidates_for_cell(board, rc[0], rc[1])))
            row, col = empties[0]

            for num in sorted(candidates_for_cell(board, row, col)):
                new_board = copy.deepcopy(board)
                new_board[row][col] = num
                new_g = g_val + 1
                new_h = self._heuristic(new_board)
                if new_h != float('inf'):
                    new_f = new_g + new_h
                    counter += 1
                    heapq.heappush(frontier, (new_f, new_h, counter, new_board, new_g))
                    self.steps.append(SearchStep(new_board, row, col, num, 'try',
                                                  new_g, new_f, new_g, new_h))

            max_frontier = max(max_frontier, len(frontier))

        return None, self.steps, self._stats(max_frontier)

    def _board_key(self, board):
        return tuple(tuple(row) for row in board)

    def _stats(self, max_frontier):
        return {
            'nodes_expanded': self.nodes_expanded,
            'max_frontier_size': max_frontier,
            'total_steps_recorded': len(self.steps),
        }


if __name__ == "__main__":
    from sudoku_utils import generate_puzzle, board_to_string, is_solved

    puzzle, solution = generate_puzzle(num_clues=55, seed=42)
    print("Đề bài:")
    print(board_to_string(puzzle))
    print()

    solver = AStarSolver(puzzle)
    result, steps, stats = solver.solve()

    if result:
        print("Đã giải xong bằng A*!")
        print(board_to_string(result))
        print(f"Thống kê: {stats}")
        print(f"Hợp lệ: {is_solved(result)}")
    else:
        print("Không tìm được lời giải.")
