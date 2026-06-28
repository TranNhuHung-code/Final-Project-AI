# -*- coding: utf-8 -*-
"""
idastar_solver.py
Cài đặt thuật toán IDA* (Iterative Deepening A*) để giải Sudoku 9x9.

Ý tưởng áp dụng IDA* vào Sudoku:
    - State: bảng Sudoku tại một thời điểm (điền một phần).
    - g(n): số ô đã điền được tính từ trạng thái ban đầu (độ sâu hiện tại).
    - h(n): heuristic ước lượng "khoảng cách" còn lại đến goal. Ta dùng
      heuristic_min_conflicts_domain (trong sudoku_utils.py): với mỗi ô
      trống, tính số lựa chọn hợp lệ còn lại (domain size); ô có domain
      nhỏ (ít lựa chọn) sẽ "tốn điểm" heuristic nhiều hơn -> ưu tiên xử lý
      các ô bị ràng buộc chặt trước (ý tưởng giống Minimum Remaining
      Values - MRV trong CSP), giúp phát hiện nhánh chết (dead-end) sớm.
    - f(n) = g(n) + h(n).
    - Thay vì tăng giới hạn ĐỘ SÂU như IDS, IDA* tăng dần ngưỡng GIÁ TRỊ
      f (f-limit). Tại mỗi vòng lặp, DFS sẽ cắt bỏ (prune) ngay các nhánh
      có f(n) > f-limit hiện tại, và ghi nhận giá trị f nhỏ nhất bị cắt
      để làm f-limit cho vòng lặp kế tiếp.

Đây là cài đặt có sinh "trace" để phục vụ trực quan hóa từng bước.
"""

import copy
from sudoku_utils import is_valid, find_empty_cells, heuristic_min_conflicts_domain, SIZE


class SearchStep:
    def __init__(self, board, row, col, value, action_type, detail="", **kwargs):
        import copy
        self.board = copy.deepcopy(board)
        self.row = row
        self.col = col
        self.value = value
        self.action_type = action_type
        self.detail = detail
        for k, v in kwargs.items():
            setattr(self, k, v)




class IDAStarSolver:
    """
    Thuật toán IDA* áp dụng cho Sudoku.

    Cách dùng:
        solver = IDAStarSolver(puzzle)
        solution_board, steps, stats = solver.solve()
    """

    def __init__(self, puzzle):
        self.puzzle = copy.deepcopy(puzzle)
        self.steps = []
        self.nodes_expanded = 0

    def _f_value(self, board, g):
        h = heuristic_min_conflicts_domain(board)
        if h == float('inf'):
            return float('inf')
        return g + h

    def _search(self, board, g, f_limit):
        """
        DFS có cắt nhánh theo f-limit (lõi của IDA*).
        Trả về:
            ('found', None)        -> đã giải xong
            ('failure', min_f_exceeded) -> không có lời giải trong nhánh này;
                                            min_f_exceeded là giá trị f nhỏ
                                            nhất đã bị cắt (None nếu không có)
        """
        empties = find_empty_cells(board)
        if not empties:
            return 'found', None

        f = self._f_value(board, g)
        if f > f_limit:
            return 'failure', f  # nhánh này bị cắt vì f vượt ngưỡng

        row, col = empties[0]
        min_exceeded = None

        for num in range(1, 10):
            self.nodes_expanded += 1
            if is_valid(board, row, col, num):
                board[row][col] = num
                new_f = self._f_value(board, g + 1)
                self.steps.append(SearchStep(board, row, col, num, 'try', detail=f"Pop node. Thử ({row},{col}) = {num}. F={new_f}, Limit={f_limit}.", new_f=new_f, f_limit=f_limit))

                result, exceeded = self._search(board, g + 1, f_limit)

                if result == 'found':
                    return 'found', None

                if exceeded is not None and (min_exceeded is None or exceeded < min_exceeded):
                    min_exceeded = exceeded

                board[row][col] = 0
                self.steps.append(SearchStep(board, row, col, 0, 'backtrack', detail=f"F={new_f} > Limit={f_limit} hoặc vô nghiệm. Quay lui.", new_f=new_f, f_limit=f_limit))

        return 'failure', min_exceeded

    def solve(self, max_iterations=200):
        """
        Chạy IDA*: f_limit khởi đầu = h(root). Sau mỗi vòng lặp thất bại,
        f_limit được cập nhật thành giá trị f nhỏ nhất đã bị cắt ở vòng đó.
        """
        f_limit = self._f_value(self.puzzle, 0)
        iterations = 0

        while iterations < max_iterations:
            iterations += 1
            board = copy.deepcopy(self.puzzle)
            self.steps.append(SearchStep(board, -1, -1, 0, 'new_iteration', detail=f"Tăng Limit mới = {f_limit}. Xóa Frontier cũ, lặp lại.", new_f=None, f_limit=f_limit))

            result, min_exceeded = self._search(board, 0, f_limit)

            if result == 'found':
                stats = {
                    'final_f_limit': f_limit,
                    'iterations': iterations,
                    'nodes_expanded': self.nodes_expanded,
                    'total_steps_recorded': len(self.steps),
                }
                return board, self.steps, stats

            if min_exceeded is None or min_exceeded == float('inf'):
                # Không còn nhánh nào để mở rộng -> bài toán vô nghiệm
                break

            f_limit = min_exceeded  # tăng ngưỡng f cho vòng lặp kế tiếp

        stats = {
            'final_f_limit': f_limit,
            'iterations': iterations,
            'nodes_expanded': self.nodes_expanded,
            'total_steps_recorded': len(self.steps),
        }
        return None, self.steps, stats


if __name__ == "__main__":
    from sudoku_utils import generate_puzzle, board_to_string, is_solved
    import time

    # Vì IDA* với heuristic MRV mạnh hơn IDS rất nhiều, ta có thể test
    # với độ khó cao hơn (nhiều ô trống hơn) mà vẫn chạy nhanh.
    puzzle, real_solution = generate_puzzle(num_clues=45, seed=11)
    print("Đề bài:")
    print(board_to_string(puzzle))
    print()

    solver = IDAStarSolver(puzzle)
    t0 = time.time()
    solution, steps, stats = solver.solve()
    t1 = time.time()

    if solution:
        print("Đã giải xong bằng IDA*!")
        print(board_to_string(solution))
        print()
        print("Thống kê:", stats)
        print("Thời gian:", round(t1 - t0, 4), "giây")
        print("Kết quả có hợp lệ không?", is_solved(solution))
    else:
        print("Không tìm được lời giải.")
        print("Thống kê:", stats)
