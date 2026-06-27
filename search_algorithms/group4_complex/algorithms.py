"""
=============================================================================
  NHÓM 4: SEARCHING IN COMPLEX ENVIRONMENTS
  (Tìm kiếm trong môi trường phức tạp)
=============================================================================
Các thuật toán trong nhóm này xử lý tình huống đặc biệt:
  - Không gian trạng thái có cấu trúc phức tạp (AND-OR)
  - Không quan sát được trạng thái (Sensorless)
  - Chỉ quan sát được một phần (Partially Observable)

Gồm 3 thuật toán:
  10. AND-OR Search              — Cây lời giải điều kiện
  11. Sensorless Search          — Tìm kiếm trên belief state
  12. Partially Observable Search — Kết hợp belief state + quan sát

Mô hình hóa cho Sudoku:
────────────────────────
  10. AND-OR: OR = chọn giá trị cho ô, AND = tất cả ô còn lại phải giải được
  11. Sensorless: Một số ô "không chắc chắn", tìm plan cho MỌI khả năng
  12. Partial Observable: Chỉ thấy hàng/cột hiện tại, cập nhật belief state
=============================================================================
"""
import copy
from typing import Dict, List, Set, Tuple, Optional, Any, FrozenSet
from search_algorithms.core.sudoku import SudokuHelper


# =============================================================================
# 10. AND-OR SEARCH - Tìm kiếm trên cây AND-OR
# =============================================================================

class ConditionalPlan:
    """
    Kế hoạch điều kiện (Conditional Plan) — kết quả của AND-OR Search.

    Khác với đường đi tuyến tính (path), conditional plan là một CÂY:
    - Mỗi nút OR: "nếu chọn giá trị X cho ô này"
    - Mỗi nút AND: "tất cả ô con phải giải được"

    Trong trường hợp Sudoku deterministic, plan đơn giản hóa thành
    dictionary: {(row, col): value}
    """
    def __init__(self):
        self.assignments = {}  # {(row, col): value}
        self.nodes_explored = 0

    def add(self, row: int, col: int, value: int):
        self.assignments[(row, col)] = value

    def __str__(self):
        lines = [f"  R{r+1}C{c+1} = {v}" for (r, c), v in sorted(self.assignments.items())]
        return "\n".join(lines) if lines else "  (empty plan)"


def and_or_search(problem_board: tuple) -> dict:
    """
    AND-OR Search cho Sudoku.

    ╔════════════════════════════════════════════════════════════╗
    ║  Cấu trúc cây AND-OR:                                    ║
    ║  - OR node:  Chọn giá trị nào cho ô trống hiện tại      ║
    ║              (chỉ cần 1 nhánh thành công)                ║
    ║  - AND node: TẤT CẢ ô trống còn lại phải giải được     ║
    ║              (tất cả nhánh phải thành công)               ║
    ║  Kết quả: Conditional Plan (cây lời giải điều kiện)      ║
    ╚════════════════════════════════════════════════════════════╝

    Logic cốt lõi (đệ quy):
    ─────────────────────────
    OR-SEARCH(state, empty_cells):
      1. Nếu empty_cells rỗng → trả về plan rỗng (success!)
      2. Chọn ô đầu tiên (row, col) từ empty_cells
      3. Với mỗi giá trị hợp lệ v cho ô (row, col):     ← OR: thử từng giá trị
         a. Đặt v vào (row, col) → new_state
         b. result = AND-SEARCH(new_state, remaining_cells)  ← AND: giải phần còn lại
         c. Nếu result thành công → trả về plan

    AND-SEARCH(state, remaining_cells):
      1. Tất cả remaining_cells phải giải được
      2. Trong Sudoku deterministic → tương đương OR-SEARCH trên remaining
         (AND chỉ có 1 nhánh = "giải phần còn lại")

    Tại sao dùng AND-OR cho Sudoku?
    ─────────────────────────────────
    Mặc dù Sudoku là deterministic (AND-OR = backtracking), mô hình AND-OR
    giúp hiểu bản chất: CHỌN giá trị (OR) rồi CHỨNG MINH phần còn lại
    giải được (AND). Với bài toán nondeterministic, AND sẽ xử lý nhiều
    kết quả khả dĩ.

    Args:
        problem_board: tuple 81 phần tử

    Returns:
        dict với keys: 'plan', 'found', 'nodes_explored'
    """
    empty_cells = SudokuHelper.get_empty_cells(problem_board)
    stats = {"nodes": 0}

    def or_search(state: tuple, remaining: List[Tuple[int, int]],
                  plan: ConditionalPlan) -> bool:
        """
        OR node: Chọn giá trị cho ô hiện tại.
        Chỉ cần TÌM ĐƯỢC MỘT giá trị khiến AND thành công → trả về True.
        """
        if not remaining:
            return True  # Hết ô trống → thành công!

        stats["nodes"] += 1
        row, col = remaining[0]
        rest = remaining[1:]

        # OR: thử từng giá trị hợp lệ
        valid_values = SudokuHelper.get_valid_values(state, row, col)
        for value in valid_values:
            # Đặt giá trị
            new_state = list(state)
            new_state[row * 9 + col] = value
            new_state = tuple(new_state)

            # AND: tất cả ô còn lại phải giải được
            if and_search_node(new_state, rest, plan):
                plan.add(row, col, value)
                return True

        return False  # Không giá trị nào hoạt động → thất bại

    def and_search_node(state: tuple, remaining: List[Tuple[int, int]],
                        plan: ConditionalPlan) -> bool:
        """
        AND node: TẤT CẢ ô còn lại phải giải được.
        Trong Sudoku deterministic, AND chỉ có 1 "outcome" → gọi OR tiếp.

        Trong bài toán nondeterministic, AND sẽ xử lý nhiều outcomes:
        for each outcome of action:
            if not or_search(outcome, ...): return False
        return True
        """
        stats["nodes"] += 1
        # Kiểm tra dead-end: có ô trống nào không có giá trị hợp lệ?
        for r, c in remaining:
            if not SudokuHelper.get_valid_values(state, r, c):
                return False  # Dead-end!

        # Gọi OR search cho phần còn lại
        return or_search(state, remaining, plan)

    plan = ConditionalPlan()
    found = or_search(problem_board, empty_cells, plan)
    plan.nodes_explored = stats["nodes"]

    if found:
        # Xây dựng bảng kết quả
        result_board = list(problem_board)
        for (r, c), v in plan.assignments.items():
            result_board[r * 9 + c] = v
        return {
            'algorithm': 'AND-OR Search',
            'board': tuple(result_board),
            'plan': plan,
            'found': True,
            'nodes_explored': stats["nodes"],
        }
    return {
        'algorithm': 'AND-OR Search',
        'board': problem_board,
        'plan': plan,
        'found': False,
        'nodes_explored': stats["nodes"],
    }


# =============================================================================
# 11. SENSORLESS SEARCH - Tìm kiếm không quan sát
# =============================================================================
def sensorless_search(problem_board: tuple, uncertain_indices: List[int] = None) -> dict:
    """
    Sensorless Search (Conformant Search) - Tìm kiếm không có quan sát.

    ╔════════════════════════════════════════════════════════════╗
    ║  Bối cảnh: Agent KHÔNG THỂ quan sát trạng thái.          ║
    ║  Phải tìm kế hoạch hoạt động cho MỌI trạng thái ban đầu ║
    ║  có thể.                                                  ║
    ║                                                            ║
    ║  Khái niệm chính: BELIEF STATE                           ║
    ║  = tập hợp các trạng thái agent tin là có thể            ║
    ╚════════════════════════════════════════════════════════════╝

    Mô hình cho Sudoku:
    ────────────────────
    - Một số ô ban đầu "không chắc chắn" (uncertain):
      agent không biết giá trị thực của chúng
    - Belief state = tập các khả năng cho mỗi ô uncertain
    - Action = xác định giá trị cho một ô
    - Goal = mọi ô đều chỉ có 1 giá trị khả dĩ

    Biểu diễn Belief State (compact):
    ──────────────────────────────────
    Thay vì lưu tập tất cả bảng Sudoku khả dĩ (quá lớn),
    ta biểu diễn bằng DOMAIN cho mỗi ô:
    - Ô đã biết: domain = {giá trị}
    - Ô uncertain: domain = {các giá trị khả dĩ}
    - Ô trống: domain = {1..9} trừ ràng buộc

    Args:
        problem_board:     tuple 81 phần tử
        uncertain_indices: danh sách index các ô "không chắc chắn"
                          (mặc định: chọn 3 ô đã cho làm uncertain)

    Returns:
        dict với keys: 'board', 'plan', 'found', 'nodes_explored'
    """
    stats = {"nodes": 0}

    # ── Thiết lập belief state ban đầu ──
    # Mỗi ô có một domain (tập giá trị khả dĩ)
    domains = {}
    for i in range(81):
        row, col = i // 9, i % 9
        if problem_board[i] != 0:
            domains[i] = {problem_board[i]}
        else:
            domains[i] = set(range(1, 10))

    # Tạo uncertain cells: một số ô "đã biết" trở thành uncertain
    if uncertain_indices is None:
        # Chọn 3 ô đã cho để làm uncertain
        given = [i for i in range(81) if problem_board[i] != 0]
        uncertain_indices = given[:3] if len(given) >= 3 else given

    for idx in uncertain_indices:
        if problem_board[idx] != 0:
            row, col = idx // 9, idx % 9
            valid = SudokuHelper.get_valid_values(
                tuple(0 if i in uncertain_indices else problem_board[i]
                      for i in range(81)),
                row, col
            )
            domains[idx] = set(valid) if valid else {problem_board[idx]}

    # ── Propagate constraints ──
    def propagate(domains: Dict[int, set]) -> Optional[Dict[int, set]]:
        """Arc consistency: loại bỏ giá trị không hợp lệ."""
        changed = True
        while changed:
            changed = False
            for i in range(81):
                if len(domains[i]) == 1:
                    val = next(iter(domains[i]))
                    row, col = i // 9, i % 9
                    # Loại val khỏi peers
                    for pr, pc in SudokuHelper.get_peers(row, col):
                        pidx = pr * 9 + pc
                        if val in domains[pidx] and len(domains[pidx]) > 1:
                            domains[pidx] = domains[pidx] - {val}
                            changed = True
                            if len(domains[pidx]) == 0:
                                return None  # Contradiction!
        return domains

    # ── BFS trên belief states ──
    def search(domains: Dict[int, set]) -> Optional[List[Tuple[int, int]]]:
        """Tìm kế hoạch: gán giá trị cho các ô có domain > 1."""
        stats["nodes"] += 1

        domains = propagate(copy.deepcopy(domains))
        if domains is None:
            return None

        # Kiểm tra goal: mọi domain có size = 1
        unresolved = [(i, domains[i]) for i in range(81) if len(domains[i]) > 1]
        if not unresolved:
            return []

        # Chọn ô có domain nhỏ nhất (MRV heuristic)
        idx, domain = min(unresolved, key=lambda x: len(x[1]))
        row, col = idx // 9, idx % 9

        for value in sorted(domain):
            new_domains = copy.deepcopy(domains)
            new_domains[idx] = {value}

            result = search(new_domains)
            if result is not None:
                return [(idx, value)] + result

        return None

    plan = search(domains)

    if plan is not None:
        # Xây dựng bảng kết quả
        result_domains = copy.deepcopy(domains)
        for idx, value in plan:
            result_domains[idx] = {value}
        result_domains = propagate(result_domains)

        result_board = list(problem_board)
        if result_domains:
            for i in range(81):
                if len(result_domains[i]) == 1:
                    result_board[i] = next(iter(result_domains[i]))

        return {
            'algorithm': 'Sensorless Search',
            'board': tuple(result_board),
            'plan': [f"R{i//9+1}C{i%9+1}={v}" for i, v in plan],
            'found': True,
            'nodes_explored': stats["nodes"],
            'uncertain_cells': uncertain_indices,
        }

    return {
        'algorithm': 'Sensorless Search',
        'board': problem_board,
        'plan': [],
        'found': False,
        'nodes_explored': stats["nodes"],
        'uncertain_cells': uncertain_indices,
    }


# =============================================================================
# 12. PARTIALLY OBSERVABLE SEARCH
# =============================================================================
def partial_observable_search(problem_board: tuple,
                              observable_radius: int = 1) -> dict:
    """
    Partially Observable Search - Tìm kiếm trong môi trường quan sát một phần.

    ╔════════════════════════════════════════════════════════════╗
    ║  Bối cảnh: Agent chỉ quan sát được MỘT PHẦN bảng.       ║
    ║  Sau mỗi hành động, agent nhận quan sát (observation)    ║
    ║  và cập nhật belief state.                                ║
    ║                                                            ║
    ║  Belief State + Observation → Updated Belief State       ║
    ╚════════════════════════════════════════════════════════════╝

    Mô hình cho Sudoku:
    ────────────────────
    - Agent chỉ thấy các ô trong bán kính observable_radius
      xung quanh ô vừa điền
    - Sau khi đặt giá trị, agent quan sát xung quanh:
      + Nếu hợp lệ → tiếp tục
      + Nếu xung đột → cập nhật belief state, thử giá trị khác
    - Belief state = domains cho mỗi ô (compact representation)

    Logic cốt lõi:
    ─────────────
    1. Khởi tạo belief state = domains từ các ô observable
    2. Lặp:
       a. Chọn ô cần điền (MRV trong belief state)
       b. Thử giá trị → đặt vào
       c. Quan sát (observe) các ô xung quanh
       d. Cập nhật belief state dựa trên observation
       e. Nếu contradiction → backtrack
    3. Khi mọi ô đã xác định → trả về plan

    Args:
        problem_board:      tuple 81 phần tử
        observable_radius:  Bán kính quan sát (1 = ô liền kề)

    Returns:
        dict với keys: 'board', 'plan', 'found', 'nodes_explored',
                       'observations_made'
    """
    stats = {"nodes": 0, "observations": 0}

    # ── Xây dựng belief state ban đầu ──
    # Agent chỉ thấy một số ô ban đầu (giả sử thấy ô đã cho)
    known_cells = {i: problem_board[i] for i in range(81) if problem_board[i] != 0}
    empty_cells = [i for i in range(81) if problem_board[i] == 0]

    # Domains cho belief state
    domains = {}
    for i in range(81):
        if i in known_cells:
            domains[i] = {known_cells[i]}
        else:
            row, col = i // 9, i % 9
            valid = SudokuHelper.get_valid_values(problem_board, row, col)
            domains[i] = set(valid) if valid else set(range(1, 10))

    def observe(state: list, cell_idx: int, radius: int) -> Dict[int, int]:
        """
        Quan sát: trả về giá trị các ô trong bán kính radius
        xung quanh cell_idx.
        """
        stats["observations"] += 1
        row, col = cell_idx // 9, cell_idx % 9
        observed = {}

        for r in range(max(0, row - radius), min(9, row + radius + 1)):
            for c in range(max(0, col - radius), min(9, col + radius + 1)):
                idx = r * 9 + c
                if state[idx] != 0:
                    observed[idx] = state[idx]

        # Cũng quan sát peers (cùng hàng, cột, khối)
        for pr, pc in SudokuHelper.get_peers(row, col):
            pidx = pr * 9 + pc
            if state[pidx] != 0:
                observed[pidx] = state[pidx]

        return observed

    def update_belief(domains: Dict[int, set],
                      observation: Dict[int, int]) -> Optional[Dict[int, set]]:
        """Cập nhật belief state dựa trên observation."""
        new_domains = copy.deepcopy(domains)

        for idx, val in observation.items():
            new_domains[idx] = {val}

        # Propagate constraints
        changed = True
        while changed:
            changed = False
            for i in range(81):
                if len(new_domains[i]) == 1:
                    val = next(iter(new_domains[i]))
                    row, col = i // 9, i % 9
                    for pr, pc in SudokuHelper.get_peers(row, col):
                        pidx = pr * 9 + pc
                        if val in new_domains[pidx] and len(new_domains[pidx]) > 1:
                            new_domains[pidx] = new_domains[pidx] - {val}
                            changed = True
                            if len(new_domains[pidx]) == 0:
                                return None
        return new_domains

    # ── Tìm kiếm với belief state ──
    plan = []

    def search(current_state: list, domains: Dict[int, set]) -> bool:
        stats["nodes"] += 1

        # Cập nhật domains
        domains = update_belief(domains, {})
        if domains is None:
            return False

        # Kiểm tra: còn ô nào chưa xác định?
        unresolved = [(i, domains[i]) for i in range(81)
                      if len(domains[i]) > 1 or current_state[i] == 0]
        unresolved = [(i, d) for i, d in unresolved if current_state[i] == 0]

        if not unresolved:
            return True  # Mọi ô đã xác định

        # Chọn ô MRV (domain nhỏ nhất)
        idx, domain = min(unresolved, key=lambda x: len(x[1]))
        row, col = idx // 9, idx % 9

        for value in sorted(domain):
            # Thử đặt giá trị
            new_state = current_state[:]
            new_state[idx] = value

            # Quan sát xung quanh
            obs = observe(new_state, idx, observable_radius)

            # Cập nhật belief state
            new_domains = copy.deepcopy(domains)
            new_domains[idx] = {value}
            new_domains = update_belief(new_domains, obs)

            if new_domains is None:
                continue  # Contradiction → thử giá trị khác

            plan.append(f"R{row+1}C{col+1}={value}")

            if search(new_state, new_domains):
                return True

            plan.pop()  # Backtrack

        return False

    current = list(problem_board)
    found = search(current, copy.deepcopy(domains))

    if found:
        # Xây dựng bảng kết quả
        result_board = list(problem_board)
        for action in plan:
            # Parse "R{r}C{c}={v}"
            parts = action.replace('R', '').replace('C', '').replace('=', ' ').split()
            r, c, v = int(parts[0]) - 1, int(parts[1]) - 1, int(parts[2])
            result_board[r * 9 + c] = v

        return {
            'algorithm': 'Partial Observable Search',
            'board': tuple(result_board),
            'plan': plan,
            'found': True,
            'nodes_explored': stats["nodes"],
            'observations_made': stats["observations"],
        }

    return {
        'algorithm': 'Partial Observable Search',
        'board': problem_board,
        'plan': [],
        'found': False,
        'nodes_explored': stats["nodes"],
        'observations_made': stats["observations"],
    }
