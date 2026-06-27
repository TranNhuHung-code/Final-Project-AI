# -*- coding: utf-8 -*-
"""
greedy_solver.py
Cài đặt thuật toán Greedy Best-First Search để giải Sudoku 9x9.

Ý tưởng áp dụng Greedy vào Sudoku:
    - State: bảng Sudoku tại một thời điểm.
    - h(n): số ô trống còn lại — ưu tiên trạng thái gần hoàn thành nhất.
    - Frontier: Priority Queue sắp xếp theo h(n).
    - Nhanh hơn BFS nhưng KHÔNG đảm bảo tối ưu.
    - Dead-end detection: h = ∞ nếu có ô trống không có giá trị hợp lệ.
"""

import copy
import heapq
from sudoku_utils import is_valid, find_empty_cells, SIZE, candidates_for_cell


class SearchStep:
    def __init__(self, board, row, col, value, action_type, depth, h_value):
        self.board = copy.deepcopy(board)
        self.row = row
        self.col = col
        self.value = value
        self.action_type = action_type
        self.depth = depth
        self.h_value = h_value


class GreedySolver:
    """
    Greedy Best-First Search áp dụng cho Sudoku.
    Frontier ưu tiên theo h(n) = số ô trống còn lại.
    """

    def __init__(self, puzzle):
        self.puzzle = copy.deepcopy(puzzle)
        self.steps = []
        self.nodes_expanded = 0

    def _heuristic(self, board):
        """h(n) = số ô trống. Nếu dead-end (ô trống không có candidate) → ∞."""
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
            return initial, self.steps, {'nodes_expanded': 0, 'total_steps_recorded': 0}

        counter = 0
        frontier = [(h0, counter, initial, 0)]
        explored = set()
        max_frontier = 1

        while frontier:
            h_val, _, board, depth = heapq.heappop(frontier)
            if h_val == float('inf'):
                continue

            state_key = self._board_key(board)
            if state_key in explored:
                continue
            explored.add(state_key)
            self.nodes_expanded += 1

            empties = find_empty_cells(board)
            if not empties:
                self.steps.append(SearchStep(board, -1, -1, 0, 'solved', depth, 0))
                return board, self.steps, self._stats(max_frontier)

            # Chọn ô có ít candidate nhất (MRV-like)
            empties.sort(key=lambda rc: len(candidates_for_cell(board, rc[0], rc[1])))
            row, col = empties[0]

            for num in sorted(candidates_for_cell(board, row, col)):
                new_board = copy.deepcopy(board)
                new_board[row][col] = num
                h = self._heuristic(new_board)
                if h != float('inf'):
                    counter += 1
                    heapq.heappush(frontier, (h, counter, new_board, depth + 1))
                    self.steps.append(SearchStep(new_board, row, col, num, 'try', depth + 1, h))

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

    solver = GreedySolver(puzzle)
    result, steps, stats = solver.solve()

    if result:
        print("Đã giải xong bằng Greedy Best-First!")
        print(board_to_string(result))
        print(f"Thống kê: {stats}")
        print(f"Hợp lệ: {is_solved(result)}")
    else:
        print("Không tìm được lời giải.")
