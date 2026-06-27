# -*- coding: utf-8 -*-
"""
ids_solver.py
Cài đặt thuật toán Iterative Deepening Search (IDS) để giải Sudoku 9x9.

Ý tưởng áp dụng IDS vào Sudoku:
    - State (trạng thái): bảng Sudoku tại một thời điểm (có thể điền một phần).
    - Action (hành động): chọn ô trống ĐẦU TIÊN theo thứ tự duyệt trái->phải,
      trên->dưới, rồi thử điền một số hợp lệ (1..9) vào ô đó.
    - Initial state: đề bài (puzzle) ban đầu.
    - Goal test: bảng đã điền đầy đủ và không vi phạm luật Sudoku nào.
    - Depth limit: vì mỗi action chỉ điền đúng 1 ô, nên lời giải luôn nằm ở
      độ sâu CHÍNH XÁC bằng số ô trống ban đầu. IDS sẽ tăng dần giới hạn
      l = 1, 2, 3, ... cho đến khi tìm được lời giải (hoặc đến limit tối đa).

Đây là cài đặt có sinh "trace" (vết các bước duyệt) để phục vụ trực quan hóa
từng bước trên giao diện Tkinter.
"""

import copy
from sudoku_utils import is_valid, find_empty_cells, SIZE


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




class IDSSolver:
    """
    Thuật toán Iterative Deepening Search áp dụng cho Sudoku.

    Cách dùng:
        solver = IDSSolver(puzzle)
        solution_board, steps, stats = solver.solve(max_depth_limit=60)
    """

    def __init__(self, puzzle):
        self.puzzle = copy.deepcopy(puzzle)
        self.steps = []           # Lưu lại toàn bộ vết duyệt để minh họa
        self.nodes_expanded = 0   # Số node đã mở rộng (để đánh giá hiệu năng)

    # ---------- Depth-Limited Search dùng làm "lõi" cho IDS ----------
    def _depth_limited_search(self, board, depth_limit):
        """
        DFS có giới hạn độ sâu. Trả về:
            'found'  -> đã tìm thấy lời giải (board được cập nhật tại chỗ)
            'cutoff' -> hết giới hạn độ sâu nhưng còn nhánh chưa duyệt
            'failure'-> duyệt hết cây con này mà không có lời giải
        """
        empties = find_empty_cells(board)

        # Goal test: không còn ô trống nào => đã giải xong
        if not empties:
            return 'found'

        # Cutoff test: đã chạm giới hạn độ sâu mà vẫn còn ô trống
        if depth_limit <= 0:
            return 'cutoff'

        row, col = empties[0]   # luôn chọn ô trống đầu tiên theo thứ tự duyệt
        current_depth = (SIZE * SIZE) - len(empties)  # số ô đã điền = độ sâu hiện tại

        cutoff_occurred = False

        for num in range(1, 10):
            self.nodes_expanded += 1
            if is_valid(board, row, col, num):
                board[row][col] = num
                self.steps.append(SearchStep(board, row, col, num, 'try', detail=f"DLS Depth={depth}. Pop từ Stack, đánh dấu Explored. Mở rộng ({row},{col})={num}.",
                                              current_depth + 1, depth_limit))

                result = self._depth_limited_search(board, depth_limit - 1)

                if result == 'found':
                    return 'found'
                elif result == 'cutoff':
                    cutoff_occurred = True

                # Quay lui (backtrack): undo nước đi vừa thử
                board[row][col] = 0
                self.steps.append(SearchStep(board, row, col, 0, 'backtrack', detail=f"DLS Depth={depth}. Nhánh vô nghiệm hoặc quá sâu, Quay lui (Backtrack).",
                                              current_depth, depth_limit))

        return 'cutoff' if cutoff_occurred else 'failure'

    # ---------- Iterative Deepening: tăng dần giới hạn độ sâu ----------
    def solve(self, max_depth_limit=None):
        """
        Chạy IDS: với l = 1, 2, 3, ..., gọi Depth-Limited-Search(problem, l)
        cho đến khi tìm được lời giải hoặc vượt max_depth_limit.

        Trả về (solution_board hoặc None, steps, stats)
        """
        num_empty = len(find_empty_cells(self.puzzle))
        if max_depth_limit is None:
            max_depth_limit = num_empty  # với Sudoku, lời giải luôn ở đúng độ sâu = số ô trống

        for depth_limit in range(1, max_depth_limit + 1):
            board = copy.deepcopy(self.puzzle)
            self.steps.append(SearchStep(board, -1, -1, 0, 'new_iteration', detail=f"Bắt đầu Iteration mới với Max Depth={depth_limit}. Reset Frontier.",
                                          0, depth_limit))

            result = self._depth_limited_search(board, depth_limit)

            if result == 'found':
                stats = {
                    'final_depth_limit': depth_limit,
                    'nodes_expanded': self.nodes_expanded,
                    'total_steps_recorded': len(self.steps),
                }
                return board, self.steps, stats

        # Không tìm được lời giải trong giới hạn cho phép
        stats = {
            'final_depth_limit': max_depth_limit,
            'nodes_expanded': self.nodes_expanded,
            'total_steps_recorded': len(self.steps),
        }
        return None, self.steps, stats


if __name__ == "__main__":
    # Test nhanh thuật toán bằng một đề rất ít ô trống để chạy nhanh
    from sudoku_utils import generate_puzzle, board_to_string, is_solved

    # Vì IDS rất chậm với nhiều ô trống (độ phức tạp ~ 9^d), ta test với
    # một đề CHỈ thiếu vài ô để minh họa thuật toán chạy đúng trong thời gian hợp lý.
    puzzle, real_solution = generate_puzzle(num_clues=78, seed=7)  # chỉ 3 ô trống
    print("Đề bài (puzzle) -- chỉ vài ô trống để demo IDS nhanh:")
    print(board_to_string(puzzle))
    print()

    solver = IDSSolver(puzzle)
    solution, steps, stats = solver.solve()

    if solution:
        print("Đã giải xong bằng IDS!")
        print(board_to_string(solution))
        print()
        print("Thống kê:", stats)
        print("Kết quả có hợp lệ không?", is_solved(solution))
    else:
        print("Không tìm được lời giải.")
        print("Thống kê:", stats)
