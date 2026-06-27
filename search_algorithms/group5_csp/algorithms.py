"""
=============================================================================
  NHÓM 5: CONSTRAINT SATISFACTION PROBLEMS (CSP)
  (Bài toán thỏa mãn ràng buộc)
=============================================================================
Sudoku là bài toán CSP KINH ĐIỂN:
  - Variables (Biến):     81 ô (chỉ ô trống cần gán giá trị)
  - Domains (Miền giá trị): {1, 2, ..., 9} cho mỗi ô trống
  - Constraints (Ràng buộc): AllDifferent cho mỗi hàng, cột, khối 3×3

Gồm 3 thuật toán:
  13. Backtracking Search   — DFS + kiểm tra ràng buộc tại mỗi bước
  14. Forward Checking      — Backtracking + cập nhật domain khi gán
  15. Min-Conflicts         — Local search trên CSP

So sánh với Tree Search (Nhóm 1-2):
  - Tree Search: state = toàn bộ bảng, successor = đặt 1 giá trị
  - CSP: variable = 1 ô, assignment = gán giá trị, constraint = ràng buộc
  - CSP hiệu quả hơn nhờ constraint propagation
=============================================================================
"""
import random
import copy
from typing import Dict, List, Set, Tuple, Optional
from search_algorithms.core.sudoku import SudokuHelper


# =============================================================================
#  SUDOKU CSP MODEL
# =============================================================================
class SudokuCSP:
    """
    Mô hình CSP cho Sudoku.

    Components:
    ───────────
    - variables:   Danh sách ô trống [(row, col), ...]
    - domains:     {(row, col): set of possible values}
    - constraints: Mỗi cặp ô cùng hàng/cột/khối → giá trị phải khác nhau
    - assignment:  {(row, col): value} — các ô đã gán giá trị
    """

    def __init__(self, board: tuple):
        self.board = board
        self.variables = []
        self.domains = {}
        self.assignment = {}  # Ô đã cho (given)
        self.neighbors = {}   # {(r,c): [(r2,c2), ...]}

        # Khởi tạo variables, domains, assignment
        for i in range(81):
            r, c = i // 9, i % 9
            if board[i] != 0:
                self.assignment[(r, c)] = board[i]
            else:
                self.variables.append((r, c))
                self.domains[(r, c)] = set(SudokuHelper.get_valid_values(board, r, c))

        # Xây dựng đồ thị ràng buộc (constraint graph)
        for r in range(9):
            for c in range(9):
                self.neighbors[(r, c)] = [
                    (pr, pc) for pr, pc in SudokuHelper.get_peers(r, c)
                ]

    def is_consistent(self, var: Tuple[int, int], value: int,
                      assignment: Dict) -> bool:
        """
        Kiểm tra: gán var = value có vi phạm ràng buộc nào không?
        Ràng buộc: var ≠ neighbor cho mọi neighbor cùng hàng/cột/khối.
        """
        for neighbor in self.neighbors[var]:
            if neighbor in assignment and assignment[neighbor] == value:
                return False
        return True

    def select_unassigned_variable(self, assignment: Dict,
                                    domains: Dict) -> Tuple[int, int]:
        """
        Chọn biến chưa gán — dùng MRV (Minimum Remaining Values).

        MRV Heuristic: chọn biến có domain NHỎ NHẤT.
        Lý do: biến bị ràng buộc nhiều nhất → gán sớm sẽ phát hiện
        mâu thuẫn sớm → cắt tỉa hiệu quả hơn.
        """
        unassigned = [v for v in self.variables if v not in assignment]
        return min(unassigned, key=lambda v: len(domains.get(v, set())))

    def get_board_from_assignment(self, assignment: Dict) -> tuple:
        """Xây dựng bảng Sudoku từ assignment."""
        board = list(self.board)
        for (r, c), v in assignment.items():
            board[r * 9 + c] = v
        return tuple(board)

    def is_complete(self, assignment: Dict) -> bool:
        """Kiểm tra xem tất cả biến đã được gán chưa."""
        return all(v in assignment for v in self.variables)


# =============================================================================
# 13. BACKTRACKING SEARCH - Tìm kiếm quay lui
# =============================================================================
def backtracking_search(problem_board: tuple) -> dict:
    """
    Backtracking Search cho CSP.

    ╔════════════════════════════════════════════════════════════╗
    ║  Bản chất: DFS trên không gian assignment                ║
    ║  Mỗi bước: chọn 1 biến → thử gán từng giá trị          ║
    ║  Nếu vi phạm ràng buộc → QUAY LUI (backtrack)           ║
    ║  Cải tiến: dùng MRV để chọn biến tiếp theo              ║
    ╚════════════════════════════════════════════════════════════╝

    Logic cốt lõi (đệ quy):
    ─────────────────────────
    BACKTRACK(assignment):
      1. Nếu assignment đầy đủ → trả về assignment
      2. var = chọn biến chưa gán (MRV)
      3. Với mỗi value trong domain(var):
         a. Nếu value consistent với assignment:
            - assignment[var] = value
            - result = BACKTRACK(assignment)
            - Nếu result ≠ failure → trả về result
            - Xóa assignment[var]  (backtrack!)
      4. Trả về failure

    So sánh với DFS (Nhóm 1):
    ──────────────────────────
    - DFS: mỗi node = toàn bộ bảng, explored set lớn
    - Backtracking: mỗi node = 1 assignment, kiểm tra ràng buộc ngay
    - Backtracking hiệu quả hơn nhiều nhờ early pruning

    Complexity:
    ───────────
    - Time:  O(d^n) worst case — d = domain size (9), n = variables (ô trống)
    - Space: O(n) — chỉ lưu assignment hiện tại

    Args:
        problem_board: tuple 81 phần tử

    Returns:
        dict với keys: 'board', 'found', 'nodes_explored', 'backtracks'
    """
    csp = SudokuCSP(problem_board)
    stats = {"nodes": 0, "backtracks": 0}

    def backtrack(assignment: Dict) -> Optional[Dict]:
        stats["nodes"] += 1

        # Kiểm tra đầy đủ
        if csp.is_complete(assignment):
            return assignment

        # Chọn biến chưa gán (MRV)
        var = csp.select_unassigned_variable(assignment, csp.domains)

        # Thử từng giá trị trong domain
        for value in sorted(csp.domains.get(var, set())):
            if csp.is_consistent(var, value, assignment):
                # Gán giá trị
                assignment[var] = value

                result = backtrack(assignment)
                if result is not None:
                    return result

                # Backtrack: xóa gán giá trị
                del assignment[var]
                stats["backtracks"] += 1

        return None

    assignment = dict(csp.assignment)  # Bắt đầu từ given cells
    result = backtrack(assignment)

    if result is not None:
        board = csp.get_board_from_assignment(result)
        return {
            'algorithm': 'Backtracking Search',
            'board': board,
            'found': True,
            'nodes_explored': stats["nodes"],
            'backtracks': stats["backtracks"],
        }
    return {
        'algorithm': 'Backtracking Search',
        'board': problem_board,
        'found': False,
        'nodes_explored': stats["nodes"],
        'backtracks': stats["backtracks"],
    }


# =============================================================================
# 14. FORWARD CHECKING - Kiểm tra tiến
# =============================================================================
def forward_checking(problem_board: tuple) -> dict:
    """
    Forward Checking - Backtracking + cập nhật domain.

    ╔════════════════════════════════════════════════════════════╗
    ║  Cải tiến Backtracking: khi gán var = value,             ║
    ║  LOẠI BỎ value khỏi domain của các biến liên quan       ║
    ║  (cùng hàng/cột/khối).                                   ║
    ║  Nếu domain nào trở thành RỖNG → backtrack NGAY         ║
    ║  (không cần đợi đến khi gán biến đó)                     ║
    ╚════════════════════════════════════════════════════════════╝

    Logic cốt lõi:
    ─────────────
    FORWARD-CHECK(assignment, domains):
      1. var = chọn biến (MRV trên domains đã cập nhật)
      2. Với mỗi value trong domains[var]:
         a. new_domains = copy(domains)
         b. new_domains[var] = {value}
         c. Với mỗi neighbor chưa gán:
            - Loại value khỏi new_domains[neighbor]
            - Nếu new_domains[neighbor] rỗng → bỏ qua value này
         d. assignment[var] = value
         e. result = FORWARD-CHECK(assignment, new_domains)
         f. Nếu thành công → trả về

    So sánh với Backtracking thuần:
    ────────────────────────────────
    - Backtracking: chỉ kiểm tra khi GÁN → phát hiện mâu thuẫn muộn
    - Forward Checking: kiểm tra domain NGAY → phát hiện sớm → cắt tỉa mạnh
    - Forward Checking thường nhanh hơn 10-100x

    Complexity:
    ───────────
    - Time:  Thường tốt hơn Backtracking nhờ pruning sớm
    - Space: O(n × d) — lưu domain cho mỗi biến

    Args:
        problem_board: tuple 81 phần tử

    Returns:
        dict với keys: 'board', 'found', 'nodes_explored', 'pruned'
    """
    csp = SudokuCSP(problem_board)
    stats = {"nodes": 0, "pruned": 0}

    def forward_check(assignment: Dict,
                      domains: Dict[Tuple, Set]) -> Optional[Dict]:
        stats["nodes"] += 1

        if csp.is_complete(assignment):
            return assignment

        # Chọn biến MRV (trên domains đã cập nhật)
        var = csp.select_unassigned_variable(assignment, domains)

        for value in sorted(domains.get(var, set())):
            if not csp.is_consistent(var, value, assignment):
                continue

            # ── Forward Check: cập nhật domain các neighbor ──
            new_domains = {k: set(v) for k, v in domains.items()}
            new_domains[var] = {value}

            # Loại value khỏi domain các neighbor chưa gán
            domain_wipeout = False
            for neighbor in csp.neighbors[var]:
                if neighbor not in assignment and neighbor in new_domains:
                    new_domains[neighbor].discard(value)
                    if len(new_domains[neighbor]) == 0:
                        # Domain wipeout! → prune nhánh này
                        domain_wipeout = True
                        stats["pruned"] += 1
                        break

            if domain_wipeout:
                continue  # Thử giá trị khác

            assignment[var] = value
            result = forward_check(assignment, new_domains)
            if result is not None:
                return result

            del assignment[var]

        return None

    assignment = dict(csp.assignment)
    domains = {k: set(v) for k, v in csp.domains.items()}
    result = forward_check(assignment, domains)

    if result is not None:
        board = csp.get_board_from_assignment(result)
        return {
            'algorithm': 'Forward Checking',
            'board': board,
            'found': True,
            'nodes_explored': stats["nodes"],
            'pruned': stats["pruned"],
        }
    return {
        'algorithm': 'Forward Checking',
        'board': problem_board,
        'found': False,
        'nodes_explored': stats["nodes"],
        'pruned': stats["pruned"],
    }


# =============================================================================
# 15. MIN-CONFLICTS - Xung đột tối thiểu
# =============================================================================
def min_conflicts(problem_board: tuple, max_steps: int = 100000) -> dict:
    """
    Min-Conflicts Algorithm - Local search cho CSP.

    ╔════════════════════════════════════════════════════════════╗
    ║  Chiến lược: Bắt đầu từ gán giá trị NGẪU NHIÊN,        ║
    ║  lặp lại: chọn biến đang VI PHẠM → gán giá trị tạo    ║
    ║  ÍT XUNG ĐỘT NHẤT.                                     ║
    ║                                                            ║
    ║  Đặc biệt: rất hiệu quả cho N-Queens và Sudoku!         ║
    ║  Thường giải n-queens với n = 10^6 trong vài bước!       ║
    ╚════════════════════════════════════════════════════════════╝

    Logic cốt lõi:
    ─────────────
    1. Gán ngẫu nhiên giá trị cho tất cả ô trống
    2. Lặp (max_steps lần):
       a. Nếu không còn xung đột → trả về (thành công!)
       b. Chọn ngẫu nhiên 1 biến đang vi phạm (conflicting variable)
       c. Gán giá trị tạo ÍT XUNG ĐỘT NHẤT cho biến đó
    3. Nếu hết bước mà chưa giải → thất bại

    Min-conflicts value:
    ────────────────────
    Với mỗi giá trị v ∈ domain:
      conflicts(v) = số biến neighbor đang có cùng giá trị v
    Chọn v có conflicts(v) nhỏ nhất (tie-break ngẫu nhiên).

    Args:
        problem_board: tuple 81 phần tử
        max_steps:     Số bước tối đa

    Returns:
        dict với keys: 'board', 'found', 'steps', 'conflicts_remaining'
    """
    csp = SudokuCSP(problem_board)
    assignment = dict(csp.assignment)

    # Gán ngẫu nhiên cho các ô trống
    for var in csp.variables:
        domain = csp.domains.get(var, set(range(1, 10)))
        if domain:
            assignment[var] = random.choice(list(domain))
        else:
            assignment[var] = random.randint(1, 9)

    def count_conflicts(var: Tuple[int, int], value: int,
                        assignment: Dict) -> int:
        """Đếm số xung đột nếu gán var = value."""
        count = 0
        for neighbor in csp.neighbors[var]:
            if neighbor in assignment and assignment[neighbor] == value:
                count += 1
        return count

    def get_conflicting_variables(assignment: Dict) -> List[Tuple[int, int]]:
        """Lấy danh sách các biến đang có xung đột."""
        conflicting = []
        for var in csp.variables:
            if count_conflicts(var, assignment[var], assignment) > 0:
                conflicting.append(var)
        return conflicting

    for step in range(max_steps):
        # Tìm các biến đang vi phạm
        conflicting = get_conflicting_variables(assignment)

        if not conflicting:
            # Không còn xung đột → thành công!
            board = csp.get_board_from_assignment(assignment)
            return {
                'algorithm': 'Min-Conflicts',
                'board': board,
                'found': True,
                'steps': step,
                'conflicts_remaining': 0,
            }

        # Chọn ngẫu nhiên 1 biến đang vi phạm
        var = random.choice(conflicting)

        # Tìm giá trị tạo ít xung đột nhất
        min_conflict_count = float('inf')
        best_values = []

        for value in range(1, 10):
            c = count_conflicts(var, value, assignment)
            if c < min_conflict_count:
                min_conflict_count = c
                best_values = [value]
            elif c == min_conflict_count:
                best_values.append(value)

        # Tie-break ngẫu nhiên
        assignment[var] = random.choice(best_values)

    # Hết bước
    conflicts = len(get_conflicting_variables(assignment))
    board = csp.get_board_from_assignment(assignment)
    return {
        'algorithm': 'Min-Conflicts',
        'board': board,
        'found': False,
        'steps': max_steps,
        'conflicts_remaining': conflicts,
    }
