"""
=============================================================================
  PROBLEM BASE - Lớp trừu tượng cho mọi bài toán tìm kiếm
=============================================================================
Mọi bài toán cụ thể (Sudoku, 8-Puzzle, N-Queens, ...) đều kế thừa từ lớp này.
Cung cấp giao diện chuẩn: initial_state, goal_test, get_successors, ...

Bao gồm:
  - Node:          Nút trong cây tìm kiếm
  - Problem:       Lớp trừu tượng cho bài toán
  - SearchResult:  Đóng gói kết quả tìm kiếm
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Tuple, Optional


# =============================================================================
# NODE - Nút trong cây tìm kiếm
# =============================================================================
@dataclass
class Node:
    """
    Đại diện cho một nút trong cây tìm kiếm (Search Tree Node).

    Attributes:
        state:   Trạng thái hiện tại (ví dụ: tuple 81 phần tử cho Sudoku)
        parent:  Nút cha (dùng để truy vết đường đi)
        action:  Hành động từ parent → state (ví dụ: 'R1C3=5')
        depth:   Độ sâu của nút trong cây tìm kiếm
        cost:    Chi phí tích lũy từ trạng thái ban đầu đến nút này g(n)
    """
    state: Any
    parent: Optional['Node'] = None
    action: Optional[str] = None
    depth: int = 0
    cost: float = 0.0

    def get_path(self) -> List['Node']:
        """Truy vết đường đi từ gốc đến nút hiện tại."""
        path = []
        node = self
        while node is not None:
            path.append(node)
            node = node.parent
        path.reverse()
        return path

    def get_actions(self) -> List[str]:
        """Trả về danh sách các hành động từ gốc đến nút hiện tại."""
        return [node.action for node in self.get_path() if node.action is not None]


# =============================================================================
# PROBLEM - Lớp trừu tượng cho bài toán tìm kiếm
# =============================================================================
class Problem(ABC):
    """
    Lớp trừu tượng (Abstract Base Class) cho mọi bài toán tìm kiếm.

    Bất kỳ bài toán nào muốn sử dụng các thuật toán tìm kiếm
    đều cần kế thừa lớp này và implement các phương thức trừu tượng.
    """

    @abstractmethod
    def initial_state(self) -> Any:
        """Trả về trạng thái ban đầu của bài toán."""
        pass

    @abstractmethod
    def goal_test(self, state: Any) -> bool:
        """Kiểm tra xem state có phải trạng thái đích hay không."""
        pass

    @abstractmethod
    def get_successors(self, state: Any) -> List[Tuple[str, Any, float]]:
        """
        Sinh ra các trạng thái kế tiếp (transition model).

        Returns:
            Danh sách các tuple (action, new_state, step_cost)
            - action:    Tên hành động (vd: 'R1C3=5')
            - new_state: Trạng thái mới sau khi thực hiện action
            - step_cost: Chi phí của bước đi này
        """
        pass

    def heuristic(self, state: Any) -> float:
        """
        Hàm heuristic h(n) - ước lượng chi phí từ state đến đích.
        Mặc định trả về 0 (tương đương không có heuristic).
        Override ở lớp con nếu cần dùng cho Informed Search.
        """
        return 0.0

    def make_node(self, state: Any, parent: Optional[Node] = None,
                  action: Optional[str] = None, step_cost: float = 0.0) -> Node:
        """Tạo một Node mới từ thông tin cho trước."""
        depth = parent.depth + 1 if parent else 0
        cost = parent.cost + step_cost if parent else 0.0
        return Node(state=state, parent=parent, action=action,
                    depth=depth, cost=cost)

    def expand(self, node: Node) -> List[Node]:
        """
        Mở rộng (expand) một node: sinh ra tất cả các node con.
        Đây là thao tác cốt lõi trong mọi thuật toán tìm kiếm.
        """
        children = []
        for action, new_state, step_cost in self.get_successors(node.state):
            child = self.make_node(new_state, parent=node,
                                   action=action, step_cost=step_cost)
            children.append(child)
        return children


# =============================================================================
# SEARCH RESULT - Đóng gói kết quả tìm kiếm
# =============================================================================
class SearchResult:
    """
    Đóng gói kết quả tìm kiếm để dễ phân tích và so sánh.

    Attributes:
        algorithm:          Tên thuật toán
        solution:           Node lời giải (None nếu không tìm thấy)
        nodes_expanded:     Số node đã mở rộng
        max_frontier_size:  Kích thước frontier tối đa
    """

    def __init__(self, algorithm: str, solution: Optional[Node],
                 nodes_expanded: int, max_frontier_size: int):
        self.algorithm = algorithm
        self.solution = solution
        self.nodes_expanded = nodes_expanded
        self.max_frontier_size = max_frontier_size

    @property
    def found(self) -> bool:
        return self.solution is not None

    @property
    def path_length(self) -> int:
        return self.solution.depth if self.solution else -1

    @property
    def path_cost(self) -> float:
        return self.solution.cost if self.solution else float('inf')

    def __str__(self) -> str:
        status = "✅ TÌM THẤY LỜI GIẢI" if self.found else "❌ KHÔNG TÌM THẤY"
        lines = [
            f"╔══════════════════════════════════════════════╗",
            f"║  Thuật toán: {self.algorithm:<32}║",
            f"║  Kết quả:   {status:<32}║",
            f"║  Số node đã mở rộng: {self.nodes_expanded:<23}║",
            f"║  Kích thước frontier tối đa: {self.max_frontier_size:<15}║",
        ]
        if self.found:
            lines.append(
                f"║  Độ dài đường đi: {self.path_length:<26}║"
            )
            lines.append(
                f"║  Chi phí đường đi: {self.path_cost:<25}║"
            )
        lines.append(f"╚══════════════════════════════════════════════╝")
        return "\n".join(lines)
