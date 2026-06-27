# -*- coding: utf-8 -*-
"""
02_IDAstar_sudoku.py
=====================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: INFORMED SEARCH (Tìm kiếm có thông tin)
Thuật toán trình bày: IDA* (Iterative Deepening A*)
Bài toán áp dụng: Giải Sudoku 9x9

----------------------------------------------------------------------
MÔ TẢ BÀI TOÁN (PEAS):
    - Performance measure: Giải đúng toàn bộ bảng Sudoku, số node mở
      rộng càng ít càng tốt, thời gian chạy càng nhanh càng tốt.
    - Environment: Bảng Sudoku 9x9, một số ô đã có giá trị (đề bài).
    - Actuators: Hành động điền một số (1-9) vào một ô trống.
    - Sensors: Quan sát toàn bộ trạng thái hiện tại (fully-observable).

    - Trạng thái bắt đầu: bảng Sudoku với các ô gợi ý đã cho.
    - Trạng thái mục tiêu: bảng đã điền đầy đủ, không vi phạm luật.
    - Hàm heuristic h(n): với mỗi ô trống, tính số lựa chọn hợp lệ còn
      lại (kích thước domain). Ô có domain nhỏ "đóng góp" giá trị
      heuristic lớn hơn -> thuật toán ưu tiên xử lý các ô bị ràng buộc
      chặt trước (tương tự chiến lược Minimum Remaining Values - MRV
      trong CSP), giúp phát hiện nhánh sai (dead-end) sớm hơn rất nhiều
      so với duyệt mù (so sánh trực tiếp với IDS ở nhóm Uninformed Search).
    - f(n) = g(n) + h(n). IDA* tăng dần "ngưỡng f" (f-limit) qua từng
      vòng lặp thay vì tăng độ sâu như IDS thuần.
    - Chi tiết từng bước: xem file idastar_solver.py (IDAStarSolver.solve),
      được trực quan hóa trong giao diện Tkinter dưới đây.

CÁCH CHẠY:
    python 02_IDAstar_sudoku.py

YÊU CẦU: Python 3.x có sẵn thư viện tkinter.
----------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import messagebox
import time
import threading

from sudoku_utils import generate_puzzle, SIZE, BOX
from idastar_solver import IDAStarSolver


# ===================== CẤU HÌNH MÀU SẮC & GIAO DIỆN =====================
COLOR_BG = "#1f2933"
COLOR_CLUE_TEXT = "#1f2933"
COLOR_CLUE_BG = "#e4e7eb"
COLOR_EMPTY_BG = "#ffffff"
COLOR_TRY_BG = "#cfe8ff"           # Ô đang thử một giá trị (xanh dương nhạt cho IDA*)
COLOR_TRY_TEXT = "#1d4ed8"
COLOR_BACKTRACK_BG = "#ffd6d6"     # Ô vừa bị quay lui / cắt nhánh
COLOR_BACKTRACK_TEXT = "#b3261e"
COLOR_SOLVED_BG = "#d6f5d6"
COLOR_SOLVED_TEXT = "#1b5e20"
COLOR_NEW_ITER_FLASH = "#fde68a"

FONT_CELL = ("Segoe UI", 18, "bold")
FONT_LABEL = ("Segoe UI", 12)
FONT_TITLE = ("Segoe UI", 16, "bold")


class IDAStarVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IDA* - Iterative Deepening A* giải Sudoku 9x9")
        self.root.configure(bg=COLOR_BG)

        # num_clues=32 mô phỏng độ khó GẦN với Sudoku chuẩn thực tế (báo,
        # tạp chí thường dùng 28-36 clue). Nhờ heuristic MRV, IDA* xử lý
        # được mức độ khó này trong thời gian hợp lý cho mục đích DEMO,
        # khác biệt rõ rệt so với IDS thuần ở nhóm Uninformed Search.
        self.puzzle, self.real_solution = generate_puzzle(num_clues=32, seed=None)
        self.solver = IDAStarSolver(self.puzzle)

        self.steps = []
        self.stats = {}
        self.solution_board = None
        self.is_solving = False
        self.is_playing = False
        self.current_step_index = -1
        self.play_speed_ms = 40

        self._build_ui()
        self._render_board(self.puzzle)

    # ------------------------------------------------------------------
    def _build_ui(self):
        title = tk.Label(self.root, text="IDA* — Iterative Deepening A* | Sudoku 9x9",
                          font=FONT_TITLE, bg=COLOR_BG, fg="white")
        title.pack(pady=(12, 4))

        subtitle = tk.Label(
            self.root,
            text="Nhóm: Informed Search   |   Đồ án cuối kỳ môn Trí Tuệ Nhân Tạo",
            font=FONT_LABEL, bg=COLOR_BG, fg="#cbd2d9"
        )
        subtitle.pack(pady=(0, 10))

        grid_frame = tk.Frame(self.root, bg="#000000", bd=2)
        grid_frame.pack(padx=12, pady=8)

        self.cell_labels = [[None] * SIZE for _ in range(SIZE)]
        for r in range(SIZE):
            for c in range(SIZE):
                pad_top = 3 if r % BOX == 0 else 1
                pad_left = 3 if c % BOX == 0 else 1
                pad_bottom = 3 if r == SIZE - 1 else 1
                pad_right = 3 if c == SIZE - 1 else 1

                cell = tk.Label(
                    grid_frame, text="", width=3, height=1,
                    font=FONT_CELL, bg=COLOR_EMPTY_BG, fg=COLOR_CLUE_TEXT,
                    relief="flat", borderwidth=0
                )
                cell.grid(row=r, column=c,
                          padx=(pad_left, pad_right), pady=(pad_top, pad_bottom),
                          sticky="nsew")
                self.cell_labels[r][c] = cell

        control_frame = tk.Frame(self.root, bg=COLOR_BG)
        control_frame.pack(pady=10)

        self.btn_solve = tk.Button(control_frame, text="▶ Giải bằng IDA* (chạy ngầm)",
                                    command=self.on_solve_click,
                                    font=FONT_LABEL, bg="#3b82f6", fg="white",
                                    activebackground="#2563eb", relief="flat", padx=10, pady=6)
        self.btn_solve.grid(row=0, column=0, padx=6)

        self.btn_play = tk.Button(control_frame, text="⏵ Phát lại từng bước",
                                   command=self.on_play_click, state="disabled",
                                   font=FONT_LABEL, bg="#10b981", fg="white",
                                   activebackground="#059669", relief="flat", padx=10, pady=6)
        self.btn_play.grid(row=0, column=1, padx=6)

        self.btn_skip = tk.Button(control_frame, text="⏭ Nhảy đến kết quả",
                                   command=self.on_skip_click, state="disabled",
                                   font=FONT_LABEL, bg="#6b7280", fg="white",
                                   activebackground="#4b5563", relief="flat", padx=10, pady=6)
        self.btn_skip.grid(row=0, column=2, padx=6)

        self.btn_new = tk.Button(control_frame, text="↻ Đề mới",
                                  command=self.on_new_puzzle_click,
                                  font=FONT_LABEL, bg="#f59e0b", fg="white",
                                  activebackground="#d97706", relief="flat", padx=10, pady=6)
        self.btn_new.grid(row=0, column=3, padx=6)

        speed_frame = tk.Frame(self.root, bg=COLOR_BG)
        speed_frame.pack(pady=(0, 6))
        tk.Label(speed_frame, text="Tốc độ phát lại:", font=FONT_LABEL,
                 bg=COLOR_BG, fg="#cbd2d9").pack(side="left", padx=(0, 8))
        self.speed_scale = tk.Scale(speed_frame, from_=1, to=300, orient="horizontal",
                                     length=220, bg=COLOR_BG, fg="white",
                                     troughcolor="#374151", highlightthickness=0,
                                     command=self._on_speed_change)
        self.speed_scale.set(self.play_speed_ms)
        self.speed_scale.pack(side="left")

        self.info_label = tk.Label(self.root, text="Nhấn 'Giải bằng IDA*' để bắt đầu.",
                                    font=FONT_LABEL, bg=COLOR_BG, fg="#f3f4f6",
                                    justify="left")
        self.info_label.pack(pady=(4, 12))

    def _on_speed_change(self, value):
        self.play_speed_ms = int(value)

    # ------------------------------------------------------------------
    def _render_board(self, board, highlight=None):
        for r in range(SIZE):
            for c in range(SIZE):
                val = board[r][c]
                label = self.cell_labels[r][c]
                is_original_clue = self.puzzle[r][c] != 0

                text = str(val) if val != 0 else ""
                label.config(text=text)

                if highlight is not None and highlight[0] == r and highlight[1] == c:
                    action_type = highlight[2]
                    if action_type == 'try':
                        label.config(bg=COLOR_TRY_BG, fg=COLOR_TRY_TEXT)
                    elif action_type == 'backtrack':
                        label.config(bg=COLOR_BACKTRACK_BG, fg=COLOR_BACKTRACK_TEXT)
                    elif action_type == 'new_iteration':
                        label.config(bg=COLOR_NEW_ITER_FLASH, fg=COLOR_CLUE_TEXT)
                    continue

                if is_original_clue:
                    label.config(bg=COLOR_CLUE_BG, fg=COLOR_CLUE_TEXT)
                elif val != 0:
                    label.config(bg=COLOR_SOLVED_BG, fg=COLOR_SOLVED_TEXT)
                else:
                    label.config(bg=COLOR_EMPTY_BG, fg=COLOR_CLUE_TEXT)

    # ------------------------------------------------------------------
    def on_solve_click(self):
        if self.is_solving:
            return
        self.is_solving = True
        self.btn_solve.config(state="disabled", text="⏳ Đang chạy IDA*...")
        self.info_label.config(text="Đang chạy thuật toán IDA* ở chế độ ngầm, vui lòng chờ...")

        def run_solver():
            t0 = time.time()
            solution, steps, stats = self.solver.solve()
            t1 = time.time()
            stats['elapsed_seconds'] = round(t1 - t0, 4)
            self.steps = steps
            self.stats = stats
            self.solution_board = solution
            self.root.after(0, self._on_solve_finished)

        threading.Thread(target=run_solver, daemon=True).start()

    def _on_solve_finished(self):
        self.is_solving = False
        self.btn_solve.config(state="normal", text="▶ Giải bằng IDA* (chạy ngầm)")

        if self.solution_board is None:
            messagebox.showwarning("Không tìm thấy lời giải",
                                    "IDA* không tìm được lời giải trong số vòng lặp cho phép.")
            self.info_label.config(text="Không tìm được lời giải.")
            return

        self.btn_play.config(state="normal")
        self.btn_skip.config(state="normal")
        self.current_step_index = -1

        info_text = (
            f"Đã giải xong! Số node đã mở rộng: {self.stats['nodes_expanded']:,} | "
            f"Số vòng lặp tăng ngưỡng f: {self.stats['iterations']} | "
            f"Ngưỡng f cuối cùng: {self.stats['final_f_limit']} | "
            f"Thời gian chạy: {self.stats['elapsed_seconds']}s\n"
            f"Nhấn 'Phát lại từng bước' để xem trực quan quá trình IDA* duyệt/cắt nhánh."
        )
        self.info_label.config(text=info_text)

    def on_play_click(self):
        if self.is_playing or not self.steps:
            return
        self.is_playing = True
        self.btn_play.config(state="disabled")
        self.btn_solve.config(state="disabled")
        self._play_next_step()

    def _play_next_step(self):
        self.current_step_index += 1

        if self.current_step_index >= len(self.steps):
            self.is_playing = False
            self.btn_play.config(state="normal", text="⏵ Phát lại từng bước")
            self._render_board(self.solution_board)
            self.info_label.config(text="Đã phát xong toàn bộ quá trình tìm kiếm IDA*. "
                                         "Bảng hiển thị là lời giải cuối cùng.")
            return

        step = self.steps[self.current_step_index]

        if step.action_type == 'new_iteration':
            self._render_board(step.board)
            self.info_label.config(
                text=f"--- Bắt đầu vòng lặp mới với ngưỡng f-limit = {step.f_limit} ---"
            )
        else:
            self._render_board(step.board, highlight=(step.row, step.col, step.action_type))
            action_desc = "thử điền" if step.action_type == 'try' else "quay lui (backtrack), xóa"
            f_text = f"{step.f_value}" if step.f_value != float('inf') else "∞"
            self.info_label.config(
                text=f"Bước {self.current_step_index + 1}/{len(self.steps)} | "
                     f"f-limit hiện tại: {step.f_limit} | f(n) = {f_text} | "
                     f"Đang {action_desc} giá trị {step.value if step.value else ''} "
                     f"tại ô (hàng {step.row + 1}, cột {step.col + 1})"
            )

        self.root.after(self.play_speed_ms, self._play_next_step)

    def on_skip_click(self):
        self.is_playing = False
        self.current_step_index = len(self.steps)
        if self.solution_board:
            self._render_board(self.solution_board)
            self.info_label.config(text="Đã hiển thị kết quả cuối cùng (bỏ qua phát lại từng bước).")
        self.btn_play.config(state="normal")
        self.btn_solve.config(state="normal")

    def on_new_puzzle_click(self):
        if self.is_solving or self.is_playing:
            return
        self.puzzle, self.real_solution = generate_puzzle(num_clues=32, seed=None)
        self.solver = IDAStarSolver(self.puzzle)
        self.steps = []
        self.stats = {}
        self.solution_board = None
        self.current_step_index = -1
        self.btn_play.config(state="disabled")
        self.btn_skip.config(state="disabled")
        self._render_board(self.puzzle)
        self.info_label.config(text="Đã sinh đề mới. Nhấn 'Giải bằng IDA*' để bắt đầu.")


def main():
    root = tk.Tk()
    app = IDAStarVisualizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
