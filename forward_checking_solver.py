# -*- coding: utf-8 -*-
"""
forward_checking_solver.py
Cài đặt thuật toán Backtracking Search kết hợp kỹ thuật Forward Checking
để giải Sudoku 9x9 — biểu diễn dưới dạng bài toán CSP (Constraint
Satisfaction Problem).

----------------------------------------------------------------------------
MÔ HÌNH HÓA SUDOKU THÀNH BÀI TOÁN CSP:
    - Variables (Biến): mỗi ô trống (row, col) là một biến cần gán giá trị.
    - Domain (Miền giá trị): ban đầu mỗi biến có domain = {1, 2, ..., 9},
      sau đó bị thu hẹp dần bởi các ràng buộc.
    - Constraints (Ràng buộc): với mỗi hàng, mỗi cột, và mỗi khung 3x3,
      tất cả các biến trong đó phải nhận giá trị KHÁC NHAU (ràng buộc
      all-different, biểu diễn dưới dạng nhị phân giữa từng cặp biến).

THUẬT TOÁN BACKTRACKING SEARCH + FORWARD CHECKING:
    Backtracking Search thông thường: gán giá trị cho 1 biến, đệ quy gán
    biến tiếp theo; nếu sau này phát hiện vi phạm ràng buộc thì mới quay
    lui. Nhược điểm: phải đi sâu vào nhánh sai rồi mới biết là sai.

    FORWARD CHECKING là kỹ thuật bổ trợ giúp PHÁT HIỆN THẤT BẠI SỚM HƠN:
    Ngay khi gán biến X = v, ta LẬP TỨC kiểm tra (forward) tất cả các biến
    Y có ràng buộc trực tiếp với X (gọi là neighbor/peer của X — cùng
    hàng/cột/khung) và LOẠI giá trị v khỏi domain của từng Y đó.
        - Nếu sau khi loại, domain của một biến Y nào đó trở thành RỖNG
          (không còn giá trị hợp lệ nào) -> ta biết NGAY nhánh hiện tại
          chắc chắn dẫn đến thất bại, quay lui (backtrack) NGAY LẬP TỨC
          mà không cần đệ quy thêm bước nào nữa.
        - Nếu không, tiếp tục đệ quy gán biến kế tiếp.
        - Khi quay lui (undo gán biến X), phải KHÔI PHỤC lại domain đã bị
          thu hẹp của các neighbor (để không làm sai belief-state cho các
          nhánh thử khác sau này).

    Kết hợp thêm chiến lược chọn biến MRV (Minimum Remaining Values):
    luôn chọn biến (ô trống) có domain NHỎ NHẤT để gán tiếp theo — đây là
    heuristic phổ biến giúp CSP solver hội tụ nhanh hơn rất nhiều so với
    việc chọn biến theo thứ tự cố định.
----------------------------------------------------------------------------
"""

import copy
from sudoku_utils import SIZE, BOX, is_valid


class SearchStep:
    def __init__(self, board, row, col, value, action_type, domain_wipeout_cell=None):
        self.board = copy.deepcopy(board)
        self.row = row
        self.col = col
        self.value = value
        self.action_type = action_type   # 'assign' | 'forward_check_fail' | 'backtrack'
        self.domain_wipeout_cell = domain_wipeout_cell  # ô bị rỗng domain (nếu forward_check_fail)


class ForwardCheckingSolver:
    """
    Backtracking Search + Forward Checking + MRV để giải Sudoku (CSP).

    Cách dùng:
        solver = ForwardCheckingSolver(puzzle)
        solution_board, steps, stats = solver.solve()
    """

    def __init__(self, puzzle):
        self.puzzle = copy.deepcopy(puzzle)
        self.steps = []
        self.nodes_expanded = 0
        self.backtrack_count = 0

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

    def _init_domains(self, board):
        domains = {}
        for r in range(SIZE):
            for c in range(SIZE):
                if board[r][c] == 0:
                    domains[(r, c)] = {n for n in range(1, 10) if is_valid(board, r, c, n)}
        return domains

    def _select_unassigned_variable(self, domains):
        """Chiến lược MRV: chọn biến (ô trống) có domain nhỏ nhất."""
        return min(domains.keys(), key=lambda var: len(domains[var]))

    def _forward_check(self, board, domains, row, col, value):
        """
        Sau khi gán board[row][col] = value, loại `value` khỏi domain của
        các neighbor (peer) chưa được gán. Trả về:
            (removed: dict{var: set_giá_trị_đã_bị_loại}, wipeout_var hoặc None)
        Nếu wipeout_var khác None, nghĩa là domain của biến đó đã trở thành
        rỗng -> cần báo hiệu thất bại để quay lui ngay.
        """
        removed = {}
        wipeout_var = None
        for (r, c) in self._get_peers(row, col):
            if (r, c) in domains and value in domains[(r, c)]:
                domains[(r, c)].discard(value)
                removed.setdefault((r, c), set()).add(value)
                if len(domains[(r, c)]) == 0:
                    wipeout_var = (r, c)
                    break  # phát hiện thất bại ngay, không cần kiểm tra tiếp
        return removed, wipeout_var

    def _restore_domains(self, domains, removed):
        """Khôi phục lại domain đã bị forward checking thu hẹp, dùng khi quay lui."""
        for var, values in removed.items():
            domains[var].update(values)

    def _backtrack(self, board, domains):
        if not domains:
            return True  # không còn biến nào chưa gán -> đã giải xong

        var = self._select_unassigned_variable(domains)
        row, col = var
        domain_values = sorted(domains[var])  # thử theo thứ tự tăng dần cho dễ theo dõi

        for value in domain_values:
            self.nodes_expanded += 1
            board[row][col] = value
            del domains[var]

            self.steps.append(SearchStep(board, row, col, value, 'assign'))

            removed, wipeout_var = self._forward_check(board, domains, row, col, value)

            if wipeout_var is not None:
                # Forward checking phát hiện thất bại NGAY, không cần đệ quy thêm
                self.steps.append(SearchStep(board, row, col, value,
                                              'forward_check_fail', wipeout_var))
            else:
                if self._backtrack(board, domains):
                    return True

            # Quay lui: khôi phục domain và undo gán biến
            self._restore_domains(domains, removed)
            domains[var] = set(domain_values)  # khôi phục domain gốc của var này
            board[row][col] = 0
            self.backtrack_count += 1
            self.steps.append(SearchStep(board, row, col, 0, 'backtrack'))

        return False

    def solve(self):
        board = copy.deepcopy(self.puzzle)
        domains = self._init_domains(board)

        success = self._backtrack(board, domains)

        stats = {
            'nodes_expanded': self.nodes_expanded,
            'backtrack_count': self.backtrack_count,
            'total_steps_recorded': len(self.steps),
            'solved': success,
        }
        return (board if success else None), self.steps, stats


if __name__ == "__main__":
    from sudoku_utils import generate_puzzle, board_to_string, is_solved
    import time

    # Forward Checking + MRV xử lý tốt cả Sudoku chuẩn (28-30 clue)
    puzzle, real_solution = generate_puzzle(num_clues=28, seed=15)
    print("Đề bài:")
    print(board_to_string(puzzle))
    print()

    solver = ForwardCheckingSolver(puzzle)
    t0 = time.time()
    solution, steps, stats = solver.solve()
    t1 = time.time()

    print("Thống kê:", stats)
    print("Thời gian:", round(t1 - t0, 4), "giây")

    if solution:
        print("Đã giải xong bằng Forward Checking!")
        print(board_to_string(solution))
        print("Hợp lệ:", is_solved(solution))
    else:
        print("Không tìm được lời giải.")
