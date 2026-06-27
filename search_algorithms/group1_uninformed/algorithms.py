"""
=============================================================================
  NHÓM 1: UNINFORMED SEARCH ALGORITHMS (Tìm kiếm không có thông tin)
=============================================================================
Các thuật toán trong nhóm này KHÔNG sử dụng heuristic.
Chúng chỉ dựa vào cấu trúc của cây/đồ thị tìm kiếm.

Gồm 3 thuật toán:
  1. Breadth-First Search (BFS)  — Frontier: Queue (FIFO)
  2. Depth-First Search (DFS)    — Frontier: Stack (LIFO)
  3. Iterative Deepening Search  — DFS lặp với depth tăng dần

Áp dụng cho Sudoku:
  - Mỗi node = trạng thái bảng Sudoku (tuple 81 phần tử)
  - Successor = điền một giá trị hợp lệ vào ô trống đầu tiên
  - Goal = bảng đã điền đầy đủ và hợp lệ
=============================================================================
"""
from collections import deque
from typing import Optional
from search_algorithms.core.problem_base import Problem, Node, SearchResult


# =============================================================================
# 1. BREADTH-FIRST SEARCH (BFS) - Tìm kiếm theo chiều rộng
# =============================================================================
def bfs(problem: Problem) -> SearchResult:
    """
    Breadth-First Search (BFS) - Tìm kiếm theo chiều rộng.

    ╔════════════════════════════════════════════════════════════╗
    ║  Cấu trúc dữ liệu Frontier: QUEUE (FIFO - hàng đợi)    ║
    ║  Chiến lược: Mở rộng node NÔNG NHẤT trước               ║
    ║  Đảm bảo: Tìm thấy lời giải NGẮN NHẤT (optimal nếu     ║
    ║           step cost đồng nhất)                            ║
    ╚════════════════════════════════════════════════════════════╝

    Logic cốt lõi:
    ─────────────
    1. Khởi tạo frontier = Queue chứa node gốc
    2. Khởi tạo explored = Set rỗng (tập đã duyệt)
    3. Lặp:
       a. Nếu frontier rỗng → thất bại
       b. Lấy node đầu tiên ra khỏi frontier (dequeue)
       c. Thêm state của node vào explored
       d. Với mỗi child của node:
          - Nếu child.state chưa ở explored VÀ chưa ở frontier:
            + Nếu goal_test(child.state) → trả về child
            + Ngược lại → thêm child vào frontier (enqueue)

    Tại sao dùng Queue (FIFO)?
    ──────────────────────────
    Queue đảm bảo các node được mở rộng theo thứ tự từ nông → sâu.
    Tất cả node ở depth d được duyệt hết trước khi sang depth d+1.

    Với Sudoku:
    ───────────
    BFS sẽ thử điền tất cả giá trị cho ô trống đầu tiên (depth 1),
    rồi mới chuyển sang ô trống thứ 2 (depth 2), v.v.
    ⚠️ Tốn bộ nhớ! Chỉ nên dùng cho puzzle ÍT ô trống.

    Complexity:
    ───────────
    - Time:  O(b^d)  — b = branching factor, d = depth of solution
    - Space: O(b^d)  — phải lưu toàn bộ frontier

    Args:
        problem: Đối tượng Problem (SudokuProblem)

    Returns:
        SearchResult chứa kết quả tìm kiếm
    """
    # Tạo node gốc từ trạng thái ban đầu
    root = problem.make_node(problem.initial_state())

    # Kiểm tra đích ngay tại node gốc (early goal test)
    if problem.goal_test(root.state):
        return SearchResult("BFS", root, 0, 1)

    # Frontier: Queue (FIFO) - dùng deque cho hiệu năng O(1) ở cả 2 đầu
    frontier = deque([root])

    # Tập hợp các state đang nằm trong frontier (để tra cứu O(1))
    frontier_states = {root.state}

    # Explored: tập các state đã được mở rộng (expanded)
    explored = set()

    # Thống kê
    nodes_expanded = 0
    max_frontier_size = 1

    while frontier:
        # Lấy node ở đầu queue ra (FIFO)
        node = frontier.popleft()
        frontier_states.discard(node.state)

        # Đánh dấu đã duyệt
        explored.add(node.state)
        nodes_expanded += 1

        # Mở rộng node: sinh ra tất cả các node con
        for child in problem.expand(node):
            # Chỉ xét nếu chưa duyệt VÀ chưa nằm trong frontier
            if child.state not in explored and child.state not in frontier_states:
                # Early goal test: kiểm tra NGAY KHI SINH RA (không đợi lấy ra)
                if problem.goal_test(child.state):
                    return SearchResult("BFS", child, nodes_expanded,
                                        max_frontier_size)
                # Thêm vào cuối queue
                frontier.append(child)
                frontier_states.add(child.state)

        max_frontier_size = max(max_frontier_size, len(frontier))

    # Frontier rỗng mà chưa tìm thấy → không có lời giải
    return SearchResult("BFS", None, nodes_expanded, max_frontier_size)


# =============================================================================
# 2. DEPTH-FIRST SEARCH (DFS) - Tìm kiếm theo chiều sâu
# =============================================================================
def dfs(problem: Problem, depth_limit: int = -1) -> SearchResult:
    """
    Depth-First Search (DFS) - Tìm kiếm theo chiều sâu.

    ╔════════════════════════════════════════════════════════════╗
    ║  Cấu trúc dữ liệu Frontier: STACK (LIFO - ngăn xếp)    ║
    ║  Chiến lược: Mở rộng node SÂU NHẤT trước                ║
    ║  KHÔNG đảm bảo tìm lời giải tối ưu                      ║
    ║  Ưu điểm: tiết kiệm bộ nhớ O(b·m)                      ║
    ╚════════════════════════════════════════════════════════════╝

    Logic cốt lõi:
    ─────────────
    1. Khởi tạo frontier = Stack chứa node gốc
    2. Khởi tạo explored = Set rỗng
    3. Lặp:
       a. Nếu frontier rỗng → thất bại
       b. Pop node trên cùng của stack
       c. Nếu goal_test(node.state) → trả về node
       d. Thêm node.state vào explored
       e. Với mỗi child (theo thứ tự ngược để duyệt đúng thứ tự):
          - Nếu child.state chưa ở explored → push

    Tại sao dùng Stack (LIFO)?
    ──────────────────────────
    Stack đảm bảo luôn mở rộng nhánh sâu nhất trước.
    Khi gặp ngõ cụt (ô trống không có giá trị hợp lệ), tự động backtrack.

    Với Sudoku:
    ───────────
    DFS rất phù hợp! Đi sâu điền từng ô, gặp xung đột thì quay lui.
    Bản chất giống Backtracking nhưng trên Graph Search.

    Complexity:
    ───────────
    - Time:  O(b^m)  — m = max depth (= số ô trống)
    - Space: O(b·m)  — chỉ lưu đường đi hiện tại

    Args:
        problem:     Đối tượng Problem (SudokuProblem)
        depth_limit: Giới hạn độ sâu tối đa (-1 = không giới hạn)

    Returns:
        SearchResult chứa kết quả tìm kiếm
    """
    root = problem.make_node(problem.initial_state())

    # Frontier: Stack (LIFO) - dùng list, append/pop ở cuối → O(1)
    frontier = [root]

    # Explored: tập các state đã duyệt
    explored = set()

    # Thống kê
    nodes_expanded = 0
    max_frontier_size = 1
    algo_name = f"DFS (depth≤{depth_limit})" if depth_limit != -1 else "DFS"

    while frontier:
        # Pop node trên cùng stack (LIFO)
        node = frontier.pop()

        # Late goal test: kiểm tra KHI LẤY RA khỏi frontier
        if problem.goal_test(node.state):
            return SearchResult(algo_name, node, nodes_expanded, max_frontier_size)

        # Kiểm tra giới hạn độ sâu
        if depth_limit != -1 and node.depth >= depth_limit:
            continue

        # Đánh dấu đã duyệt
        explored.add(node.state)
        nodes_expanded += 1

        # Mở rộng node - đảo ngược thứ tự để duyệt theo thứ tự đúng
        children = problem.expand(node)
        for child in reversed(children):
            if child.state not in explored:
                frontier.append(child)

        max_frontier_size = max(max_frontier_size, len(frontier))

    return SearchResult(algo_name, None, nodes_expanded, max_frontier_size)


# =============================================================================
# Depth-Limited Search (DLS) - Hàm phụ trợ cho IDS
# =============================================================================
class DLSResult:
    """
    Kết quả của Depth-Limited Search, phân biệt:
    - SOLUTION: tìm thấy lời giải
    - CUTOFF:   bị cắt do giới hạn depth (có thể có lời giải ở sâu hơn)
    - FAILURE:  đã duyệt hết, không có lời giải
    """
    SOLUTION = "solution"
    FAILURE = "failure"
    CUTOFF = "cutoff"

    def __init__(self, status: str, node: Optional[Node] = None,
                 nodes_expanded: int = 0, max_frontier_size: int = 0):
        self.status = status
        self.node = node
        self.nodes_expanded = nodes_expanded
        self.max_frontier_size = max_frontier_size


def depth_limited_search(problem: Problem, limit: int) -> DLSResult:
    """
    Depth-Limited Search (DLS) - DFS có giới hạn độ sâu.

    Giống DFS nhưng dừng mở rộng khi đạt depth = limit.
    Trả về CUTOFF nếu bị cắt (có thể có lời giải ở sâu hơn),
    FAILURE nếu đã duyệt hết mà không tìm thấy.

    Triển khai bằng đệ quy để dễ theo dõi logic.
    """
    root = problem.make_node(problem.initial_state())
    stats = {"expanded": 0, "max_frontier": 1}

    def recursive_dls(node: Node, limit: int) -> DLSResult:
        if problem.goal_test(node.state):
            return DLSResult(DLSResult.SOLUTION, node,
                             stats["expanded"], stats["max_frontier"])

        if limit == 0:
            return DLSResult(DLSResult.CUTOFF, nodes_expanded=stats["expanded"],
                             max_frontier_size=stats["max_frontier"])

        stats["expanded"] += 1
        cutoff_occurred = False

        children = problem.expand(node)
        stats["max_frontier"] = max(stats["max_frontier"], len(children))

        for child in children:
            result = recursive_dls(child, limit - 1)
            if result.status == DLSResult.CUTOFF:
                cutoff_occurred = True
            elif result.status == DLSResult.SOLUTION:
                return result

        if cutoff_occurred:
            return DLSResult(DLSResult.CUTOFF, nodes_expanded=stats["expanded"],
                             max_frontier_size=stats["max_frontier"])
        return DLSResult(DLSResult.FAILURE, nodes_expanded=stats["expanded"],
                         max_frontier_size=stats["max_frontier"])

    return recursive_dls(root, limit)


# =============================================================================
# 3. ITERATIVE DEEPENING SEARCH (IDS) - Tìm kiếm sâu dần
# =============================================================================
def ids(problem: Problem, max_depth: int = 81) -> SearchResult:
    """
    Iterative Deepening Search (IDS) - Tìm kiếm sâu dần.

    ╔════════════════════════════════════════════════════════════╗
    ║  Kết hợp ưu điểm của BFS (tối ưu) và DFS (tiết kiệm    ║
    ║  bộ nhớ).                                                 ║
    ║  Chiến lược: Chạy DFS lặp lại với depth limit tăng dần  ║
    ║  Frontier: STACK (LIFO) - giống DFS ở mỗi vòng lặp     ║
    ╚════════════════════════════════════════════════════════════╝

    Logic cốt lõi:
    ─────────────
    1. Với depth_limit = 0, 1, 2, 3, ..., max_depth:
       a. Chạy Depth-Limited Search với limit hiện tại
       b. Nếu tìm thấy lời giải → trả về
       c. Nếu bị CUTOFF → tăng limit và thử lại
       d. Nếu FAILURE (đã duyệt hết) → dừng

    Tại sao IDS không lãng phí dù phải lặp lại?
    ─────────────────────────────────────────────
    Với branching factor b, overhead chỉ ~11% khi b=10.
    Nhưng bộ nhớ chỉ cần O(b·d) thay vì O(b^d) của BFS!

    Với Sudoku:
    ───────────
    max_depth mặc định = 81 (tối đa 81 ô cần điền).
    Trong thực tế sẽ tìm thấy sớm hơn nhiều.

    Complexity:
    ───────────
    - Time:  O(b^d)  — tương đương BFS
    - Space: O(b·d)  — tương đương DFS

    Args:
        problem:   Đối tượng Problem (SudokuProblem)
        max_depth: Độ sâu tối đa cho phép

    Returns:
        SearchResult chứa kết quả tìm kiếm
    """
    total_expanded = 0
    overall_max_frontier = 0

    for depth in range(max_depth + 1):
        result = depth_limited_search(problem, depth)
        total_expanded += result.nodes_expanded
        overall_max_frontier = max(overall_max_frontier, result.max_frontier_size)

        if result.status == DLSResult.SOLUTION:
            return SearchResult("IDS", result.node,
                                total_expanded, overall_max_frontier)
        elif result.status == DLSResult.FAILURE:
            # Đã duyệt hết toàn bộ không gian, không cần tăng depth
            break

    return SearchResult("IDS", None, total_expanded, overall_max_frontier)
