# -*- coding: utf-8 -*-
"""
bfs_solver.py
Cài đặt thuật toán Breadth-First Search (BFS) để giải Sudoku 9x9.

Ý tưởng áp dụng BFS vào Sudoku:
    - State: bảng Sudoku tại một thời điểm.
    - Action: chọn ô trống đầu tiên, thử điền số hợp lệ (1..9).
    - Frontier: Queue (FIFO) — duyệt theo chiều rộng (level by level).
    - Goal: bảng đã điền đầy đủ và hợp lệ.
    - BFS đảm bảo tìm lời giải NGẮN NHẤT (ít bước nhất).

    ⚠️ BFS rất tốn bộ nhớ (O(b^d)) — chỉ phù hợp đề ÍT ô trống.
"""

import copy
from collections import deque
from sudoku_utils import is_valid, find_empty_cells, SIZE


class SearchStep:
    """Một bước trong quá trình tìm kiếm, dùng để phát lại trên giao diện."""
    def __init__(self, board, row, col, value, action_type, depth):
        self.board = copy.deepcopy(board)
        self.row = row
        self.col = col
        self.value = value
        self.action_type = action_type   # 'try' | 'backtrack' | 'dequeue'
        self.depth = depth


class BFSSolver:
    """
    Thuật toán Breadth-First Search áp dụng cho Sudoku.

    Cách dùng:
        solver = BFSSolver(puzzle)
        solution_board, steps, stats = solver.solve()
    """

    def __init__(self, puzzle):
        self.puzzle = copy.deepcopy(puzzle)
        self.steps = []
        self.nodes_expanded = 0

    def solve(self):
        """
        Chạy BFS. Trả về (solution_board hoặc None, steps, stats).

        Frontier = deque chứa (board, depth).
        Mỗi bước: lấy board đầu queue, tìm ô trống đầu tiên,
        sinh tất cả trạng thái con (điền 1..9 hợp lệ), đẩy vào queue.
        """
        initial = copy.deepcopy(self.puzzle)
        empties = find_empty_cells(initial)
        if not empties:
            return initial, self.steps, {'nodes_expanded': 0, 'total_steps_recorded': 0}

        frontier = deque()
        frontier.append((initial, 0))

        while frontier:
            board, depth = frontier.popleft()
            self.nodes_expanded += 1

            empties = find_empty_cells(board)
            if not empties:
                # Goal: không còn ô trống
                self.steps.append(SearchStep(board, -1, -1, 0, 'solved', depth))
                stats = {
                    'nodes_expanded': self.nodes_expanded,
                    'max_frontier_size': len(frontier),
                    'total_steps_recorded': len(self.steps),
                }
                return board, self.steps, stats

            row, col = empties[0]

            for num in range(1, 10):
                if is_valid(board, row, col, num):
                    new_board = copy.deepcopy(board)
                    new_board[row][col] = num
                    self.steps.append(SearchStep(new_board, row, col, num, 'try', depth + 1))
                    frontier.append((new_board, depth + 1))

        stats = {
            'nodes_expanded': self.nodes_expanded,
            'max_frontier_size': 0,
            'total_steps_recorded': len(self.steps),
        }
        return None, self.steps, stats


if __name__ == "__main__":
    from sudoku_utils import generate_puzzle, board_to_string, is_solved

    puzzle, solution = generate_puzzle(num_clues=75, seed=42)
    print("Đề bài (rất ít ô trống để BFS chạy nhanh):")
    print(board_to_string(puzzle))
    print()

    solver = BFSSolver(puzzle)
    result, steps, stats = solver.solve()

    if result:
        print("Đã giải xong bằng BFS!")
        print(board_to_string(result))
        print(f"Thống kê: {stats}")
        print(f"Hợp lệ: {is_solved(result)}")
    else:
        print("Không tìm được lời giải.")
        print(f"Thống kê: {stats}")
