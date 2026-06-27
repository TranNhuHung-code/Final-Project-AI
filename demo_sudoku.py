"""
=============================================================================
  DEMO TỔNG HỢP: 18 THUẬT TOÁN TÌM KIẾM AI TRÊN BÀI TOÁN SUDOKU
=============================================================================
Chạy file này để demo tất cả 6 nhóm thuật toán:

  Cách chạy:
    cd Final-Project-AI
    python demo_sudoku.py

  Hoặc chạy từng nhóm:
    python demo_sudoku.py --group 1
    python demo_sudoku.py --group 5
=============================================================================
"""
import sys
import time
import argparse

# Thêm thư mục gốc vào path
sys.path.insert(0, '.')

from search_algorithms.core.sudoku import (
    SudokuProblem, SudokuHelper, SAMPLE_PUZZLES,
    VERY_EASY_BOARD, EASY_BOARD, MEDIUM_BOARD, HARD_BOARD, SOLUTION,
)


# =============================================================================
#  UTILITY FUNCTIONS
# =============================================================================
def print_header(title: str):
    print(f"\n{'═' * 64}")
    print(f"  {title}")
    print(f"{'═' * 64}")


def print_subheader(title: str):
    print(f"\n{'─' * 50}")
    print(f"  {title}")
    print(f"{'─' * 50}")


def print_board_comparison(title1: str, board1: tuple, title2: str, board2: tuple):
    """In 2 bảng Sudoku cạnh nhau."""
    lines1 = SudokuHelper.print_board(board1).split('\n')
    lines2 = SudokuHelper.print_board(board2).split('\n')

    print(f"  {title1:<25}  {title2}")
    for l1, l2 in zip(lines1, lines2):
        print(f"  {l1}    {l2}")


def timed_run(func, *args, **kwargs):
    """Chạy hàm và đo thời gian."""
    start = time.time()
    result = func(*args, **kwargs)
    elapsed = time.time() - start
    return result, elapsed


# =============================================================================
#  NHÓM 1: UNINFORMED SEARCH
# =============================================================================
def demo_group1():
    print_header("NHÓM 1: UNINFORMED SEARCH ALGORITHMS")
    print("  Bài toán: Sudoku 9×9 (8 ô trống — rất dễ)")
    print()

    from search_algorithms.group1_uninformed import bfs, dfs, ids

    puzzle = SudokuProblem(VERY_EASY_BOARD)
    print("  Trạng thái ban đầu:")
    print("  " + SudokuHelper.print_board(VERY_EASY_BOARD).replace("\n", "\n  "))

    # ── 1. BFS ──
    print_subheader("1. Breadth-First Search (BFS)")
    result, elapsed = timed_run(bfs, puzzle)
    print(result)
    print(f"  ⏱  Thời gian: {elapsed:.4f}s")
    if result.found:
        print("  Bảng kết quả:")
        print("  " + SudokuHelper.print_board(result.solution.state).replace("\n", "\n  "))

    # ── 2. DFS ──
    print_subheader("2. Depth-First Search (DFS)")
    result, elapsed = timed_run(dfs, puzzle)
    print(result)
    print(f"  ⏱  Thời gian: {elapsed:.4f}s")
    if result.found:
        print("  Bảng kết quả:")
        print("  " + SudokuHelper.print_board(result.solution.state).replace("\n", "\n  "))

    # ── 3. IDS ──
    print_subheader("3. Iterative Deepening Search (IDS)")
    result, elapsed = timed_run(ids, puzzle)
    print(result)
    print(f"  ⏱  Thời gian: {elapsed:.4f}s")
    if result.found:
        print("  Bảng kết quả:")
        print("  " + SudokuHelper.print_board(result.solution.state).replace("\n", "\n  "))


# =============================================================================
#  NHÓM 2: INFORMED SEARCH
# =============================================================================
def demo_group2():
    print_header("NHÓM 2: INFORMED SEARCH ALGORITHMS")
    print("  Bài toán: Sudoku 9×9 (15 ô trống — dễ)")
    print()

    from search_algorithms.group2_informed import greedy_best_first, astar, ida_star

    puzzle = SudokuProblem(EASY_BOARD)
    print("  Trạng thái ban đầu:")
    print("  " + SudokuHelper.print_board(EASY_BOARD).replace("\n", "\n  "))

    # ── 4. Greedy Best-First ──
    print_subheader("4. Greedy Best-First Search")
    result, elapsed = timed_run(greedy_best_first, puzzle)
    print(result)
    print(f"  ⏱  Thời gian: {elapsed:.4f}s")
    if result.found:
        print("  Bảng kết quả:")
        print("  " + SudokuHelper.print_board(result.solution.state).replace("\n", "\n  "))

    # ── 5. A* ──
    print_subheader("5. A* Search")
    result, elapsed = timed_run(astar, puzzle)
    print(result)
    print(f"  ⏱  Thời gian: {elapsed:.4f}s")
    if result.found:
        print("  Bảng kết quả:")
        print("  " + SudokuHelper.print_board(result.solution.state).replace("\n", "\n  "))

    # ── 6. IDA* ──
    print_subheader("6. IDA* Search")
    result, elapsed = timed_run(ida_star, puzzle)
    print(result)
    print(f"  ⏱  Thời gian: {elapsed:.4f}s")
    if result.found:
        print("  Bảng kết quả:")
        print("  " + SudokuHelper.print_board(result.solution.state).replace("\n", "\n  "))


# =============================================================================
#  NHÓM 3: LOCAL SEARCH
# =============================================================================
def demo_group3():
    print_header("NHÓM 3: LOCAL SEARCH ALGORITHMS")
    print("  Bài toán: Sudoku 9×9 (25 ô trống — trung bình)")
    print("  Phương pháp: Swap trong khối 3×3, giảm xung đột hàng/cột")
    print()

    from search_algorithms.group3_local import hill_climbing, local_beam_search, simulated_annealing

    board = MEDIUM_BOARD
    print("  Trạng thái ban đầu:")
    print("  " + SudokuHelper.print_board(board).replace("\n", "\n  "))

    # ── 7. Hill Climbing ──
    print_subheader("7. Hill Climbing (Steepest-Ascent)")
    result, elapsed = timed_run(hill_climbing, board)
    status = "✅ TÌM THẤY" if result['found'] else f"❌ Cost còn lại: {result['cost']}"
    print(f"  Kết quả: {status}")
    print(f"  Số bước: {result['steps']}, Restarts: {result['restarts']}")
    print(f"  ⏱  Thời gian: {elapsed:.4f}s")
    if result['found']:
        print("  Bảng kết quả:")
        print("  " + SudokuHelper.print_board(result['board']).replace("\n", "\n  "))

    # ── 8. Local Beam Search ──
    print_subheader("8. Local Beam Search (k=5)")
    result, elapsed = timed_run(local_beam_search, board, k=5)
    status = "✅ TÌM THẤY" if result['found'] else f"❌ Cost còn lại: {result['cost']}"
    print(f"  Kết quả: {status}")
    print(f"  Số bước: {result['steps']}")
    print(f"  ⏱  Thời gian: {elapsed:.4f}s")
    if result['found']:
        print("  Bảng kết quả:")
        print("  " + SudokuHelper.print_board(result['board']).replace("\n", "\n  "))

    # ── 9. Simulated Annealing ──
    print_subheader("9. Simulated Annealing")
    result, elapsed = timed_run(simulated_annealing, board)
    status = "✅ TÌM THẤY" if result['found'] else f"❌ Cost còn lại: {result['cost']}"
    print(f"  Kết quả: {status}")
    print(f"  Số bước: {result['steps']}")
    print(f"  Nhiệt độ cuối: {result['temperature']:.6f}")
    print(f"  ⏱  Thời gian: {elapsed:.4f}s")
    if result['found']:
        print("  Bảng kết quả:")
        print("  " + SudokuHelper.print_board(result['board']).replace("\n", "\n  "))


# =============================================================================
#  NHÓM 4: COMPLEX ENVIRONMENTS
# =============================================================================
def demo_group4():
    print_header("NHÓM 4: SEARCHING IN COMPLEX ENVIRONMENTS")
    print("  Bài toán: Sudoku 9×9 (15 ô trống — dễ)")
    print()

    from search_algorithms.group4_complex import and_or_search, sensorless_search, partial_observable_search

    board = EASY_BOARD
    print("  Trạng thái ban đầu:")
    print("  " + SudokuHelper.print_board(board).replace("\n", "\n  "))

    # ── 10. AND-OR Search ──
    print_subheader("10. AND-OR Search")
    print("  Mô hình: OR = chọn giá trị, AND = tất cả ô còn lại phải giải được")
    result, elapsed = timed_run(and_or_search, board)
    status = "✅ TÌM THẤY" if result['found'] else "❌ KHÔNG TÌM THẤY"
    print(f"  Kết quả: {status}")
    print(f"  Nodes explored: {result['nodes_explored']}")
    print(f"  ⏱  Thời gian: {elapsed:.4f}s")
    if result['found']:
        print("  Conditional Plan:")
        print(result['plan'])
        print("  Bảng kết quả:")
        print("  " + SudokuHelper.print_board(result['board']).replace("\n", "\n  "))

    # ── 11. Sensorless Search ──
    print_subheader("11. Sensorless Search (Conformant)")
    print("  Mô hình: 3 ô ban đầu 'không chắc chắn', tìm plan cho mọi khả năng")
    result, elapsed = timed_run(sensorless_search, board)
    status = "✅ TÌM THẤY" if result['found'] else "❌ KHÔNG TÌM THẤY"
    print(f"  Kết quả: {status}")
    print(f"  Uncertain cells: {result.get('uncertain_cells', [])}")
    print(f"  Nodes explored: {result['nodes_explored']}")
    print(f"  ⏱  Thời gian: {elapsed:.4f}s")
    if result['found']:
        print(f"  Plan ({len(result['plan'])} bước): {', '.join(result['plan'][:10])}...")
        print("  Bảng kết quả:")
        print("  " + SudokuHelper.print_board(result['board']).replace("\n", "\n  "))

    # ── 12. Partial Observable Search ──
    print_subheader("12. Partially Observable Search")
    print("  Mô hình: Agent chỉ quan sát được hàng/cột/khối xung quanh ô vừa điền")
    result, elapsed = timed_run(partial_observable_search, board)
    status = "✅ TÌM THẤY" if result['found'] else "❌ KHÔNG TÌM THẤY"
    print(f"  Kết quả: {status}")
    print(f"  Nodes explored: {result['nodes_explored']}")
    print(f"  Observations made: {result['observations_made']}")
    print(f"  ⏱  Thời gian: {elapsed:.4f}s")
    if result['found']:
        print(f"  Plan ({len(result['plan'])} bước): {', '.join(result['plan'][:10])}...")
        print("  Bảng kết quả:")
        print("  " + SudokuHelper.print_board(result['board']).replace("\n", "\n  "))


# =============================================================================
#  NHÓM 5: CSP
# =============================================================================
def demo_group5():
    print_header("NHÓM 5: CONSTRAINT SATISFACTION PROBLEMS (CSP)")
    print("  Bài toán: Sudoku 9×9 (45 ô trống — khó)")
    print("  Sudoku là bài toán CSP kinh điển!")
    print()

    from search_algorithms.group5_csp import backtracking_search, forward_checking, min_conflicts

    board = HARD_BOARD
    print("  Trạng thái ban đầu:")
    print("  " + SudokuHelper.print_board(board).replace("\n", "\n  "))

    # ── 13. Backtracking ──
    print_subheader("13. Backtracking Search (CSP)")
    result, elapsed = timed_run(backtracking_search, board)
    status = "✅ TÌM THẤY" if result['found'] else "❌ KHÔNG TÌM THẤY"
    print(f"  Kết quả: {status}")
    print(f"  Nodes explored: {result['nodes_explored']}")
    print(f"  Backtracks: {result['backtracks']}")
    print(f"  ⏱  Thời gian: {elapsed:.4f}s")
    if result['found']:
        print("  Bảng kết quả:")
        print("  " + SudokuHelper.print_board(result['board']).replace("\n", "\n  "))

    # ── 14. Forward Checking ──
    print_subheader("14. Forward Checking")
    result, elapsed = timed_run(forward_checking, board)
    status = "✅ TÌM THẤY" if result['found'] else "❌ KHÔNG TÌM THẤY"
    print(f"  Kết quả: {status}")
    print(f"  Nodes explored: {result['nodes_explored']}")
    print(f"  Pruned branches: {result['pruned']}")
    print(f"  ⏱  Thời gian: {elapsed:.4f}s")
    if result['found']:
        print("  Bảng kết quả:")
        print("  " + SudokuHelper.print_board(result['board']).replace("\n", "\n  "))

    # ── 15. Min-Conflicts ──
    print_subheader("15. Min-Conflicts")
    result, elapsed = timed_run(min_conflicts, board)
    status = "✅ TÌM THẤY" if result['found'] else f"❌ Xung đột còn: {result['conflicts_remaining']}"
    print(f"  Kết quả: {status}")
    print(f"  Số bước: {result['steps']}")
    print(f"  ⏱  Thời gian: {elapsed:.4f}s")
    if result['found']:
        print("  Bảng kết quả:")
        print("  " + SudokuHelper.print_board(result['board']).replace("\n", "\n  "))


# =============================================================================
#  NHÓM 6: ADVERSARIAL SEARCH
# =============================================================================
def demo_group6():
    print_header("NHÓM 6: ADVERSARIAL SEARCH")
    print("  Mô hình: Sudoku đối kháng 2 người chơi")
    print("  MAX (Filler) muốn hoàn thành, MIN (Blocker) muốn cản trở")
    print("  Bài toán: Sudoku 9×9 (8 ô trống — rất dễ)")
    print()

    from search_algorithms.group6_adversarial import minimax, alpha_beta, expectimax

    board = VERY_EASY_BOARD
    print("  Trạng thái ban đầu:")
    print("  " + SudokuHelper.print_board(board).replace("\n", "\n  "))

    # ── 16. Minimax ──
    print_subheader("16. Minimax")
    result, elapsed = timed_run(minimax, board, max_depth=4)
    status = "✅ HOÀN THÀNH" if result['found'] else "❌ KHÔNG HOÀN THÀNH"
    print(f"  Kết quả: {status}")
    print(f"  Nước đi đầu (MAX): {result['best_move']}")
    print(f"  Evaluation: {result['value']:.2f}")
    print(f"  Nodes explored: {result['nodes_explored']}")
    print(f"  ⏱  Thời gian: {elapsed:.4f}s")
    print("  Bảng kết quả:")
    print("  " + SudokuHelper.print_board(result['board']).replace("\n", "\n  "))

    # ── 17. Alpha-Beta ──
    print_subheader("17. Alpha-Beta Pruning")
    result, elapsed = timed_run(alpha_beta, board, max_depth=4)
    status = "✅ HOÀN THÀNH" if result['found'] else "❌ KHÔNG HOÀN THÀNH"
    print(f"  Kết quả: {status}")
    print(f"  Nước đi đầu (MAX): {result['best_move']}")
    print(f"  Evaluation: {result['value']:.2f}")
    print(f"  Nodes explored: {result['nodes_explored']}")
    print(f"  Pruned: {result['pruned']}")
    print(f"  ⏱  Thời gian: {elapsed:.4f}s")
    print("  Bảng kết quả:")
    print("  " + SudokuHelper.print_board(result['board']).replace("\n", "\n  "))

    # ── 18. Expectimax ──
    print_subheader("18. Expectimax")
    result, elapsed = timed_run(expectimax, board, max_depth=4)
    status = "✅ HOÀN THÀNH" if result['found'] else "❌ KHÔNG HOÀN THÀNH"
    print(f"  Kết quả: {status}")
    print(f"  Nước đi đầu (MAX): {result['best_move']}")
    print(f"  Evaluation: {result['value']:.2f}")
    print(f"  Nodes explored: {result['nodes_explored']}")
    print(f"  ⏱  Thời gian: {elapsed:.4f}s")
    print("  Bảng kết quả:")
    print("  " + SudokuHelper.print_board(result['board']).replace("\n", "\n  "))


# =============================================================================
#  MAIN
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Demo 18 thuật toán tìm kiếm AI trên Sudoku")
    parser.add_argument('--group', type=int, choices=[1, 2, 3, 4, 5, 6],
                        help="Chỉ chạy nhóm cụ thể (1-6). Mặc định: chạy tất cả.")
    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║        18 THUẬT TOÁN TÌM KIẾM AI — BÀI TOÁN SUDOKU       ║")
    print("║           Trí tuệ nhân tạo — Final Project                ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    demos = {
        1: demo_group1,
        2: demo_group2,
        3: demo_group3,
        4: demo_group4,
        5: demo_group5,
        6: demo_group6,
    }

    if args.group:
        demos[args.group]()
    else:
        for group_num, demo_func in demos.items():
            demo_func()

    print("\n" + "═" * 64)
    print("  ✅ HOÀN THÀNH DEMO TẤT CẢ 18 THUẬT TOÁN!")
    print("═" * 64)


if __name__ == "__main__":
    main()
