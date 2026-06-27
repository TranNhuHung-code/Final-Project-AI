# -*- coding: utf-8 -*-
"""
partial_observable_solver.py
Cài đặt thuật toán Searching for Partially Observable Problems áp dụng cho
Sudoku 9x9, mô phỏng một "agent" với cảm biến (sensor) bị hạn chế.

----------------------------------------------------------------------------
MÔ HÌNH HÓA BÀI TOÁN:
    Trong bài toán Sudoku thông thường, agent quan sát được TOÀN BỘ bảng
    (fully-observable). Ở đây ta mô phỏng lại một biến thể PARTIALLY
    OBSERVABLE: agent KHÔNG được nhìn thấy lời giải đầy đủ ngay từ đầu,
    mà tại mỗi bước, sensor của agent chỉ cho phép "quan sát" (percept)
    giá trị thật của ĐÚNG MỘT Ô duy nhất được chọn ngẫu nhiên trong số các
    ô mà agent còn chưa biết chắc giá trị.

    - Belief state b: tập hợp tất cả các bảng Sudoku (đầy đủ, hợp lệ) còn
      KHẢ DĨ (consistent) với toàn bộ thông tin agent đã quan sát được
      cho đến hiện tại + các ràng buộc Sudoku đã suy luận được.
      Vì việc lưu trữ literal mọi bảng khả dĩ là không khả thi (có thể
      lên đến hàng triệu khả năng), ta dùng cách biểu diễn RÚT GỌN: với
      mỗi ô, lưu DOMAIN (tập giá trị còn khả dĩ cho ô đó) — đây là cách
      biểu diễn belief-state phổ biến và hiệu quả cho các bài toán dạng
      lưới ràng buộc (constraint-grid).
    - Percept (tri giác): tại mỗi bước, sensor trả về giá trị CHÍNH XÁC
      của một ô (row, col) được chọn ngẫu nhiên trong số các ô mà domain
      hiện tại vẫn còn > 1 khả năng.
    - Update belief state: sau khi nhận percept (ô (r,c) thực ra có giá
      trị v), ta:
        1) Thu hẹp domain của (r, c) về đúng {v}.
        2) Lan truyền ràng buộc (constraint propagation / forward
           checking): loại bỏ v khỏi domain của tất cả các ô cùng hàng,
           cùng cột, cùng khung 3x3 với (r, c).
        3) Lặp lại việc kiểm tra: bất kỳ ô nào domain chỉ còn 1 giá trị
           thì giá trị đó coi như được "biết chắc", tiếp tục lan truyền.
    - Goal test: belief state đã thu hẹp về DUY NHẤT 1 trạng thái khả dĩ,
      nghĩa là mọi ô đều có domain kích thước 1 (agent đã suy luận/biết
      chắc toàn bộ bảng dù sensor chỉ cho quan sát từng ô một).

    Đây là minh họa rất sát với khái niệm "coercion"/sensorless suy luận
    dần belief-state trong giáo trình AI (Russell & Norvig, chương
    Searching in Complex Environments).
----------------------------------------------------------------------------
"""

import copy
import random
from sudoku_utils import SIZE, BOX, is_valid


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




class PartiallyObservableSolver:
    """
    Thuật toán tìm kiếm trong môi trường QUAN SÁT ĐƯỢC MỘT PHẦN, áp dụng
    cho Sudoku: agent chỉ "nhìn" được 1 ô/lượt, phải duy trì và thu hẹp
    BELIEF STATE (miền giá trị khả dĩ của từng ô) cho đến khi suy luận ra
    toàn bộ bảng.

    Cách dùng:
        solver = PartiallyObservableSolver(puzzle, real_solution)
        solution_board, steps, stats = solver.solve()
    """

    def __init__(self, puzzle, real_solution):
        self.puzzle = copy.deepcopy(puzzle)
        # real_solution: lời giải THẬT của đề bài, dùng để mô phỏng "sensor"
        # trả lời đúng giá trị thật khi agent quan sát một ô. Đây KHÔNG phải
        # là agent "gian lận" nhìn trộm lời giải, mà là quy ước mô phỏng môi
        # trường: trong thực tế, sensor vật lý của agent (ví dụ camera quét
        # từng ô) sẽ trả về đúng giá trị thật tại ô đó.
        self.real_solution = real_solution
        self.steps = []

    def _init_domains(self):
        """Domain ban đầu: ô đề bài (clue) đã biết chắc -> domain = {giá trị
        đó}. Ô trống -> domain = mọi giá trị còn hợp lệ theo ràng buộc hiện
        có của đề bài (suy luận ban đầu trước khi quan sát thêm gì cả)."""
        domains = [[None] * SIZE for _ in range(SIZE)]
        for r in range(SIZE):
            for c in range(SIZE):
                if self.puzzle[r][c] != 0:
                    domains[r][c] = {self.puzzle[r][c]}
                else:
                    domains[r][c] = {n for n in range(1, 10)
                                      if is_valid(self.puzzle, r, c, n)}
        return domains

    def _propagate(self, domains, row, col, value):
        """Lan truyền ràng buộc sau khi biết chắc (row, col) = value:
        loại bỏ `value` khỏi domain của các ô cùng hàng/cột/khung."""
        affected = []
        peers = self._get_peers(row, col)
        for (r, c) in peers:
            if value in domains[r][c] and len(domains[r][c]) > 1:
                domains[r][c].discard(value)
                affected.append((r, c))
        return affected

    def _get_peers(self, row, col):
        peers = set()
        for c in range(SIZE):
            if c != col:
                peers.add((row, c))
        for r in range(SIZE):
            if r != row:
                peers.add((r, col))
        box_row, box_col = (row // BOX) * BOX, (col // BOX) * BOX
        for r in range(box_row, box_row + BOX):
            for c in range(box_col, box_col + BOX):
                if (r, c) != (row, col):
                    peers.add((r, c))
        return peers

    def _cascade_singletons(self, domains):
        """Sau khi lan truyền, có thể một số ô domain bị thu hẹp về đúng 1
        giá trị (singleton) -> coi như agent đã 'suy luận chắc chắn' được
        giá trị đó dù chưa quan sát trực tiếp, và tiếp tục lan truyền tiếp
        (giống AC-3 / constraint propagation đơn giản hóa)."""
        changed_any = True
        all_affected = []
        while changed_any:
            changed_any = False
            for r in range(SIZE):
                for c in range(SIZE):
                    if len(domains[r][c]) == 1:
                        value = next(iter(domains[r][c]))
                        affected = self._propagate(domains, r, c, value)
                        if affected:
                            all_affected.extend(affected)
                            changed_any = True
        return all_affected

    def solve(self, max_observations=500):
        domains = self._init_domains()

        # Lan truyền ban đầu dựa trên các ô đề bài đã cho
        for r in range(SIZE):
            for c in range(SIZE):
                if self.puzzle[r][c] != 0:
                    self._propagate(domains, r, c, self.puzzle[r][c])
        self._cascade_singletons(domains)

        num_unknown = sum(1 for r in range(SIZE) for c in range(SIZE) if len(domains[r][c]) > 1)
        self.steps.append(SearchStep(domains, None, None, [], 'init', num_unknown))

        observations_made = 0

        while num_unknown > 0 and observations_made < max_observations:
            # Agent CHỈ được sensor quan sát đúng 1 ô còn chưa chắc (domain > 1)
            unknown_cells = [(r, c) for r in range(SIZE) for c in range(SIZE)
                              if len(domains[r][c]) > 1]
            if not unknown_cells:
                break

            row, col = random.choice(unknown_cells)
            true_value = self.real_solution[row][col]
            observations_made += 1

            # Cập nhật belief-state: thu hẹp domain ô vừa quan sát về đúng 1 giá trị
            domains[row][col] = {true_value}
            self.steps.append(SearchStep(domains, (row, col), true_value, [],
                                          'observe', num_unknown - 1))

            # Lan truyền ràng buộc trực tiếp
            affected = self._propagate(domains, row, col, true_value)
            # Lan truyền dây chuyền (cascade) các ô vừa trở thành singleton
            cascade_affected = self._cascade_singletons(domains)
            all_affected = affected + cascade_affected

            num_unknown = sum(1 for r in range(SIZE) for c in range(SIZE) if len(domains[r][c]) > 1)

            if all_affected:
                self.steps.append(SearchStep(domains, (row, col), true_value,
                                              all_affected, 'propagate', num_unknown))

        solved = (num_unknown == 0)
        solution_board = None
        if solved:
            solution_board = [[next(iter(domains[r][c])) for c in range(SIZE)]
                               for r in range(SIZE)]
            self.steps.append(SearchStep(domains, None, None, [], 'solved', 0))

        stats = {
            'observations_made': observations_made,
            'total_cells': SIZE * SIZE,
            'cells_given_as_clue': sum(1 for row in self.puzzle for v in row if v != 0),
            'solved': solved,
            'total_steps_recorded': len(self.steps),
        }
        return solution_board, self.steps, stats


if __name__ == "__main__":
    from sudoku_utils import generate_puzzle, board_to_string, is_solved
    import time

    puzzle, real_solution = generate_puzzle(num_clues=30, seed=5)
    print("Đề bài (agent chỉ biết các ô màu xám này lúc đầu):")
    print(board_to_string(puzzle))
    print()

    solver = PartiallyObservableSolver(puzzle, real_solution)
    t0 = time.time()
    solution, steps, stats = solver.solve()
    t1 = time.time()

    print("Thống kê:", stats)
    print("Thời gian:", round(t1 - t0, 4), "giây")

    if solution:
        print("Agent đã suy luận ra toàn bộ bảng sau khi quan sát từng ô!")
        print(board_to_string(solution))
        print("Hợp lệ:", is_solved(solution))
        print(f"Agent chỉ cần QUAN SÁT TRỰC TIẾP {stats['observations_made']} ô "
              f"(trong tổng số {81 - stats['cells_given_as_clue']} ô trống) nhờ "
              f"lan truyền ràng buộc suy luận ra phần còn lại.")
