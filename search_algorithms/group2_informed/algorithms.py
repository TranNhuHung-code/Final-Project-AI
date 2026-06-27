"""
=============================================================================
  NHÓM 2: INFORMED SEARCH ALGORITHMS (Tìm kiếm có thông tin)
=============================================================================
Các thuật toán trong nhóm này SỬ DỤNG heuristic h(n) để ước lượng
chi phí từ trạng thái hiện tại đến đích, giúp định hướng tìm kiếm.

Gồm 3 thuật toán:
  4. Greedy Best-First Search  — Frontier ưu tiên theo h(n)
  5. A* Search                 — Frontier ưu tiên theo f(n) = g(n) + h(n)
  6. IDA* Search               — IDS + A*, dùng f-limit thay depth-limit

Heuristic cho Sudoku:
  h(n) = số ô trống còn lại (admissible, consistent)
  Nếu phát hiện dead-end (ô trống không có giá trị hợp lệ) → h = ∞
=============================================================================
"""
import heapq
from typing import Optional
from search_algorithms.core.problem_base import Problem, Node, SearchResult


# =============================================================================
# 4. GREEDY BEST-FIRST SEARCH - Tìm kiếm tham lam
# =============================================================================
def greedy_best_first(problem: Problem) -> SearchResult:
    """
    Greedy Best-First Search - Tìm kiếm tham lam theo heuristic.

    ╔════════════════════════════════════════════════════════════╗
    ║  Cấu trúc dữ liệu Frontier: PRIORITY QUEUE              ║
    ║  Key sắp xếp: h(n) — heuristic (ước lượng đến đích)     ║
    ║  Chiến lược: Mở rộng node có h(n) NHỎ NHẤT              ║
    ║  KHÔNG đảm bảo tìm lời giải tối ưu                      ║
    ╚════════════════════════════════════════════════════════════╝

    Logic cốt lõi:
    ─────────────
    1. Khởi tạo frontier = Priority Queue, key = h(n)
    2. Lặp:
       a. Lấy node có h(n) nhỏ nhất
       b. Nếu goal_test → trả về
       c. Mở rộng node, thêm children vào frontier

    Tại sao "tham lam"?
    ────────────────────
    Luôn chọn node TRÔNG GẦN ĐÍCH NHẤT (h nhỏ nhất) mà không
    quan tâm chi phí đã đi (g). Nhanh nhưng có thể bị "lừa".

    Với Sudoku:
    ───────────
    h(n) = số ô trống → ưu tiên trạng thái gần hoàn thành nhất.
    Khi phát hiện ô trống không có giá trị hợp lệ → h = ∞ (tránh dead-end).

    Complexity:
    ───────────
    - Time:  O(b^m) worst case, nhưng thường nhanh hơn nhiều
    - Space: O(b^m)

    Args:
        problem: Đối tượng Problem (SudokuProblem)

    Returns:
        SearchResult chứa kết quả tìm kiếm
    """
    root = problem.make_node(problem.initial_state())

    if problem.goal_test(root.state):
        return SearchResult("Greedy Best-First", root, 0, 1)

    # Priority Queue: (h(n), counter, node)
    # counter dùng để phá vỡ tie khi h(n) bằng nhau (tránh so sánh Node)
    counter = 0
    frontier = [(problem.heuristic(root.state), counter, root)]
    heapq.heapify(frontier)

    # Tra cứu nhanh: state → đã nằm trong frontier chưa
    frontier_states = {root.state}

    explored = set()
    nodes_expanded = 0
    max_frontier_size = 1

    while frontier:
        h_val, _, node = heapq.heappop(frontier)
        frontier_states.discard(node.state)

        # Bỏ qua nếu h = ∞ (dead-end)
        if h_val == float('inf'):
            continue

        if problem.goal_test(node.state):
            return SearchResult("Greedy Best-First", node,
                                nodes_expanded, max_frontier_size)

        explored.add(node.state)
        nodes_expanded += 1

        for child in problem.expand(node):
            if child.state not in explored and child.state not in frontier_states:
                h = problem.heuristic(child.state)
                if h != float('inf'):  # Bỏ qua dead-end
                    counter += 1
                    heapq.heappush(frontier, (h, counter, child))
                    frontier_states.add(child.state)

        max_frontier_size = max(max_frontier_size, len(frontier))

    return SearchResult("Greedy Best-First", None, nodes_expanded, max_frontier_size)


# =============================================================================
# 5. A* SEARCH - Tìm kiếm A*
# =============================================================================
def astar(problem: Problem) -> SearchResult:
    """
    A* Search - Thuật toán tìm kiếm tối ưu với heuristic.

    ╔════════════════════════════════════════════════════════════╗
    ║  Cấu trúc dữ liệu Frontier: PRIORITY QUEUE              ║
    ║  Key sắp xếp: f(n) = g(n) + h(n)                        ║
    ║     g(n) = chi phí thực từ gốc đến n                     ║
    ║     h(n) = ước lượng chi phí từ n đến đích               ║
    ║  Đảm bảo OPTIMAL nếu h(n) admissible & consistent       ║
    ╚════════════════════════════════════════════════════════════╝

    Logic cốt lõi:
    ─────────────
    1. Frontier = Priority Queue theo f(n) = g(n) + h(n)
    2. Lặp:
       a. Lấy node có f(n) nhỏ nhất
       b. Nếu goal_test → trả về (đảm bảo optimal!)
       c. Thêm vào explored
       d. Mở rộng, cập nhật frontier

    So sánh với Greedy:
    ────────────────────
    - Greedy: chỉ dùng h(n) → nhanh nhưng không optimal
    - A*:     dùng g(n) + h(n) → cân bằng giữa chi phí đã đi và ước lượng

    Với Sudoku:
    ───────────
    g(n) = số ô đã điền, h(n) = số ô trống còn lại
    → f(n) = g(n) + h(n) = tổng số ô trống ban đầu (hằng số!)
    Do đó A* hoạt động tương tự BFS cho Sudoku khi dùng heuristic đơn giản.
    Dead-end detection (h=∞) giúp A* cắt tỉa hiệu quả hơn.

    Complexity:
    ───────────
    - Time:  O(b^d) — phụ thuộc chất lượng heuristic
    - Space: O(b^d) — lưu toàn bộ frontier

    Args:
        problem: Đối tượng Problem (SudokuProblem)

    Returns:
        SearchResult chứa kết quả tìm kiếm
    """
    root = problem.make_node(problem.initial_state())

    if problem.goal_test(root.state):
        return SearchResult("A*", root, 0, 1)

    h_root = problem.heuristic(root.state)
    f_root = root.cost + h_root  # f = g + h

    counter = 0
    frontier = [(f_root, h_root, counter, root)]
    heapq.heapify(frontier)

    # Lưu g tốt nhất đã biết cho mỗi state
    best_g = {root.state: root.cost}

    explored = set()
    nodes_expanded = 0
    max_frontier_size = 1

    while frontier:
        f_val, h_val, _, node = heapq.heappop(frontier)

        # Bỏ qua nếu đã tìm thấy đường tốt hơn đến state này
        if node.state in explored:
            continue

        if problem.goal_test(node.state):
            return SearchResult("A*", node, nodes_expanded, max_frontier_size)

        explored.add(node.state)
        nodes_expanded += 1

        for child in problem.expand(node):
            if child.state not in explored:
                h = problem.heuristic(child.state)
                if h == float('inf'):
                    continue  # Bỏ qua dead-end

                f = child.cost + h
                # Chỉ thêm nếu tìm được đường tốt hơn
                if child.state not in best_g or child.cost < best_g[child.state]:
                    best_g[child.state] = child.cost
                    counter += 1
                    heapq.heappush(frontier, (f, h, counter, child))

        max_frontier_size = max(max_frontier_size, len(frontier))

    return SearchResult("A*", None, nodes_expanded, max_frontier_size)


# =============================================================================
# 6. IDA* SEARCH - Iterative Deepening A*
# =============================================================================
def ida_star(problem: Problem) -> SearchResult:
    """
    IDA* Search - Kết hợp IDS và A*.

    ╔════════════════════════════════════════════════════════════╗
    ║  Chiến lược: IDS nhưng dùng f-limit thay vì depth-limit ║
    ║  f-limit tăng dần ở mỗi vòng lặp                        ║
    ║  Ưu điểm: Optimal như A* nhưng bộ nhớ O(b·d) như DFS    ║
    ╚════════════════════════════════════════════════════════════╝

    Logic cốt lõi:
    ─────────────
    1. f_limit = h(root) — bắt đầu từ ước lượng của trạng thái gốc
    2. Lặp:
       a. Chạy DFS với giới hạn f ≤ f_limit
       b. Nếu tìm thấy → trả về
       c. Nếu bị cắt → f_limit = min(f vượt quá limit cũ)
       d. Nếu f_limit = ∞ → không có lời giải

    So sánh IDA* với A*:
    ─────────────────────
    - A*:   lưu toàn bộ OPEN list → Space O(b^d)
    - IDA*: chỉ lưu stack hiện tại → Space O(b·d)
    - Cả hai đều optimal với heuristic admissible

    Với Sudoku:
    ───────────
    IDA* rất hiệu quả cho Sudoku: bộ nhớ thấp, optimal,
    và dead-end detection qua h=∞ giúp cắt tỉa mạnh.

    Complexity:
    ───────────
    - Time:  O(b^d) — tương tự A*
    - Space: O(b·d) — tương tự DFS/IDS

    Args:
        problem: Đối tượng Problem (SudokuProblem)

    Returns:
        SearchResult chứa kết quả tìm kiếm
    """
    root = problem.make_node(problem.initial_state())

    if problem.goal_test(root.state):
        return SearchResult("IDA*", root, 0, 1)

    h_root = problem.heuristic(root.state)
    if h_root == float('inf'):
        return SearchResult("IDA*", None, 0, 0)

    f_limit = h_root
    stats = {"expanded": 0, "max_frontier": 1}

    def search(node: Node, g: float, f_limit: float) -> tuple:
        """
        DFS có giới hạn f.

        Returns:
            (node_or_None, next_f_limit)
            - Nếu tìm thấy: (solution_node, f_limit)
            - Nếu bị cắt:   (None, min_f_over_limit)
        """
        f = g + problem.heuristic(node.state)

        if f > f_limit:
            return None, f  # Vượt quá limit → cắt

        if problem.goal_test(node.state):
            return node, f_limit

        stats["expanded"] += 1
        min_over = float('inf')  # f nhỏ nhất vượt quá limit

        children = problem.expand(node)
        stats["max_frontier"] = max(stats["max_frontier"], len(children))

        for child in children:
            h_child = problem.heuristic(child.state)
            if h_child == float('inf'):
                continue  # Bỏ qua dead-end

            result, new_f = search(child, child.cost, f_limit)
            if result is not None:
                return result, new_f
            min_over = min(min_over, new_f)

        return None, min_over

    # Vòng lặp chính: tăng f_limit dần
    while f_limit != float('inf'):
        solution, new_limit = search(root, 0, f_limit)
        if solution is not None:
            return SearchResult("IDA*", solution,
                                stats["expanded"], stats["max_frontier"])
        f_limit = new_limit

    return SearchResult("IDA*", None, stats["expanded"], stats["max_frontier"])
