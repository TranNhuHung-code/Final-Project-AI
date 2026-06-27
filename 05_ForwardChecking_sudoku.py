# -*- coding: utf-8 -*-
"""
05_ForwardChecking_sudoku.py
==============================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: CSP (Constraint Satisfaction Problem)
Thuật toán trình bày: Backtracking Search + Forward Checking (+ MRV)
Bài toán áp dụng: Giải Sudoku 9x9

----------------------------------------------------------------------
MÔ TẢ BÀI TOÁN DƯỚI DẠNG CSP (PEAS):
    - Variables: mỗi ô trống là 1 biến cần gán giá trị.
    - Domain: ban đầu {1..9}, thu hẹp dần qua forward checking.
    - Constraints: ràng buộc all-different trên từng hàng / cột / khung 3x3.
    - Performance measure: giải đúng toàn bộ bảng, số node mở rộng và số
      lần quay lui (backtrack) càng ít càng tốt.

    - Trạng thái bắt đầu: các ô đề bài đã gán, các ô trống domain = {1..9}
      đã được thu hẹp lần đầu theo ràng buộc của các ô đề bài.
    - Trạng thái mục tiêu: tất cả các biến (ô trống) đã được gán giá trị
      hợp lệ, không còn biến nào chưa gán.
    - Các bước để tìm ra Solution:
        1) Chọn biến (ô trống) có domain NHỎ NHẤT để gán trước (MRV).
        2) Thử gán từng giá trị còn lại trong domain của biến đó.
        3) FORWARD CHECKING: ngay sau khi gán, loại giá trị đó khỏi domain
           của các biến láng giềng (cùng hàng/cột/khung). Nếu domain của
           một biến láng giềng nào đó trở thành RỖNG -> phát hiện thất bại
           NGAY, quay lui ngay lập tức (không cần đệ quy sâu hơn).
        4) Nếu không bị rỗng domain, đệ quy gán biến tiếp theo.
        5) Khi quay lui: khôi phục lại domain đã bị thu hẹp trước đó.
      Chi tiết: xem file forward_checking_solver.py.

CÁCH CHẠY:
    python 05_ForwardChecking_sudoku.py

YÊU CẦU: Python 3.x có sẵn thư viện tkinter.
----------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import messagebox
import time
import threading

from sudoku_utils import SIZE, BOX, generate_puzzle
from forward_checking_solver import ForwardCheckingSolver


# ===================== CẤU HÌNH MÀU SẮC & GIAO DIỆN =====================
COLOR_BG = "#1f2933"
COLOR_CLUE_TEXT = "#1f2933"
COLOR_CLUE_BG = "#e4e7eb"
COLOR_EMPTY_BG = "#ffffff"
COLOR_ASSIGN_BG = "#cfe8ff"          # Ô vừa được gán giá trị (forward checking)
COLOR_ASSIGN_TEXT = "#1d4ed8"
COLOR_BACKTRACK_BG = "#ffd6d6"       # Ô vừa bị quay lui (undo gán)
COLOR_BACKTRACK_TEXT = "#b3261e"
COLOR_WIPEOUT_BG = "#fecaca"         # Ô bị domain rỗng (forward check fail) -> highlight đậm
COLOR_WIPEOUT_TEXT = "#7f1d1d"
COLOR_SOLVED_BG = "#d6f5d6"
COLOR_SOLVED_TEXT = "#1b5e20"

FONT_CELL = ("Segoe UI", 18, "bold")
FONT_LABEL = ("Segoe UI", 12)
FONT_TITLE = ("Segoe UI", 16, "bold")


class ForwardCheckingVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Forward Checking (CSP) - giải Sudoku 9x9")
        self.root.configure(bg=COLOR_BG)

        # num_clues=26 mô phỏng Sudoku độ khó CAO (gần ngưỡng khó nhất về lý
        # thuyết, 17 clue) nhưng vẫn đủ nhanh cho demo trực quan từng bước,
        # đồng thời thể hiện rõ sức mạnh của Forward Checking + MRV so với
        # các nhóm thuật toán Uninformed/Informed Search.
        self.puzzle, self.real_solution = generate_puzzle(num_clues=26, seed=None)
        self.solver = ForwardCheckingSolver(self.puzzle)

        self.steps = []
        self.stats = {}
        self.solution_board = None
        self.is_solving = False
        self.is_playing = False
        self.current_step_index = -1
        self.play_speed_ms = 60

        self._build_ui()
        self._render_board(self.puzzle)

    # ------------------------------------------------------------------
    def _build_ui(self):
        title = tk.Label(self.root, text="Forward Checking (CSP) | Sudoku 9x9",
                          font=FONT_TITLE, bg=COLOR_BG, fg="white")
        title.pack(pady=(12, 4))

        subtitle = tk.Label(
            self.root,
            text="Nhóm: CSP   |   Đồ án cuối kỳ môn Trí Tuệ Nhân Tạo",
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

        self.btn_solve = tk.Button(control_frame, text="▶ Giải bằng Forward Checking",
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

        self.info_label = tk.Label(self.root, text="Nhấn 'Giải bằng Forward Checking' để bắt đầu.",
                                    font=FONT_LABEL, bg=COLOR_BG, fg="#f3f4f6",
                                    justify="left")
        self.info_label.pack(pady=(4, 12))

    def _on_speed_change(self, value):
        self.play_speed_ms = int(value)

    # ------------------------------------------------------------------
    def _render_board(self, board, highlight=None, wipeout_cell=None):
        """
        highlight: (row, col, action_type) - ô vừa thao tác chính
        wipeout_cell: (row, col) - ô bị domain rỗng do forward checking (nếu có)
        """
        for r in range(SIZE):
            for c in range(SIZE):
                val = board[r][c]
                label = self.cell_labels[r][c]
                is_original_clue = self.puzzle[r][c] != 0

                label.config(text=str(val) if val != 0 else "")

                if wipeout_cell is not None and wipeout_cell == (r, c):
                    label.config(bg=COLOR_WIPEOUT_BG, fg=COLOR_WIPEOUT_TEXT, text="✕")
                    continue

                if highlight is not None and highlight[0] == r and highlight[1] == c:
                    action_type = highlight[2]
                    if action_type in ('assign', 'forward_check_fail'):
                        label.config(bg=COLOR_ASSIGN_BG, fg=COLOR_ASSIGN_TEXT)
                    elif action_type == 'backtrack':
                        label.config(bg=COLOR_BACKTRACK_BG, fg=COLOR_BACKTRACK_TEXT)
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
        self.btn_solve.config(state="disabled", text="⏳ Đang chạy...")
        self.info_label.config(text="Đang chạy Backtracking + Forward Checking ở chế độ ngầm, vui lòng chờ...")

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
        self.btn_solve.config(state="normal", text="▶ Giải bằng Forward Checking")

        if self.solution_board is None:
            messagebox.showwarning("Không tìm thấy lời giải",
                                    "Không tìm được lời giải (đề bài có thể không hợp lệ).")
            self.info_label.config(text="Không tìm được lời giải.")
            return

        self.btn_play.config(state="normal")
        self.btn_skip.config(state="normal")
        self.current_step_index = -1

        info_text = (
            f"Đã giải xong! Số node đã mở rộng: {self.stats['nodes_expanded']:,} | "
            f"Số lần quay lui (backtrack): {self.stats['backtrack_count']:,} | "
            f"Thời gian chạy: {self.stats['elapsed_seconds']}s\n"
            f"Nhấn 'Phát lại từng bước' để xem trực quan quá trình gán/forward-check/quay lui."
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
            self.info_label.config(text="Đã phát xong toàn bộ quá trình Forward Checking. "
                                         "Bảng hiển thị là lời giải cuối cùng.")
            return

        step = self.steps[self.current_step_index]

        if step.action_type == 'assign':
            self._render_board(step.board, highlight=(step.row, step.col, 'assign'))
            self.info_label.config(
                text=f"Bước {self.current_step_index + 1}/{len(self.steps)} | "
                     f"GÁN giá trị {step.value} cho ô (hàng {step.row + 1}, cột {step.col + 1}) "
                     f"[biến được chọn theo MRV - domain nhỏ nhất]"
            )
        elif step.action_type == 'forward_check_fail':
            self._render_board(step.board, highlight=(step.row, step.col, 'forward_check_fail'),
                                wipeout_cell=step.domain_wipeout_cell)
            self.info_label.config(
                text=f"Bước {self.current_step_index + 1}/{len(self.steps)} | "
                     f"⚠ FORWARD CHECKING phát hiện THẤT BẠI SỚM: sau khi gán {step.value} "
                     f"tại (hàng {step.row + 1}, cột {step.col + 1}), ô (hàng "
                     f"{step.domain_wipeout_cell[0] + 1}, cột {step.domain_wipeout_cell[1] + 1}) "
                     f"bị RỖNG DOMAIN -> quay lui ngay, không cần đệ quy thêm!"
            )
        elif step.action_type == 'backtrack':
            self._render_board(step.board, highlight=(step.row, step.col, 'backtrack'))
            self.info_label.config(
                text=f"Bước {self.current_step_index + 1}/{len(self.steps)} | "
                     f"QUAY LUI (backtrack): xóa giá trị tại ô (hàng {step.row + 1}, "
                     f"cột {step.col + 1}), khôi phục domain các ô liên quan."
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
        self.puzzle, self.real_solution = generate_puzzle(num_clues=26, seed=None)
        self.solver = ForwardCheckingSolver(self.puzzle)
        self.steps = []
        self.stats = {}
        self.solution_board = None
        self.current_step_index = -1
        self.btn_play.config(state="disabled")
        self.btn_skip.config(state="disabled")
        self._render_board(self.puzzle)
        self.info_label.config(text="Đã sinh đề mới. Nhấn 'Giải bằng Forward Checking' để bắt đầu.")


def main():
    root = tk.Tk()
    app = ForwardCheckingVisualizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
