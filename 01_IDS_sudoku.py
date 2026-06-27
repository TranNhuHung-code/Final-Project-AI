# -*- coding: utf-8 -*-
"""
01_IDS_sudoku.py
================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: UNINFORMED SEARCH (Tìm kiếm mù / không thông tin)
Thuật toán trình bày: Iterative Deepening Search (IDS)
Bài toán áp dụng: Giải Sudoku 9x9

----------------------------------------------------------------------
MÔ TẢ BÀI TOÁN (PEAS):
    - Performance measure: Giải đúng toàn bộ bảng Sudoku (không vi phạm
      luật ở bất kỳ hàng/cột/khung 3x3 nào), số bước duyệt (node mở rộng)
      càng ít càng tốt.
    - Environment: Bảng Sudoku 9x9 với một số ô đã có giá trị (đề bài),
      các ô còn lại cần được điền số 1-9 sao cho hợp lệ.
    - Actuators: Hành động điền một số (1-9) vào một ô trống.
    - Sensors: Quan sát được toàn bộ trạng thái hiện tại của bảng (đây là
      bài toán fully-observable, deterministic, single-agent, static).

    - Trạng thái bắt đầu (Initial state): bảng Sudoku với các ô gợi ý đã
      cho và phần còn lại trống (giá trị 0).
    - Trạng thái mục tiêu (Goal state): bảng đã điền đầy đủ 81 ô, không
      vi phạm luật Sudoku ở bất kỳ hàng/cột/khung 3x3 nào.
    - Các bước để tìm ra Solution: xem chi tiết trong file ids_solver.py
      (hàm IDSSolver.solve), được trực quan hóa từng bước trong giao
      diện Tkinter dưới đây.

CÁCH CHẠY:
    python 01_IDS_sudoku.py

YÊU CẦU: Python 3.x có sẵn thư viện tkinter (mặc định có sẵn trên
Windows/macOS; trên Ubuntu/Debian cần: sudo apt install python3-tk)
----------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import messagebox
import time
import threading

from sudoku_utils import generate_puzzle, SIZE, BOX
from ids_solver import IDSSolver


# ===================== CẤU HÌNH MÀU SẮC & GIAO DIỆN =====================
COLOR_BG = "#1f2933"
COLOR_GRID_BG = "#ffffff"
COLOR_CLUE_TEXT = "#1f2933"        # Số đề bài cho sẵn (cố định)
COLOR_CLUE_BG = "#e4e7eb"
COLOR_EMPTY_BG = "#ffffff"
COLOR_TRY_BG = "#fff3b0"           # Ô đang thử một giá trị
COLOR_TRY_TEXT = "#946800"
COLOR_BACKTRACK_BG = "#ffd6d6"     # Ô vừa bị quay lui (backtrack)
COLOR_BACKTRACK_TEXT = "#b3261e"
COLOR_SOLVED_BG = "#d6f5d6"        # Ô đã điền đúng trong lời giải cuối cùng
COLOR_SOLVED_TEXT = "#1b5e20"
COLOR_NEW_ITER_FLASH = "#cfe8ff"

FONT_CELL = ("Segoe UI", 18, "bold")
FONT_LABEL = ("Segoe UI", 12)
FONT_TITLE = ("Segoe UI", 16, "bold")


class IDSVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IDS - Iterative Deepening Search giải Sudoku 9x9")
        self.root.configure(bg=COLOR_BG)

        # ---- Sinh đề bài ----
        # num_clues=42 (39 ô trống) được chọn để thuật toán IDS chạy ra kết
        # quả trong thời gian hợp lý cho mục đích DEMO TRỰC QUAN. Vì IDS có
        # độ phức tạp ~O(9^d), Sudoku chuẩn (~30 clue) sẽ mất rất nhiều thời
        # gian nếu chạy thuần IDS không có heuristic hỗ trợ.
        self.puzzle, self.real_solution = generate_puzzle(num_clues=42, seed=None)
        self.solver = IDSSolver(self.puzzle)

        self.steps = []
        self.stats = {}
        self.solution_board = None
        self.is_solving = False
        self.is_playing = False
        self.current_step_index = -1
        self.play_speed_ms = 40  # tốc độ phát lại (ms / bước), điều chỉnh được

        self._build_ui()
        self._render_board(self.puzzle)

    # ------------------------------------------------------------------
    # XÂY DỰNG GIAO DIỆN
    # ------------------------------------------------------------------
    def _build_ui(self):
        title = tk.Label(self.root, text="IDS — Iterative Deepening Search | Sudoku 9x9",
                          font=FONT_TITLE, bg=COLOR_BG, fg="white")
        title.pack(pady=(12, 4))

        subtitle = tk.Label(
            self.root,
            text="Nhóm: Uninformed Search   |   Đồ án cuối kỳ môn Trí Tuệ Nhân Tạo",
            font=FONT_LABEL, bg=COLOR_BG, fg="#cbd2d9"
        )
        subtitle.pack(pady=(0, 10))

        # --- Khung lưới Sudoku ---
        grid_frame = tk.Frame(self.root, bg="#000000", bd=2)
        grid_frame.pack(padx=12, pady=8)

        self.cell_labels = [[None] * SIZE for _ in range(SIZE)]
        for r in range(SIZE):
            for c in range(SIZE):
                # Viền dày hơn quanh từng khung 3x3 để dễ nhìn
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

        # --- Khung điều khiển ---
        control_frame = tk.Frame(self.root, bg=COLOR_BG)
        control_frame.pack(pady=10)

        self.btn_solve = tk.Button(control_frame, text="▶ Giải bằng IDS (chạy ngầm)",
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

        # --- Thanh tốc độ ---
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

        # --- Khung thông tin trạng thái ---
        self.info_label = tk.Label(self.root, text="Nhấn 'Giải bằng IDS' để bắt đầu.",
                                    font=FONT_LABEL, bg=COLOR_BG, fg="#f3f4f6",
                                    justify="left")
        self.info_label.pack(pady=(4, 12))

    def _on_speed_change(self, value):
        self.play_speed_ms = int(value)

    # ------------------------------------------------------------------
    # VẼ BẢNG SUDOKU
    # ------------------------------------------------------------------
    def _render_board(self, board, highlight=None):
        """
        Vẽ lại toàn bộ bảng.
        highlight: tuple (row, col, action_type) để tô màu ô vừa thao tác.
            action_type in {'try', 'backtrack', None}
        """
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
    # XỬ LÝ SỰ KIỆN NÚT BẤM
    # ------------------------------------------------------------------
    def on_solve_click(self):
        """Chạy thuật toán IDS ở một thread riêng để không treo giao diện,
        sau khi xong sẽ cho phép phát lại (replay) từng bước đã ghi nhận."""
        if self.is_solving:
            return
        self.is_solving = True
        self.btn_solve.config(state="disabled", text="⏳ Đang chạy IDS...")
        self.info_label.config(text="Đang chạy thuật toán IDS ở chế độ ngầm, vui lòng chờ...")

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
        self.btn_solve.config(state="normal", text="▶ Giải bằng IDS (chạy ngầm)")

        if self.solution_board is None:
            messagebox.showwarning("Không tìm thấy lời giải",
                                    "IDS không tìm được lời giải trong giới hạn cho phép.")
            self.info_label.config(text="Không tìm được lời giải.")
            return

        self.btn_play.config(state="normal")
        self.btn_skip.config(state="normal")
        self.current_step_index = -1

        info_text = (
            f"Đã giải xong! Tổng số node đã mở rộng: {self.stats['nodes_expanded']:,} | "
            f"Giới hạn độ sâu cuối cùng: {self.stats['final_depth_limit']} | "
            f"Thời gian chạy: {self.stats['elapsed_seconds']}s | "
            f"Số bước ghi lại để phát: {len(self.steps):,}\n"
            f"Nhấn 'Phát lại từng bước' để xem trực quan quá trình IDS duyệt/quay lui."
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
            self.info_label.config(text="Đã phát xong toàn bộ quá trình tìm kiếm IDS. "
                                         "Bảng hiển thị là lời giải cuối cùng.")
            return

        step = self.steps[self.current_step_index]

        if step.action_type == 'new_iteration':
            self._render_board(step.board)
            self.info_label.config(
                text=f"--- Bắt đầu lượt lặp mới với giới hạn độ sâu = {step.depth_limit} ---"
            )
        else:
            self._render_board(step.board, highlight=(step.row, step.col, step.action_type))
            action_desc = "thử điền" if step.action_type == 'try' else "quay lui (backtrack), xóa"
            self.info_label.config(
                text=f"Bước {self.current_step_index + 1}/{len(self.steps)} | "
                     f"Giới hạn độ sâu hiện tại: {step.depth_limit} | "
                     f"Đang {action_desc} giá trị {step.value if step.value else ''} "
                     f"tại ô (hàng {step.row + 1}, cột {step.col + 1})"
            )

        self.root.after(self.play_speed_ms, self._play_next_step)

    def on_skip_click(self):
        """Bỏ qua phần phát lại, hiển thị ngay kết quả cuối cùng."""
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
        self.puzzle, self.real_solution = generate_puzzle(num_clues=42, seed=None)
        self.solver = IDSSolver(self.puzzle)
        self.steps = []
        self.stats = {}
        self.solution_board = None
        self.current_step_index = -1
        self.btn_play.config(state="disabled")
        self.btn_skip.config(state="disabled")
        self._render_board(self.puzzle)
        self.info_label.config(text="Đã sinh đề mới. Nhấn 'Giải bằng IDS' để bắt đầu.")


def main():
    root = tk.Tk()
    app = IDSVisualizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
