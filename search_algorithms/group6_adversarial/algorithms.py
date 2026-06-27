"""
=============================================================================
  NHÓM 6: ADVERSARIAL SEARCH (Tìm kiếm đối kháng)
=============================================================================
Mô hình Sudoku như trò chơi 2 người (game theory):
  - Player MAX (Filler):  Chọn ô và đặt giá trị hợp lệ → muốn hoàn thành
  - Player MIN (Blocker): Chọn ô và đặt giá trị hợp lệ → muốn cản trở

Cả hai đều đặt giá trị HỢP LỆ (không vi phạm ràng buộc tại thời điểm đặt),
nhưng MIN cố tình chọn giá trị gây KHÓ KHĂN cho MAX sau này.

Gồm 3 thuật toán:
  16. Minimax          — MAX chọn tốt nhất, MIN chọn xấu nhất
  17. Alpha-Beta       — Minimax + cắt tỉa α-β
  18. Expectimax       — MAX + CHANCE node (đối thủ ngẫu nhiên)

Evaluation function:
  - Dương → có lợi cho MAX (nhiều lựa chọn, ít xung đột)
  - Âm   → có lợi cho MIN (ít lựa chọn, khó giải tiếp)
  - +1000 → MAX thắng (Sudoku hoàn thành)
  - -1000 → MIN thắng (dead-end, không thể tiếp tục)
=============================================================================
"""
import random
from typing import List, Tuple, Optional, Dict
from search_algorithms.core.sudoku import SudokuHelper


# =============================================================================
#  SUDOKU GAME MODEL
# =============================================================================
class SudokuGame:
    """
    Mô hình Sudoku đối kháng 2 người.

    Rules:
    ──────
    - Hai người chơi luân phiên đặt số vào ô trống
    - Mỗi nước đi phải hợp lệ (không trùng hàng/cột/khối)
    - MAX muốn hoàn thành bảng, MIN muốn tạo dead-end
    - Game kết thúc khi: bảng đầy HOẶC không còn nước đi hợp lệ
    """

    def __init__(self, board: tuple):
        self.initial_board = board
        self.given_cells = frozenset(i for i in range(81) if board[i] != 0)

    def get_moves(self, state: tuple) -> List[Tuple[int, int, int]]:
        """
        Lấy danh sách nước đi hợp lệ: (row, col, value).
        Chỉ xét ô trống đầu tiên (để giảm branching factor).
        """
        # Tìm ô trống đầu tiên
        for i in range(81):
            if state[i] == 0:
                row, col = i // 9, i % 9
                valid = SudokuHelper.get_valid_values(state, row, col)
                return [(row, col, v) for v in valid]
        return []

    def apply_move(self, state: tuple, row: int, col: int, value: int) -> tuple:
        """Áp dụng nước đi: đặt value vào ô (row, col)."""
        new_state = list(state)
        new_state[row * 9 + col] = value
        return tuple(new_state)

    def is_terminal(self, state: tuple) -> bool:
        """Kiểm tra trạng thái kết thúc (hết ô trống hoặc hết nước đi)."""
        if 0 not in state:
            return True
        # Kiểm tra ô trống đầu tiên có nước đi hợp lệ không
        return len(self.get_moves(state)) == 0

    def evaluate(self, state: tuple) -> float:
        """
        Evaluation function — đánh giá trạng thái.

        Công thức:
        ──────────
        - Nếu bảng hoàn thành hợp lệ → +1000 (MAX thắng)
        - Nếu dead-end (ô trống không có nước đi) → -1000 (MIN thắng)
        - Ngược lại: score = tổng domain_size cho mỗi ô trống
          (domain lớn = MAX có nhiều lựa chọn = tốt cho MAX)
        """
        empty_count = state.count(0)

        if empty_count == 0:
            if SudokuHelper.is_valid_complete(state):
                return 1000  # MAX thắng!
            else:
                return -1000  # Bảng đầy nhưng không hợp lệ

        # Tính tổng domain sizes
        total_options = 0
        for i in range(81):
            if state[i] == 0:
                row, col = i // 9, i % 9
                valid = SudokuHelper.get_valid_values(state, row, col)
                if not valid:
                    return -1000  # Dead-end!
                total_options += len(valid)

        # Normalize: tổng options / số ô trống → trung bình options mỗi ô
        return total_options / empty_count


# =============================================================================
# 16. MINIMAX - Thuật toán Minimax
# =============================================================================
def minimax(problem_board: tuple, max_depth: int = 4) -> dict:
    """
    Minimax Algorithm - Tìm kiếm đối kháng cơ bản.

    ╔════════════════════════════════════════════════════════════╗
    ║  Xây dựng GAME TREE đầy đủ đến depth giới hạn           ║
    ║  - MAX level: chọn nước đi có giá trị CAO NHẤT          ║
    ║  - MIN level: chọn nước đi có giá trị THẤP NHẤT         ║
    ║  Đảm bảo optimal play cho cả 2 bên                      ║
    ╚════════════════════════════════════════════════════════════╝

    Logic cốt lõi (đệ quy):
    ─────────────────────────
    MINIMAX(state, depth, is_max_turn):
      1. Nếu terminal hoặc depth = 0 → evaluate(state)
      2. Nếu MAX turn:
         return max(MINIMAX(child, depth-1, False) for child in moves)
      3. Nếu MIN turn:
         return min(MINIMAX(child, depth-1, True) for child in moves)

    Game tree cho Sudoku:
    ─────────────────────
    - Level 0 (MAX): MAX chọn ô + giá trị (muốn maximize evaluation)
    - Level 1 (MIN): MIN chọn ô + giá trị (muốn minimize evaluation)
    - Level 2 (MAX): MAX chọn lại...
    - Leaf: evaluate(state)

    Complexity:
    ───────────
    - Time:  O(b^d)  — b = branching factor, d = depth limit
    - Space: O(b·d)  — lưu stack đệ quy

    Args:
        problem_board: tuple 81 phần tử
        max_depth:     Độ sâu tối đa của game tree

    Returns:
        dict với keys: 'board', 'best_move', 'value', 'nodes_explored'
    """
    game = SudokuGame(problem_board)
    stats = {"nodes": 0}

    def minimax_value(state: tuple, depth: int, is_max: bool) -> float:
        stats["nodes"] += 1

        if depth == 0 or game.is_terminal(state):
            return game.evaluate(state)

        moves = game.get_moves(state)
        if not moves:
            return game.evaluate(state)

        if is_max:
            # MAX player: chọn giá trị cao nhất
            value = float('-inf')
            for row, col, val in moves:
                child = game.apply_move(state, row, col, val)
                value = max(value, minimax_value(child, depth - 1, False))
            return value
        else:
            # MIN player: chọn giá trị thấp nhất
            value = float('inf')
            for row, col, val in moves:
                child = game.apply_move(state, row, col, val)
                value = min(value, minimax_value(child, depth - 1, True))
            return value

    # Tìm nước đi tốt nhất cho MAX
    moves = game.get_moves(problem_board)
    best_move = None
    best_value = float('-inf')

    for row, col, val in moves:
        child = game.apply_move(problem_board, row, col, val)
        value = minimax_value(child, max_depth - 1, False)
        if value > best_value:
            best_value = value
            best_move = (row, col, val)

    # Áp dụng nước đi tốt nhất, rồi giải phần còn lại bằng backtracking
    if best_move:
        result_board = game.apply_move(problem_board, *best_move)
        # Tiếp tục chơi cho đến khi kết thúc
        result_board = _play_game(game, result_board, max_depth, 'minimax')
        return {
            'algorithm': 'Minimax',
            'board': result_board,
            'best_move': f"R{best_move[0]+1}C{best_move[1]+1}={best_move[2]}",
            'value': best_value,
            'found': 0 not in result_board and SudokuHelper.is_valid_complete(result_board),
            'nodes_explored': stats["nodes"],
        }

    return {
        'algorithm': 'Minimax',
        'board': problem_board,
        'best_move': None,
        'value': game.evaluate(problem_board),
        'found': False,
        'nodes_explored': stats["nodes"],
    }


# =============================================================================
# 17. ALPHA-BETA PRUNING - Cắt tỉa Alpha-Beta
# =============================================================================
def alpha_beta(problem_board: tuple, max_depth: int = 4) -> dict:
    """
    Alpha-Beta Pruning - Minimax với cắt tỉa thông minh.

    ╔════════════════════════════════════════════════════════════╗
    ║  Cải tiến Minimax: CẮT TỈA các nhánh không thể ảnh     ║
    ║  hưởng đến quyết định cuối cùng.                         ║
    ║                                                            ║
    ║  α (alpha) = giá trị TỐT NHẤT MAX đã đảm bảo được      ║
    ║  β (beta)  = giá trị TỐT NHẤT MIN đã đảm bảo được      ║
    ║  Cắt khi α ≥ β (không cần xét nhánh còn lại)            ║
    ╚════════════════════════════════════════════════════════════╝

    Logic cắt tỉa:
    ───────────────
    MAX node (α cập nhật):
      - α = max(α, value)
      - Nếu α ≥ β → CẮT (β cutoff)
        Lý do: MIN đã có lựa chọn ≤ β, sẽ không bao giờ chọn nhánh này

    MIN node (β cập nhật):
      - β = min(β, value)
      - Nếu α ≥ β → CẮT (α cutoff)
        Lý do: MAX đã có lựa chọn ≥ α, sẽ không bao giờ cho phép nhánh này

    So sánh với Minimax thuần:
    ──────────────────────────
    - Kết quả GIỐNG HỆT Minimax
    - Nhưng duyệt ÍT NODE hơn (trung bình sqrt(b^d) thay vì b^d)
    - Best case: O(b^(d/2)) — hiệu quả gấp đôi depth!

    Args:
        problem_board: tuple 81 phần tử
        max_depth:     Độ sâu tối đa

    Returns:
        dict với keys: 'board', 'best_move', 'value', 'nodes_explored', 'pruned'
    """
    game = SudokuGame(problem_board)
    stats = {"nodes": 0, "pruned": 0}

    def ab_value(state: tuple, depth: int, alpha: float, beta: float,
                 is_max: bool) -> float:
        stats["nodes"] += 1

        if depth == 0 or game.is_terminal(state):
            return game.evaluate(state)

        moves = game.get_moves(state)
        if not moves:
            return game.evaluate(state)

        if is_max:
            value = float('-inf')
            for row, col, val in moves:
                child = game.apply_move(state, row, col, val)
                value = max(value, ab_value(child, depth - 1, alpha, beta, False))
                alpha = max(alpha, value)
                if alpha >= beta:
                    stats["pruned"] += 1
                    break  # β cutoff!
            return value
        else:
            value = float('inf')
            for row, col, val in moves:
                child = game.apply_move(state, row, col, val)
                value = min(value, ab_value(child, depth - 1, alpha, beta, True))
                beta = min(beta, value)
                if alpha >= beta:
                    stats["pruned"] += 1
                    break  # α cutoff!
            return value

    # Tìm nước đi tốt nhất
    moves = game.get_moves(problem_board)
    best_move = None
    best_value = float('-inf')
    alpha = float('-inf')
    beta = float('inf')

    for row, col, val in moves:
        child = game.apply_move(problem_board, row, col, val)
        value = ab_value(child, max_depth - 1, alpha, beta, False)
        if value > best_value:
            best_value = value
            best_move = (row, col, val)
        alpha = max(alpha, best_value)

    if best_move:
        result_board = game.apply_move(problem_board, *best_move)
        result_board = _play_game(game, result_board, max_depth, 'alpha_beta')
        return {
            'algorithm': 'Alpha-Beta Pruning',
            'board': result_board,
            'best_move': f"R{best_move[0]+1}C{best_move[1]+1}={best_move[2]}",
            'value': best_value,
            'found': 0 not in result_board and SudokuHelper.is_valid_complete(result_board),
            'nodes_explored': stats["nodes"],
            'pruned': stats["pruned"],
        }

    return {
        'algorithm': 'Alpha-Beta Pruning',
        'board': problem_board,
        'best_move': None,
        'value': game.evaluate(problem_board),
        'found': False,
        'nodes_explored': stats["nodes"],
        'pruned': stats["pruned"],
    }


# =============================================================================
# 18. EXPECTIMAX - Minimax với nút Chance
# =============================================================================
def expectimax(problem_board: tuple, max_depth: int = 4) -> dict:
    """
    Expectimax - Minimax với đối thủ NGẪU NHIÊN.

    ╔════════════════════════════════════════════════════════════╗
    ║  Thay MIN node bằng CHANCE node:                         ║
    ║  - MAX node: chọn giá trị CAO NHẤT (như Minimax)         ║
    ║  - CHANCE node: tính GIÁ TRỊ KỲ VỌNG (trung bình)      ║
    ║                                                            ║
    ║  Mô hình: đối thủ không chơi tối ưu mà NGẪU NHIÊN      ║
    ║  → thực tế hơn khi đối thủ không hoàn hảo               ║
    ╚════════════════════════════════════════════════════════════╝

    Logic cốt lõi:
    ─────────────
    EXPECTIMAX(state, depth, is_max):
      1. Nếu terminal/depth=0 → evaluate(state)
      2. MAX node: max(children values)
      3. CHANCE node: average(children values)
         = Σ P(child) × value(child)
         với P(child) = 1/n (phân phối đều cho n nước đi)

    So sánh:
    ─────────
    - Minimax:   MAX vs MIN tối ưu → pessimistic (bi quan)
    - Expectimax: MAX vs CHANCE → realistic (thực tế hơn)
    - Không thể dùng alpha-beta cho Expectimax!
      (average có thể thay đổi khi thêm nhánh mới)

    Với Sudoku:
    ───────────
    CHANCE node = "đối thủ" chọn ngẫu nhiên giá trị cho ô tiếp theo.
    MAX phải tìm nước đi tốt TRUNG BÌNH (không chỉ worst case).

    Args:
        problem_board: tuple 81 phần tử
        max_depth:     Độ sâu tối đa

    Returns:
        dict với keys: 'board', 'best_move', 'value', 'nodes_explored'
    """
    game = SudokuGame(problem_board)
    stats = {"nodes": 0}

    def expectimax_value(state: tuple, depth: int, is_max: bool) -> float:
        stats["nodes"] += 1

        if depth == 0 or game.is_terminal(state):
            return game.evaluate(state)

        moves = game.get_moves(state)
        if not moves:
            return game.evaluate(state)

        if is_max:
            # MAX node: chọn giá trị cao nhất
            value = float('-inf')
            for row, col, val in moves:
                child = game.apply_move(state, row, col, val)
                value = max(value, expectimax_value(child, depth - 1, False))
            return value
        else:
            # CHANCE node: tính kỳ vọng (trung bình)
            total = 0
            for row, col, val in moves:
                child = game.apply_move(state, row, col, val)
                total += expectimax_value(child, depth - 1, True)
            return total / len(moves)  # Phân phối đều

    # Tìm nước đi tốt nhất cho MAX
    moves = game.get_moves(problem_board)
    best_move = None
    best_value = float('-inf')

    for row, col, val in moves:
        child = game.apply_move(problem_board, row, col, val)
        value = expectimax_value(child, max_depth - 1, False)
        if value > best_value:
            best_value = value
            best_move = (row, col, val)

    if best_move:
        result_board = game.apply_move(problem_board, *best_move)
        result_board = _play_game(game, result_board, max_depth, 'expectimax')
        return {
            'algorithm': 'Expectimax',
            'board': result_board,
            'best_move': f"R{best_move[0]+1}C{best_move[1]+1}={best_move[2]}",
            'value': best_value,
            'found': 0 not in result_board and SudokuHelper.is_valid_complete(result_board),
            'nodes_explored': stats["nodes"],
        }

    return {
        'algorithm': 'Expectimax',
        'board': problem_board,
        'best_move': None,
        'value': game.evaluate(problem_board),
        'found': False,
        'nodes_explored': stats["nodes"],
    }


# =============================================================================
#  HELPER: Play game to completion
# =============================================================================
def _play_game(game: SudokuGame, state: tuple, depth: int,
               method: str) -> tuple:
    """
    Tiếp tục chơi game cho đến khi kết thúc.
    MAX dùng thuật toán đã chọn, MIN chọn giá trị gây khó nhất.

    Dùng nội bộ để hoàn thành bảng Sudoku sau khi tìm nước đi đầu tiên.
    """
    current = state
    is_max_turn = False  # Nước đi đầu đã chơi (MAX), tiếp theo là MIN

    for _ in range(81):
        if game.is_terminal(current):
            break

        moves = game.get_moves(current)
        if not moves:
            break

        if is_max_turn:
            # MAX: chọn nước tốt nhất đơn giản (greedy)
            best_val = float('-inf')
            best_m = moves[0]
            for r, c, v in moves:
                child = game.apply_move(current, r, c, v)
                ev = game.evaluate(child)
                if ev > best_val:
                    best_val = ev
                    best_m = (r, c, v)
            current = game.apply_move(current, *best_m)
        else:
            # MIN: chọn nước "xấu nhất" cho MAX
            worst_val = float('inf')
            worst_m = moves[0]
            for r, c, v in moves:
                child = game.apply_move(current, r, c, v)
                ev = game.evaluate(child)
                if ev < worst_val:
                    worst_val = ev
                    worst_m = (r, c, v)
            current = game.apply_move(current, *worst_m)

        is_max_turn = not is_max_turn

    return current
