"""
=============================================================================
  SUDOKU PROBLEM - Bài toán Sudoku 9×9 cho các thuật toán tìm kiếm
=============================================================================
Biểu diễn trạng thái:
  - State: tuple gồm 81 phần tử (đọc theo hàng, từ trái → phải, trên → dưới)
  - Ô trống = 0, ô đã điền = 1-9
  - Ví dụ: index = row * 9 + col

Bao gồm:
  - SudokuProblem:  Kế thừa Problem, dùng cho Tree Search (BFS, DFS, A*, ...)
  - SudokuHelper:   Các hàm tiện ích chung (validate, print, ...)
  - SAMPLE_PUZZLES: Các bảng Sudoku mẫu theo mức độ khó
"""
from typing import Any, List, Tuple, Set
from search_algorithms.core.problem_base import Problem


# =============================================================================
#  SUDOKU HELPER - Hàm tiện ích dùng chung
# =============================================================================
class SudokuHelper:
    """
    Tập hợp các hàm tiện ích tĩnh cho bài toán Sudoku 9×9.
    Được dùng bởi tất cả 6 nhóm thuật toán.
    """

    @staticmethod
    def get_row_values(state: tuple, row: int) -> List[int]:
        """Lấy danh sách giá trị trong hàng row (bỏ qua 0)."""
        return [state[row * 9 + c] for c in range(9) if state[row * 9 + c] != 0]

    @staticmethod
    def get_col_values(state: tuple, col: int) -> List[int]:
        """Lấy danh sách giá trị trong cột col (bỏ qua 0)."""
        return [state[r * 9 + col] for r in range(9) if state[r * 9 + col] != 0]

    @staticmethod
    def get_block_values(state: tuple, row: int, col: int) -> List[int]:
        """Lấy danh sách giá trị trong khối 3×3 chứa ô (row, col) (bỏ qua 0)."""
        br, bc = (row // 3) * 3, (col // 3) * 3
        values = []
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                v = state[r * 9 + c]
                if v != 0:
                    values.append(v)
        return values

    @staticmethod
    def get_valid_values(state: tuple, row: int, col: int) -> List[int]:
        """
        Lấy danh sách giá trị hợp lệ có thể đặt vào ô (row, col).

        Một giá trị hợp lệ khi nó CHƯA xuất hiện ở:
          - Cùng hàng (row)
          - Cùng cột (col)
          - Cùng khối 3×3 (block)
        """
        if state[row * 9 + col] != 0:
            return []  # Ô đã điền

        used = set()
        # Giá trị đã dùng trong hàng
        for c in range(9):
            used.add(state[row * 9 + c])
        # Giá trị đã dùng trong cột
        for r in range(9):
            used.add(state[r * 9 + col])
        # Giá trị đã dùng trong khối 3×3
        br, bc = (row // 3) * 3, (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                used.add(state[r * 9 + c])

        return [v for v in range(1, 10) if v not in used]

    @staticmethod
    def get_peers(row: int, col: int) -> List[Tuple[int, int]]:
        """
        Lấy danh sách tất cả các ô 'peer' của ô (row, col).
        Peer = cùng hàng, cùng cột, hoặc cùng khối 3×3 (không tính chính nó).
        """
        peers = set()
        # Cùng hàng
        for c in range(9):
            if c != col:
                peers.add((row, c))
        # Cùng cột
        for r in range(9):
            if r != row:
                peers.add((r, col))
        # Cùng khối 3×3
        br, bc = (row // 3) * 3, (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                if (r, c) != (row, col):
                    peers.add((r, c))
        return list(peers)

    @staticmethod
    def count_empty(state: tuple) -> int:
        """Đếm số ô trống (giá trị 0) trong bảng."""
        return state.count(0)

    @staticmethod
    def get_empty_cells(state: tuple) -> List[Tuple[int, int]]:
        """Lấy danh sách tọa độ (row, col) của tất cả ô trống."""
        cells = []
        for i in range(81):
            if state[i] == 0:
                cells.append((i // 9, i % 9))
        return cells

    @staticmethod
    def count_conflicts(state: tuple) -> int:
        """
        Đếm tổng số xung đột trong bảng Sudoku.
        Xung đột = cùng giá trị xuất hiện nhiều lần trong hàng/cột/khối.
        """
        conflicts = 0
        for i in range(9):
            # Xung đột trong hàng
            row = [state[i * 9 + c] for c in range(9) if state[i * 9 + c] != 0]
            conflicts += len(row) - len(set(row))
            # Xung đột trong cột
            col = [state[r * 9 + i] for r in range(9) if state[r * 9 + i] != 0]
            conflicts += len(col) - len(set(col))
        # Xung đột trong khối 3×3
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                block = []
                for r in range(br, br + 3):
                    for c in range(bc, bc + 3):
                        v = state[r * 9 + c]
                        if v != 0:
                            block.append(v)
                conflicts += len(block) - len(set(block))
        return conflicts

    @staticmethod
    def is_valid_complete(state: tuple) -> bool:
        """Kiểm tra bảng đã điền đầy đủ VÀ hợp lệ (mỗi hàng/cột/khối chứa đúng 1-9)."""
        if 0 in state:
            return False
        for i in range(9):
            # Kiểm tra hàng
            row = state[i * 9:(i + 1) * 9]
            if len(set(row)) != 9:
                return False
            # Kiểm tra cột
            col = tuple(state[r * 9 + i] for r in range(9))
            if len(set(col)) != 9:
                return False
        # Kiểm tra khối 3×3
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                block = tuple(state[(br + r) * 9 + bc + c]
                              for r in range(3) for c in range(3))
                if len(set(block)) != 9:
                    return False
        return True

    @staticmethod
    def is_valid_partial(state: tuple) -> bool:
        """Kiểm tra bảng chưa hoàn chỉnh có hợp lệ không (không có xung đột)."""
        for i in range(9):
            # Kiểm tra hàng
            row = [state[i * 9 + c] for c in range(9) if state[i * 9 + c] != 0]
            if len(row) != len(set(row)):
                return False
            # Kiểm tra cột
            col = [state[r * 9 + i] for r in range(9) if state[r * 9 + i] != 0]
            if len(col) != len(set(col)):
                return False
        # Kiểm tra khối 3×3
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                block = [state[(br + r) * 9 + bc + c]
                         for r in range(3) for c in range(3)
                         if state[(br + r) * 9 + bc + c] != 0]
                if len(block) != len(set(block)):
                    return False
        return True

    @staticmethod
    def print_board(state: tuple) -> str:
        """
        In bảng Sudoku dạng đẹp.

        Ví dụ output:
        ╔═══════╦═══════╦═══════╗
        ║ 5 3 · ║ · 7 · ║ · · · ║
        ║ 6 · · ║ 1 9 5 ║ · · · ║
        ║ · 9 8 ║ · · · ║ · 6 · ║
        ╠═══════╬═══════╬═══════╣
        ...
        """
        lines = []
        lines.append("╔═══════╦═══════╦═══════╗")
        for r in range(9):
            row_str = "║"
            for c in range(9):
                val = state[r * 9 + c]
                cell = f" {val}" if val != 0 else " ·"
                row_str += cell
                if c % 3 == 2:
                    row_str += " ║"
            lines.append(row_str)
            if r % 3 == 2 and r < 8:
                lines.append("╠═══════╬═══════╬═══════╣")
        lines.append("╚═══════╩═══════╩═══════╝")
        return "\n".join(lines)


# =============================================================================
#  SUDOKU PROBLEM - Kế thừa Problem cho Tree Search
# =============================================================================
class SudokuProblem(Problem):
    """
    Bài toán Sudoku dưới dạng Problem cho Tree Search.

    Dùng cho các thuật toán: BFS, DFS, IDS, Greedy, A*, IDA*

    Mô hình:
    ─────────
    - State:       tuple 81 phần tử (0 = ô trống)
    - Action:      'R{row}C{col}={val}' — đặt val vào ô (row, col)
    - Successor:   Tìm ô trống ĐẦU TIÊN, thử tất cả giá trị hợp lệ
    - Step cost:   1.0 cho mỗi bước đặt số
    - Goal test:   Tất cả 81 ô ≠ 0 VÀ thỏa mãn ràng buộc Sudoku
    - Heuristic:   Số ô trống còn lại (admissible)

    Tại sao chỉ điền ô trống ĐẦU TIÊN?
    ────────────────────────────────────
    Nếu cho phép điền BẤT KỲ ô trống nào → không gian tìm kiếm bùng nổ.
    Chỉ điền ô đầu tiên theo thứ tự quét → đảm bảo systematic, không trùng lặp.
    """

    def __init__(self, initial_board: tuple):
        """
        Khởi tạo bài toán Sudoku.

        Args:
            initial_board: tuple 81 phần tử, 0 = ô trống
        """
        if len(initial_board) != 81:
            raise ValueError("Bảng Sudoku phải có đúng 81 phần tử!")
        self._initial = initial_board
        # Lưu vị trí các ô đã cho (given cells) — không được thay đổi
        self._given = frozenset(i for i in range(81) if initial_board[i] != 0)

    def initial_state(self) -> tuple:
        """Trả về trạng thái ban đầu (bảng Sudoku với các ô trống)."""
        return self._initial

    def goal_test(self, state: Any) -> bool:
        """
        Kiểm tra đích: bảng đã điền đầy đủ VÀ hợp lệ.
        Trong tree search, nếu successors chỉ sinh giá trị hợp lệ,
        thì chỉ cần kiểm tra không còn ô trống.
        """
        return 0 not in state

    def get_successors(self, state: tuple) -> List[Tuple[str, tuple, float]]:
        """
        Sinh các trạng thái kế tiếp.

        Chiến lược: Tìm ô trống đầu tiên → thử đặt từng giá trị hợp lệ.
        Chỉ đặt giá trị KHÔNG vi phạm ràng buộc (hàng, cột, khối 3×3).
        """
        # Tìm ô trống đầu tiên
        try:
            idx = state.index(0)
        except ValueError:
            return []  # Không còn ô trống

        row, col = idx // 9, idx % 9
        successors = []

        for val in SudokuHelper.get_valid_values(state, row, col):
            # Tạo trạng thái mới bằng cách đặt val vào ô (row, col)
            new_state = list(state)
            new_state[idx] = val
            action = f"R{row + 1}C{col + 1}={val}"
            successors.append((action, tuple(new_state), 1.0))

        return successors

    def heuristic(self, state: tuple) -> float:
        """
        Hàm heuristic h(n) = số ô trống còn lại.

        Tính chất:
        ──────────
        - Admissible: h(n) ≤ h*(n) vì mỗi ô trống cần ít nhất 1 bước
        - Consistent: h(n) ≤ c(n,a,n') + h(n') vì mỗi bước giảm đúng 1 ô trống

        Mở rộng: phát hiện dead-end (ô trống không có giá trị hợp lệ)
        → trả về float('inf') để tránh mở rộng nhánh chết.
        """
        empty_count = 0
        for i in range(81):
            if state[i] == 0:
                row, col = i // 9, i % 9
                if not SudokuHelper.get_valid_values(state, row, col):
                    return float('inf')  # Dead-end: ô trống không có giá trị hợp lệ
                empty_count += 1
        return float(empty_count)


# =============================================================================
#  SAMPLE PUZZLES - Các bảng Sudoku mẫu theo mức độ khó
# =============================================================================

# ── Lời giải tham khảo ──
SOLUTION = (
    5, 3, 4, 6, 7, 8, 9, 1, 2,
    6, 7, 2, 1, 9, 5, 3, 4, 8,
    1, 9, 8, 3, 4, 2, 5, 6, 7,
    8, 5, 9, 7, 6, 1, 4, 2, 3,
    4, 2, 6, 8, 5, 3, 7, 9, 1,
    7, 1, 3, 9, 2, 4, 8, 5, 6,
    9, 6, 1, 5, 3, 7, 2, 8, 4,
    2, 8, 7, 4, 1, 9, 6, 3, 5,
    3, 4, 5, 2, 8, 6, 1, 7, 9,
)

# ── VERY EASY: 8 ô trống — dùng cho BFS ──
# 5 3 4 | 6 7 8 | 9 1 2
# 6 7 2 | 1 9 5 | 3 4 8
# 1 9 8 | 3 · 2 | 5 6 7
# ------+-------+------
# 8 · 9 | 7 6 1 | 4 · 3
# 4 2 6 | 8 5 3 | 7 9 1
# 7 1 3 | · 2 4 | 8 5 6
# ------+-------+------
# 9 6 · | 5 3 7 | · 8 4
# 2 8 7 | 4 · 9 | 6 3 5
# 3 4 5 | 2 8 · | 1 7 9
VERY_EASY_BOARD = (
    5, 3, 4, 6, 7, 8, 9, 1, 2,
    6, 7, 2, 1, 9, 5, 3, 4, 8,
    1, 9, 8, 3, 0, 2, 5, 6, 7,
    8, 0, 9, 7, 6, 1, 4, 0, 3,
    4, 2, 6, 8, 5, 3, 7, 9, 1,
    7, 1, 3, 0, 2, 4, 8, 5, 6,
    9, 6, 0, 5, 3, 7, 0, 8, 4,
    2, 8, 7, 4, 0, 9, 6, 3, 5,
    3, 4, 5, 2, 8, 0, 1, 7, 9,
)

# ── EASY: 15 ô trống — dùng cho DFS, IDS ──
# 5 3 4 | 6 7 · | 9 · 2
# 6 · 2 | 1 9 5 | 3 4 8
# 1 9 8 | · 4 2 | 5 6 7
# ------+-------+------
# 8 · 9 | 7 · 1 | 4 2 3
# 4 2 6 | 8 5 3 | · 9 1
# 7 1 · | 9 2 · | 8 5 6
# ------+-------+------
# 9 6 1 | 5 · 7 | 2 8 ·
# · 8 7 | 4 1 9 | 6 · 5
# 3 4 · | 2 8 · | 1 7 9
EASY_BOARD = (
    5, 3, 4, 6, 7, 0, 9, 0, 2,
    6, 0, 2, 1, 9, 5, 3, 4, 8,
    1, 9, 8, 0, 4, 2, 5, 6, 7,
    8, 0, 9, 7, 0, 1, 4, 2, 3,
    4, 2, 6, 8, 5, 3, 0, 9, 1,
    7, 1, 0, 9, 2, 0, 8, 5, 6,
    9, 6, 1, 5, 0, 7, 2, 8, 0,
    0, 8, 7, 4, 1, 9, 6, 0, 5,
    3, 4, 0, 2, 8, 0, 1, 7, 9,
)

# ── MEDIUM: 25 ô trống — dùng cho A*, Greedy, IDA*, CSP ──
# 5 3 · | · 7 · | · · 2
# 6 · · | 1 9 5 | 3 · 8
# · 9 8 | · · 2 | 5 6 ·
# ------+-------+------
# 8 · · | 7 6 · | 4 · 3
# 4 · 6 | 8 · 3 | · 9 1
# 7 · 3 | · 2 4 | 8 · 6
# ------+-------+------
# · 6 · | 5 · 7 | · 8 ·
# 2 · 7 | 4 1 · | 6 · 5
# · 4 · | · 8 6 | 1 7 ·
MEDIUM_BOARD = (
    5, 3, 0, 0, 7, 0, 0, 0, 2,
    6, 0, 0, 1, 9, 5, 3, 0, 8,
    0, 9, 8, 0, 0, 2, 5, 6, 0,
    8, 0, 0, 7, 6, 0, 4, 0, 3,
    4, 0, 6, 8, 0, 3, 0, 9, 1,
    7, 0, 3, 0, 2, 4, 8, 0, 6,
    0, 6, 0, 5, 0, 7, 0, 8, 0,
    2, 0, 7, 4, 1, 0, 6, 0, 5,
    0, 4, 0, 0, 8, 6, 1, 7, 0,
)

# ── HARD: 45 ô trống — chỉ dùng cho CSP, Local Search ──
# 5 3 · | · 7 · | · · ·
# 6 · · | 1 9 5 | · · ·
# · 9 8 | · · · | · 6 ·
# ------+-------+------
# 8 · · | · 6 · | · · 3
# 4 · · | 8 · 3 | · · 1
# 7 · · | · 2 · | · · 6
# ------+-------+------
# · 6 · | · · · | 2 8 ·
# · · · | 4 1 9 | · · 5
# · · · | · 8 · | · 7 9
HARD_BOARD = (
    5, 3, 0, 0, 7, 0, 0, 0, 0,
    6, 0, 0, 1, 9, 5, 0, 0, 0,
    0, 9, 8, 0, 0, 0, 0, 6, 0,
    8, 0, 0, 0, 6, 0, 0, 0, 3,
    4, 0, 0, 8, 0, 3, 0, 0, 1,
    7, 0, 0, 0, 2, 0, 0, 0, 6,
    0, 6, 0, 0, 0, 0, 2, 8, 0,
    0, 0, 0, 4, 1, 9, 0, 0, 5,
    0, 0, 0, 0, 8, 0, 0, 7, 9,
)

# ── Dictionary tiện dùng ──
SAMPLE_PUZZLES = {
    "very_easy": {"board": VERY_EASY_BOARD, "empty": 8,
                  "desc": "Rất dễ (8 ô trống) — demo BFS"},
    "easy":      {"board": EASY_BOARD,      "empty": 15,
                  "desc": "Dễ (15 ô trống) — demo DFS, IDS"},
    "medium":    {"board": MEDIUM_BOARD,    "empty": 25,
                  "desc": "Trung bình (25 ô trống) — demo A*, CSP"},
    "hard":      {"board": HARD_BOARD,      "empty": 45,
                  "desc": "Khó (45 ô trống) — demo CSP, Local Search"},
}
