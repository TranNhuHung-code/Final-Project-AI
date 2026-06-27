"""
=============================================================================
  NHÓM 3: LOCAL SEARCH ALGORITHMS (Tìm kiếm cục bộ)
=============================================================================
Các thuật toán trong nhóm này KHÔNG xây dựng cây tìm kiếm.
Chúng bắt đầu từ một trạng thái và di chuyển đến trạng thái lân cận.

Gồm 3 thuật toán:
  7. Hill Climbing (Steepest-Ascent)  — chọn neighbor tốt nhất
  8. Local Beam Search               — duy trì k trạng thái song song
  9. Simulated Annealing             — chấp nhận xấu hơn với xác suất giảm dần

Mô hình Local Search cho Sudoku:
────────────────────────────────
KHÁC với Tree Search! Ở đây:
  1. Bắt đầu: Điền ngẫu nhiên mỗi khối 3×3 sao cho mỗi khối có đủ 1-9
     (giữ nguyên các ô đã cho → ràng buộc khối luôn thỏa)
  2. Đánh giá: cost = số giá trị trùng lặp trong hàng + cột
     (khối đã thỏa by construction)
  3. Neighbor: Swap 2 ô KHÔNG phải ô cho trước trong cùng khối 3×3
     (giữ ràng buộc khối, cố giảm xung đột hàng/cột)
  4. Goal: cost = 0 (không còn xung đột)
=============================================================================
"""
import random
import math
import copy
from typing import List, Tuple, Optional, Dict
from search_algorithms.core.sudoku import SudokuHelper


# =============================================================================
#  SUDOKU LOCAL SEARCH MODEL
# =============================================================================
class SudokuLocalModel:
    """
    Mô hình Sudoku cho Local Search.

    Khác biệt chính so với SudokuProblem (Tree Search):
    ────────────────────────────────────────────────────
    - Bắt đầu từ bảng ĐÃ ĐIỀN ĐẦY (random), không phải bảng có ô trống
    - Đánh giá bằng SỐ XUNG ĐỘT (cost), không phải goal_test
    - Di chuyển bằng SWAP trong khối, không phải đặt giá trị vào ô trống
    """

    def __init__(self, initial_board: tuple):
        """
        Args:
            initial_board: tuple 81 phần tử, 0 = ô trống cần điền
        """
        self.initial_board = initial_board
        # Lưu vị trí các ô đã cho (given) — không được swap
        self.given_cells = frozenset(i for i in range(81) if initial_board[i] != 0)

    def random_fill(self) -> list:
        """
        Điền ngẫu nhiên mỗi khối 3×3 sao cho mỗi khối có đủ {1,...,9}.
        Giữ nguyên các ô đã cho (given cells).

        Returns:
            list 81 phần tử — bảng đã điền đầy
        """
        board = list(self.initial_board)

        for block_row in range(3):
            for block_col in range(3):
                # Xác định vị trí ô trong khối
                indices = []
                existing = set()
                for r in range(3):
                    for c in range(3):
                        idx = (block_row * 3 + r) * 9 + (block_col * 3 + c)
                        indices.append(idx)
                        if board[idx] != 0:
                            existing.add(board[idx])

                # Giá trị còn thiếu trong khối
                missing = [v for v in range(1, 10) if v not in existing]
                random.shuffle(missing)

                # Điền vào các ô trống
                j = 0
                for idx in indices:
                    if board[idx] == 0:
                        board[idx] = missing[j]
                        j += 1

        return board

    def cost(self, board: list) -> int:
        """
        Tính chi phí = tổng số giá trị trùng lặp trong hàng + cột.

        Chỉ đếm xung đột hàng và cột (khối đã thỏa by construction).
        Cost = 0 ⟹ bảng Sudoku hợp lệ!
        """
        conflicts = 0
        for i in range(9):
            # Xung đột trong hàng i
            row = [board[i * 9 + c] for c in range(9)]
            conflicts += 9 - len(set(row))
            # Xung đột trong cột i
            col = [board[r * 9 + i] for r in range(9)]
            conflicts += 9 - len(set(col))
        return conflicts

    def get_swappable_cells(self, block_row: int, block_col: int) -> List[int]:
        """Lấy danh sách index các ô KHÔNG phải ô cho trước trong khối."""
        cells = []
        for r in range(3):
            for c in range(3):
                idx = (block_row * 3 + r) * 9 + (block_col * 3 + c)
                if idx not in self.given_cells:
                    cells.append(idx)
        return cells

    def get_neighbors(self, board: list) -> List[Tuple[list, Tuple[int, int, int, int]]]:
        """
        Sinh tất cả trạng thái lân cận bằng cách swap 2 ô non-given trong cùng khối.

        Returns:
            List of (new_board, (block_row, block_col, idx1, idx2))
        """
        neighbors = []
        for br in range(3):
            for bc in range(3):
                swappable = self.get_swappable_cells(br, bc)
                # Thử tất cả cặp swap trong khối
                for i in range(len(swappable)):
                    for j in range(i + 1, len(swappable)):
                        idx1, idx2 = swappable[i], swappable[j]
                        new_board = board[:]
                        new_board[idx1], new_board[idx2] = new_board[idx2], new_board[idx1]
                        neighbors.append((new_board, (br, bc, idx1, idx2)))
        return neighbors


# =============================================================================
# 7. HILL CLIMBING (Steepest-Ascent) - Leo đồi dốc nhất
# =============================================================================
def hill_climbing(problem_board: tuple, max_restarts: int = 10,
                  max_steps: int = 5000) -> dict:
    """
    Hill Climbing (Steepest-Ascent) - Leo đồi dốc nhất.

    ╔════════════════════════════════════════════════════════════╗
    ║  Chiến lược: Tại mỗi bước, chọn neighbor có cost THẤP   ║
    ║  NHẤT (ít xung đột nhất). Dừng khi không cải thiện được.║
    ║  Nhược điểm: dễ bị kẹt ở local optimum                  ║
    ║  Giải pháp: Random restart — bắt đầu lại nếu bị kẹt    ║
    ╚════════════════════════════════════════════════════════════╝

    Logic cốt lõi:
    ─────────────
    1. Tạo trạng thái ban đầu (random fill)
    2. Lặp:
       a. Tính cost hiện tại
       b. Sinh tất cả neighbors
       c. Tìm neighbor có cost thấp nhất
       d. Nếu best_neighbor_cost ≥ current_cost → STUCK (local optimum)
       e. Ngược lại → di chuyển sang best neighbor
    3. Nếu stuck → restart (random fill lại)

    Với Sudoku:
    ───────────
    - Mỗi khối 3×3 luôn chứa {1-9} (by construction)
    - Swap 2 ô non-given trong khối → cố giảm xung đột hàng/cột
    - Cost = 0 → lời giải hoàn chỉnh

    Args:
        problem_board: tuple 81 phần tử (bảng Sudoku ban đầu)
        max_restarts:  Số lần restart tối đa
        max_steps:     Số bước tối đa mỗi lần chạy

    Returns:
        dict với keys: 'board', 'cost', 'steps', 'restarts', 'found'
    """
    model = SudokuLocalModel(problem_board)
    total_steps = 0

    for restart in range(max_restarts):
        # Bắt đầu từ trạng thái random
        current = model.random_fill()
        current_cost = model.cost(current)

        for step in range(max_steps):
            total_steps += 1

            if current_cost == 0:
                return {
                    'algorithm': 'Hill Climbing',
                    'board': tuple(current),
                    'cost': 0,
                    'steps': total_steps,
                    'restarts': restart,
                    'found': True,
                }

            # Tìm neighbor tốt nhất (steepest ascent = steepest descent on cost)
            best_neighbor = None
            best_cost = current_cost

            for neighbor, swap_info in model.get_neighbors(current):
                c = model.cost(neighbor)
                if c < best_cost:
                    best_cost = c
                    best_neighbor = neighbor

            if best_neighbor is None:
                # STUCK! Không có neighbor nào tốt hơn → local optimum
                break

            current = best_neighbor
            current_cost = best_cost

    # Hết restarts mà chưa tìm thấy
    return {
        'algorithm': 'Hill Climbing',
        'board': tuple(current),
        'cost': current_cost,
        'steps': total_steps,
        'restarts': max_restarts,
        'found': current_cost == 0,
    }


# =============================================================================
# 8. LOCAL BEAM SEARCH - Tìm kiếm chùm tia cục bộ
# =============================================================================
def local_beam_search(problem_board: tuple, k: int = 5,
                      max_steps: int = 5000) -> dict:
    """
    Local Beam Search - Duy trì k trạng thái song song.

    ╔════════════════════════════════════════════════════════════╗
    ║  Chiến lược: Thay vì 1 trạng thái (Hill Climbing),      ║
    ║  duy trì k trạng thái song song. Mỗi bước:              ║
    ║  - Sinh TẤT CẢ successors của k trạng thái              ║
    ║  - Chọn k trạng thái TỐT NHẤT trong tất cả successors  ║
    ║  Ưu điểm: khám phá nhiều vùng hơn Hill Climbing         ║
    ╚════════════════════════════════════════════════════════════╝

    Logic cốt lõi:
    ─────────────
    1. Tạo k trạng thái ban đầu (random fill)
    2. Lặp:
       a. Kiểm tra mỗi trạng thái → nếu cost=0 → trả về
       b. Sinh TẤT CẢ neighbors của k trạng thái
       c. Chọn k neighbors tốt nhất (cost thấp nhất)
       d. Thay thế k trạng thái hiện tại bằng k neighbors này

    Khác biệt với Random Restart:
    ──────────────────────────────
    - Random Restart: k lần chạy Hill Climbing ĐỘC LẬP
    - Beam Search: k trạng thái CHIA SẺ thông tin (chọn k tốt nhất từ pool chung)

    Args:
        problem_board: tuple 81 phần tử
        k:             Số lượng trạng thái duy trì (beam width)
        max_steps:     Số bước tối đa

    Returns:
        dict với keys: 'board', 'cost', 'steps', 'found'
    """
    model = SudokuLocalModel(problem_board)

    # Khởi tạo k trạng thái ngẫu nhiên
    beams = []
    for _ in range(k):
        board = model.random_fill()
        beams.append((model.cost(board), board))

    for step in range(max_steps):
        # Kiểm tra nếu có trạng thái đạt goal
        for cost, board in beams:
            if cost == 0:
                return {
                    'algorithm': f'Local Beam Search (k={k})',
                    'board': tuple(board),
                    'cost': 0,
                    'steps': step,
                    'found': True,
                }

        # Sinh tất cả neighbors từ tất cả k trạng thái
        all_candidates = []
        for cost, board in beams:
            for neighbor, _ in model.get_neighbors(board):
                c = model.cost(neighbor)
                all_candidates.append((c, neighbor))

        if not all_candidates:
            break

        # Chọn k neighbors tốt nhất
        all_candidates.sort(key=lambda x: x[0])
        beams = all_candidates[:k]

    # Trả về trạng thái tốt nhất
    best_cost, best_board = min(beams, key=lambda x: x[0])
    return {
        'algorithm': f'Local Beam Search (k={k})',
        'board': tuple(best_board),
        'cost': best_cost,
        'steps': max_steps,
        'found': best_cost == 0,
    }


# =============================================================================
# 9. SIMULATED ANNEALING - Ủ mô phỏng
# =============================================================================
def simulated_annealing(problem_board: tuple, initial_temp: float = 2.0,
                        cooling_rate: float = 0.9999,
                        min_temp: float = 0.001,
                        max_steps: int = 500000) -> dict:
    """
    Simulated Annealing - Ủ mô phỏng.

    ╔════════════════════════════════════════════════════════════╗
    ║  Chiến lược: Giống Hill Climbing nhưng CHẤP NHẬN nước   ║
    ║  đi XẤU HƠN với xác suất giảm dần theo "nhiệt độ".     ║
    ║  Nhiệt độ cao → chấp nhận dễ dàng (khám phá rộng)      ║
    ║  Nhiệt độ thấp → gần như Hill Climbing (khai thác sâu)  ║
    ╚════════════════════════════════════════════════════════════╝

    Logic cốt lõi:
    ─────────────
    1. T = initial_temperature
    2. current = random_state
    3. Lặp:
       a. Chọn ngẫu nhiên 1 neighbor
       b. ΔE = cost(neighbor) - cost(current)
       c. Nếu ΔE < 0 (tốt hơn) → chấp nhận luôn
       d. Nếu ΔE ≥ 0 (xấu hơn) → chấp nhận với xác suất e^(-ΔE/T)
       e. T = T × cooling_rate  (giảm nhiệt độ)
       f. Dừng khi T < min_temp hoặc cost = 0

    Xác suất chấp nhận nước đi xấu:
    ─────────────────────────────────
    P = e^(-ΔE / T)
    - T cao → P ≈ 1 (chấp nhận hầu hết)
    - T thấp → P ≈ 0 (từ chối hầu hết)
    - ΔE lớn → P nhỏ (nước đi càng xấu càng khó chấp nhận)

    Lý thuyết: Nếu cooling đủ chậm, SA hội tụ đến global optimum.

    Args:
        problem_board:  tuple 81 phần tử
        initial_temp:   Nhiệt độ ban đầu
        cooling_rate:   Tỷ lệ giảm nhiệt (0 < rate < 1)
        min_temp:       Nhiệt độ dừng
        max_steps:      Số bước tối đa

    Returns:
        dict với keys: 'board', 'cost', 'steps', 'temperature', 'found'
    """
    model = SudokuLocalModel(problem_board)
    current = model.random_fill()
    current_cost = model.cost(current)

    best = current[:]
    best_cost = current_cost

    temp = initial_temp

    for step in range(max_steps):
        if current_cost == 0:
            return {
                'algorithm': 'Simulated Annealing',
                'board': tuple(current),
                'cost': 0,
                'steps': step,
                'temperature': temp,
                'found': True,
            }

        if temp < min_temp:
            break

        # Chọn ngẫu nhiên 1 khối và 1 cặp swap
        br, bc = random.randint(0, 2), random.randint(0, 2)
        swappable = model.get_swappable_cells(br, bc)

        if len(swappable) < 2:
            temp *= cooling_rate
            continue

        # Chọn ngẫu nhiên 2 ô để swap
        idx1, idx2 = random.sample(swappable, 2)
        neighbor = current[:]
        neighbor[idx1], neighbor[idx2] = neighbor[idx2], neighbor[idx1]
        neighbor_cost = model.cost(neighbor)

        # Quyết định chấp nhận hay từ chối
        delta_e = neighbor_cost - current_cost

        if delta_e < 0:
            # Tốt hơn → chấp nhận luôn
            current = neighbor
            current_cost = neighbor_cost
        else:
            # Xấu hơn → chấp nhận với xác suất e^(-ΔE/T)
            probability = math.exp(-delta_e / temp)
            if random.random() < probability:
                current = neighbor
                current_cost = neighbor_cost

        # Cập nhật best
        if current_cost < best_cost:
            best = current[:]
            best_cost = current_cost

        # Giảm nhiệt độ
        temp *= cooling_rate

    return {
        'algorithm': 'Simulated Annealing',
        'board': tuple(best),
        'cost': best_cost,
        'steps': max_steps,
        'temperature': temp,
        'found': best_cost == 0,
    }
