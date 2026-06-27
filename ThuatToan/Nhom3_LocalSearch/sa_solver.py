# -*- coding: utf-8 -*-
"""
sa_solver.py
Cài đặt thuật toán Simulated Annealing (Luyện kim giả lập) để giải Sudoku 9x9.

Ý tưởng áp dụng Simulated Annealing vào Sudoku:
    Khác với các thuật toán tìm kiếm trên cây (BFS/DFS/IDS/A*/IDA*) xây dựng
    lời giải dần dần từng ô, Local Search bắt đầu với một LỜI GIẢI ĐẦY ĐỦ
    (có thể sai luật) rồi liên tục cải thiện nó.

    - State (trạng thái): một bảng Sudoku đã điền ĐẦY ĐỦ 81 ô, trong đó:
        + Các ô đề bài (clue) giữ cố định, không đổi.
        + Mỗi HÀNG được đảm bảo luôn chứa đủ và không trùng các số 1-9
          (bằng cách điền ngẫu nhiên các số còn thiếu của hàng đó vào các
          ô trống, không vi phạm ràng buộc HÀNG).
        + Ràng buộc CỘT và KHUNG 3x3 có thể đang bị vi phạm.
    - h(n) - hàm đánh giá: tổng số cặp xung đột (số bị trùng) trên tất cả
      cột và khung 3x3 (hàm count_conflicts trong sudoku_utils.py).
      h(n) = 0 <=> đã giải xong bài toán.
    - Neighbor (lân cận): hoán đổi giá trị của HAI Ô TRỐNG (không phải ô
      đề bài) NẰM TRÊN CÙNG MỘT HÀNG. Việc giới hạn hoán đổi trong cùng
      hàng giúp luôn duy trì tính hợp lệ của ràng buộc hàng trong suốt
      quá trình tìm kiếm, chỉ còn phải tối ưu cột & khung.
    - Delta (Δ) = h(neighbor) - h(current). Nếu Δ < 0 (lân cận tốt hơn),
      luôn chấp nhận. Nếu Δ >= 0 (lân cận tệ hơn hoặc bằng), chấp nhận với
      xác suất p = exp(-Δ / T) -- đây chính là điểm khác biệt cốt lõi giúp
      Simulated Annealing thoát khỏi cực tiểu địa phương (local minimum)
      so với Hill Climbing thông thường.
    - T (nhiệt độ) giảm dần theo lịch trình làm lạnh (cooling schedule):
      T = T0 ban đầu, sau mỗi bước T = alpha * T (alpha < 1), dừng khi
      T < Tmin hoặc đã tìm được lời giải (h(n) = 0).
"""

import copy
import math
import random
from sudoku_utils import SIZE, BOX, count_conflicts, is_solved


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




class SimulatedAnnealingSolver:
    """
    Thuật toán Simulated Annealing áp dụng cho Sudoku.

    Cách dùng:
        solver = SimulatedAnnealingSolver(puzzle)
        solution_board, steps, stats = solver.solve()
    """

    def __init__(self, puzzle, T0=2.0, T_min=0.01, alpha=0.999, max_steps=60000, max_restarts=8):
        self.puzzle = copy.deepcopy(puzzle)
        self.T0 = T0
        self.T_min = T_min
        self.alpha = alpha
        self.max_steps = max_steps
        # Simulated Annealing thuần đôi khi mắc ở cực tiểu địa phương khi
        # ràng buộc Sudoku quá chặt (không hạ được h(n) về 0 trước khi T
        # nguội hết). Random-restart là kỹ thuật bổ trợ phổ biến: nếu một
        # lượt chạy không hội tụ, khởi tạo lại trạng thái ngẫu nhiên mới
        # và chạy lại, lặp tối đa max_restarts lần.
        self.max_restarts = max_restarts

        self.steps = []
        self.is_clue = [[puzzle[r][c] != 0 for c in range(SIZE)] for r in range(SIZE)]

    # ---------- Khởi tạo trạng thái ban đầu: điền đầy mỗi hàng hợp lệ theo hàng ----------
    def _init_random_board(self):
        board = copy.deepcopy(self.puzzle)
        for r in range(SIZE):
            existing = set(board[r])
            missing = [n for n in range(1, 10) if n not in existing]
            random.shuffle(missing)
            idx = 0
            for c in range(SIZE):
                if board[r][c] == 0:
                    board[r][c] = missing[idx]
                    idx += 1
        return board

    def _empty_cols_in_row(self, row):
        """Trả về danh sách cột không phải ô đề bài (clue) trong hàng `row`."""
        return [c for c in range(SIZE) if not self.is_clue[row][c]]

    def solve(self):
        rows_with_freedom = [r for r in range(SIZE) if len(self._empty_cols_in_row(r)) >= 2]

        if not rows_with_freedom:
            current = self._init_random_board()
            current_h = count_conflicts(current)
            stats = {'steps': 0, 'final_h': current_h, 'final_temperature': self.T0,
                     'restarts': 0, 'total_steps_recorded': 0}
            return (current if current_h == 0 else None), self.steps, stats

        total_step_count = 0
        restart_count = 0

        while restart_count < self.max_restarts:
            result_board, current_h, step_count, final_T = self._run_one_attempt(rows_with_freedom)
            total_step_count += step_count

            if current_h == 0:
                stats = {
                    'steps': total_step_count,
                    'final_h': 0,
                    'best_h_found': 0,
                    'final_temperature': round(final_T, 6),
                    'restarts': restart_count,
                    'total_steps_recorded': len(self.steps),
                }
                return result_board, self.steps, stats

            restart_count += 1
            if restart_count < self.max_restarts:
                self.steps.append(SearchStep(result_board, -1, -1, -1,
                                              'restart', current_h, self.T0))

        # Hết số lần restart cho phép mà vẫn chưa hội tụ về 0 xung đột
        stats = {
            'steps': total_step_count,
            'final_h': current_h,
            'best_h_found': current_h,
            'final_temperature': round(final_T, 6),
            'restarts': restart_count,
            'total_steps_recorded': len(self.steps),
        }
        return None, self.steps, stats

    def _run_one_attempt(self, rows_with_freedom):
        """Chạy một lượt Simulated Annealing đầy đủ (từ T0 nguội dần đến T_min
        hoặc đến khi hội tụ). Trả về (board, h_cuối, số_bước, T_cuối)."""
        current = self._init_random_board()
        current_h = count_conflicts(current)
        T = self.T0
        step_count = 0

        best_board = copy.deepcopy(current)
        best_h = current_h

        while T > self.T_min and step_count < self.max_steps and current_h > 0:
            step_count += 1

            row = random.choice(rows_with_freedom)
            cols = self._empty_cols_in_row(row)
            c1, c2 = random.sample(cols, 2)

            neighbor = copy.deepcopy(current)
            neighbor[row][c1], neighbor[row][c2] = neighbor[row][c2], neighbor[row][c1]
            neighbor_h = count_conflicts(neighbor)

            delta = neighbor_h - current_h

            if delta < 0:
                current = neighbor
                current_h = neighbor_h
                action = 'accept_better'
            else:
                p = math.exp(-delta / T) if T > 1e-12 else 0
                if random.random() < p:
                    current = neighbor
                    current_h = neighbor_h
                    action = 'accept_worse'
                else:
                    action = 'reject'

            if current_h < best_h:
                best_h = current_h
                best_board = copy.deepcopy(current)

            if step_count % 3 == 0 or action == 'accept_better':
                self.steps.append(SearchStep(
                    current if action != 'reject' else neighbor,
                    row, c1, c2, action, current_h if action != 'reject' else neighbor_h, T
                ))

            T = T * self.alpha

        return (current if current_h == 0 else best_board), min(current_h, best_h), step_count, T


if __name__ == "__main__":
    from sudoku_utils import generate_puzzle, board_to_string
    import time

    puzzle, real_solution = generate_puzzle(num_clues=32, seed=21)
    print("Đề bài:")
    print(board_to_string(puzzle))
    print()

    solver = SimulatedAnnealingSolver(puzzle, T0=2.0, T_min=0.01, alpha=0.9995, max_steps=200000)
    t0 = time.time()
    solution, steps, stats = solver.solve()
    t1 = time.time()

    print("Thống kê:", stats)
    print("Thời gian:", round(t1 - t0, 4), "giây")

    if solution:
        print("Đã giải xong bằng Simulated Annealing!")
        print(board_to_string(solution))
        print("Hợp lệ:", is_solved(solution))
    else:
        print("Chưa hội tụ đến lời giải hoàn chỉnh (đặc điểm của Local Search: "
              "có thể bị mắc ở cực tiểu địa phương hoặc cần nhiều bước hơn / "
              "lịch trình làm lạnh chậm hơn).")
