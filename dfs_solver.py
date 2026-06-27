# -*- coding: utf-8 -*-
"""
dfs_solver.py
Cài đặt thuật toán Depth-First Search (DFS) để giải Sudoku 9x9.

Ý tưởng áp dụng DFS vào Sudoku:
    - State: bảng Sudoku tại một thời điểm.
    - Action: chọn ô trống đầu tiên, thử điền số hợp lệ (1..9).
    - Frontier: Stack (LIFO) — đi sâu nhất trước, quay lui khi gặp ngõ cụt.
    - Goal: bảng đã điền đầy đủ và hợp lệ.
    - DFS tiết kiệm bộ nhớ O(b·m) nhưng không đảm bảo tối ưu.
    - Bản chất giống Backtracking khi áp dụng cho Sudoku.
"""

import copy
from sudoku_utils import is_valid, find_empty_cells, SIZE


class SearchStep:
    """Một bước trong quá trình tìm kiếm."""
    def __init__(self, board, row, col, value, action_type, depth):
        self.board = copy.deepcopy(board)
        self.row = row
        self.col = col
        self.value = value
        self.action_type = action_type   # 'try' | 'backtrack'
        self.depth = depth


class DFSSolver:
    """
    Thuật toán Depth-First Search áp dụng cho Sudoku.

    Cách dùng:
        solver = DFSSolver(puzzle)
        solution_board, steps, stats = solver.solve()
    """

    def __init__(self, puzzle):
        self.puzzle = copy.deepcopy(puzzle)
        self.steps = []
        self.nodes_expanded = 0

    def solve(self):
        """
        Chạy DFS dùng đệ quy (implicit stack).
        Trả về (solution_board hoặc None, steps, stats).
        """
        board = copy.deepcopy(self.puzzle)
        found = self._dfs(board, 0)

        stats = {
            'nodes_expanded': self.nodes_expanded,
            'total_steps_recorded': len(self.steps),
        }
        if found:
            return board, self.steps, stats
        return None, self.steps, stats

    def _dfs(self, board, depth):
        empties = find_empty_cells(board)
        if not empties:
            return True  # Goal!

        row, col = empties[0]
        self.nodes_expanded += 1

        for num in range(1, 10):
            if is_valid(board, row, col, num):
                board[row][col] = num
                self.steps.append(SearchStep(board, row, col, num, 'try', depth + 1))

                if self._dfs(board, depth + 1):
                    return True

                # Backtrack
                board[row][col] = 0
                self.steps.append(SearchStep(board, row, col, 0, 'backtrack', depth))

        return False


if __name__ == "__main__":
    from sudoku_utils import generate_puzzle, board_to_string, is_solved

    puzzle, solution = generate_puzzle(num_clues=40, seed=42)
    print("Đề bài:")
    print(board_to_string(puzzle))
    print()

    solver = DFSSolver(puzzle)
    result, steps, stats = solver.solve()

    if result:
        print("Đã giải xong bằng DFS!")
        print(board_to_string(result))
        print(f"Thống kê: {stats}")
        print(f"Hợp lệ: {is_solved(result)}")
    else:
        print("Không tìm được lời giải.")
