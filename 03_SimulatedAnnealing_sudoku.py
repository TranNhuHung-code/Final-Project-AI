# -*- coding: utf-8 -*-
"""
03_SimulatedAnnealing_sudoku.py
=================================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: LOCAL SEARCH (Tìm kiếm cục bộ)
Thuật toán trình bày: Simulated Annealing (Luyện kim giả lập)
Bài toán áp dụng: Giải Sudoku 9x9

----------------------------------------------------------------------
MÔ TẢ BÀI TOÁN (PEAS):
    - Performance measure: Giải đúng toàn bộ bảng Sudoku (số xung đột
      h(n) = 0), số bước lặp càng ít càng tốt.
    - Environment: Bảng Sudoku 9x9, một số ô đã có giá trị (đề bài).
    - Actuators: Hoán đổi giá trị của hai ô trống trong cùng một hàng.
    - Sensors: Quan sát toàn bộ trạng thái hiện tại (fully-observable).

    - Trạng thái bắt đầu: KHÁC với các thuật toán tìm kiếm trên cây, Local
      Search bắt đầu với một LỜI GIẢI ĐẦY ĐỦ (mỗi hàng đã chứa đủ 1-9,
      không trùng trong hàng) nhưng có thể vi phạm ràng buộc cột/khung.
    - Trạng thái mục tiêu: bảng đầy đủ, không còn xung đột nào ở cột và
      khung 3x3 (h(n) = 0).
    - Hàm đánh giá h(n): tổng số cặp số bị trùng trên các cột và khung 3x3.
    - Các bước tìm Solution: tại mỗi bước, hoán đổi ngẫu nhiên 2 ô trong
      1 hàng; nếu xung đột giảm (Δ<0) thì luôn nhận; nếu xung đột tăng
      (Δ>=0) thì vẫn có thể nhận với xác suất p = exp(-Δ/T) để thoát khỏi
      cực tiểu địa phương. Nhiệt độ T giảm dần (T = α×T) theo thời gian.
      Nếu một lượt chạy không hội tụ trước khi T nguội hết, thuật toán sẽ
      RANDOM-RESTART (khởi tạo lại trạng thái mới) tối đa một số lần nhất
      định -- đây là kỹ thuật bổ trợ rất phổ biến với Simulated Annealing
      khi áp dụng cho các bài toán CSP chặt như Sudoku.
      Chi tiết: xem file sa_solver.py (SimulatedAnnealingSolver.solve).

LƯU Ý QUAN TRỌNG (để trong báo cáo phần Đánh giá):
    Simulated Annealing là thuật toán XẤP XỈ / NGẪU NHIÊN — KHÔNG đảm bảo
    luôn tìm ra lời giải tối ưu (hoặc bất kỳ lời giải nào) như A*/IDA*.
    Với Sudoku (ràng buộc rất chặt), kể cả có random-restart, tỉ lệ hội tụ
    thực nghiệm chỉ khoảng 75% (xem phần thực nghiệm trong báo cáo).

CÁCH CHẠY:
    python 03_SimulatedAnnealing_sudoku.py

YÊU CẦU: Python 3.x có sẵn thư viện tkinter.
----------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import messagebox
import time
import threading

from sudoku_utils import SIZE, BOX, generate_puzzle
from sa_solver import SimulatedAnnealingSolver


# ===================== CẤU HÌNH MÀU SẮC (Cyberpunk Theme) =====================
BG = "#080816"              
CARD = "#141630"            
ACCENT = "#00C6FF"          
TXT = "#D7DAE8"             
TXT_D = "#646987"           
TXT_B = "#FFFFFF"           

COLOR_CLUE_TEXT = "#A0A5D0"
COLOR_CLUE_BG = "#2A2D54"
COLOR_FILLED_BG = "#1A1C38"
COLOR_BETTER_BG = "#00E473"        
COLOR_BETTER_TEXT = "#000000"
COLOR_WORSE_BG = "#FFF3B0"         
COLOR_WORSE_TEXT = "#946800"
COLOR_REJECT_BG = "#FF325A"        
COLOR_REJECT_TEXT = "#FFFFFF"
COLOR_RESTART_FLASH = "#00B9FF"
COLOR_SOLVED_BG = "#00E473"
COLOR_SOLVED_TEXT = "#000000"

FONT_CELL = ("Segoe UI", 18, "bold")
FONT_LABEL = ("Segoe UI", 12)
FONT_TITLE = ("Segoe UI", 16, "bold")


class SimulatedAnnealingVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulated Annealing - Luyện kim giả lập giải Sudoku 9x9")
        self.root.configure(bg=BG)

        self.puzzle, self.real_solution = generate_puzzle(num_clues=32, seed=None)
        self.solver = SimulatedAnnealingSolver(
            self.puzzle, T0=2.0, T_min=0.01, alpha=0.9995,
            max_steps=200000, max_restarts=8
        )

        self.steps = []
        self.stats = {}
        self.solution_board = None
        self.is_solving = False
        self.is_playing = False
        self.current_step_index = -1
        self.play_speed_ms = 15  # SA có rất nhiều bước nên cần tốc độ mặc định nhanh

        self._build_ui()
        self._render_board(self.puzzle)

    # ------------------------------------------------------------------
    def _build_ui(self):
        title = tk.Label(self.root, text="Simulated Annealing | Sudoku 9x9",
                          font=FONT_TITLE, bg=BG, fg=ACCENT)
        title.pack(pady=(12, 4))

        subtitle = tk.Label(
            self.root,
            text="Nhóm 3: Local Search   |   Đồ án cuối kỳ môn Trí Tuệ Nhân Tạo",
            font=FONT_LABEL, bg=BG, fg=TXT_D
        )
        subtitle.pack(pady=(0, 10))

        grid_frame = tk.Frame(self.root, bg="#2A2D54", bd=2)
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
                    font=FONT_CELL, bg=COLOR_FILLED_BG, fg=COLOR_CLUE_TEXT,
                    relief="flat", borderwidth=0
                )
                cell.grid(row=r, column=c,
                          padx=(pad_left, pad_right), pady=(pad_top, pad_bottom),
                          sticky="nsew")
                self.cell_labels[r][c] = cell

        control_frame = tk.Frame(self.root, bg=CARD, highlightbackground=ACCENT, highlightthickness=1)
        control_frame.pack(pady=10)

        self.btn_solve = tk.Button(control_frame, text="▶ Giải bằng Simulated Annealing",
                                    command=self.on_solve_click,
                                    font=FONT_LABEL, bg="#0066FF", fg=TXT_B,
                                    activebackground="#0052CC", relief="flat", padx=10, pady=6)
        self.btn_solve.grid(row=0, column=0, padx=6, pady=6)

        self.btn_play = tk.Button(control_frame, text="⏵ Phát lại từng bước",
                                   command=self.on_play_click, state="disabled",
                                   font=FONT_LABEL, bg="#00E473", fg="black",
                                   activebackground="#00C463", relief="flat", padx=10, pady=6)
        self.btn_play.grid(row=0, column=1, padx=6)

        self.btn_skip = tk.Button(control_frame, text="⏭ Bỏ qua",
                                   command=self.on_skip_click, state="disabled",
                                   font=FONT_LABEL, bg=TXT_D, fg=TXT_B,
                                   activebackground="#4B5563", relief="flat", padx=10, pady=6)
        self.btn_skip.grid(row=0, column=2, padx=6)

        self.btn_new = tk.Button(control_frame, text="↻ Đề mới",
                                  command=self.on_new_puzzle_click,
                                  font=FONT_LABEL, bg="#FF325A", fg=TXT_B,
                                  activebackground="#CC2848", relief="flat", padx=10, pady=6)
        self.btn_new.grid(row=0, column=3, padx=6)

        speed_frame = tk.Frame(self.root, bg=BG)
        speed_frame.pack(pady=(0, 6))
        tk.Label(speed_frame, text="Tốc độ phát lại:", font=FONT_LABEL,
                 bg=BG, fg=TXT_B).pack(side="left", padx=(0, 8))
        self.speed_scale = tk.Scale(speed_frame, from_=1, to=200, orient="horizontal",
                                     length=220, bg=BG, fg=TXT_B,
                                     troughcolor=CARD, highlightthickness=0,
                                     command=self._on_speed_change)
        self.speed_scale.set(self.play_speed_ms)
        self.speed_scale.pack(side="left")

        # --- Thanh nhiệt độ T (đặc trưng riêng của Simulated Annealing) ---
        temp_frame = tk.Frame(self.root, bg=BG)
        temp_frame.pack(pady=(0, 6))
        tk.Label(temp_frame, text="Nhiệt độ T hiện tại:", font=FONT_LABEL,
                 bg=BG, fg=TXT_B).pack(side="left", padx=(0, 8))
        self.temp_canvas = tk.Canvas(temp_frame, width=220, height=18, bg=CARD,
                                      highlightthickness=0)
        self.temp_canvas.pack(side="left")
        self.temp_bar = self.temp_canvas.create_rectangle(0, 0, 220, 18, fill=ACCENT, width=0)
        self.temp_value_label = tk.Label(temp_frame, text="T0", font=FONT_LABEL,
                                          bg=BG, fg=ACCENT)
        self.temp_value_label.pack(side="left", padx=(8, 0))

        self.info_label = tk.Label(self.root, text="Nhấn 'Giải bằng Simulated Annealing' để bắt đầu.",
                                    font=FONT_LABEL, bg=BG, fg=TXT_B,
                                    justify="left")
        self.info_label.pack(pady=(4, 12))

    def _on_speed_change(self, value):
        self.play_speed_ms = int(value)

    def _update_temp_bar(self, T):
        ratio = max(0.0, min(1.0, T / self.solver.T0))
        width = int(220 * ratio)
        self.temp_canvas.coords(self.temp_bar, 0, 0, width, 18)
        self.temp_value_label.config(text=f"T = {T:.4f}")

    # ------------------------------------------------------------------
    def _render_board(self, board, highlight_cells=None, highlight_type=None):
        """
        highlight_cells: list các (row, col) cần tô màu đặc biệt.
        highlight_type: 'accept_better' | 'accept_worse' | 'reject' | 'restart'
        """
        for r in range(SIZE):
            for c in range(SIZE):
                val = board[r][c]
                label = self.cell_labels[r][c]
                is_original_clue = self.puzzle[r][c] != 0

                label.config(text=str(val) if val != 0 else "")

                if highlight_cells and (r, c) in highlight_cells:
                    if highlight_type == 'accept_better':
                        label.config(bg=COLOR_BETTER_BG, fg=COLOR_BETTER_TEXT)
                    elif highlight_type == 'accept_worse':
                        label.config(bg=COLOR_WORSE_BG, fg=COLOR_WORSE_TEXT)
                    elif highlight_type == 'reject':
                        label.config(bg=COLOR_REJECT_BG, fg=COLOR_REJECT_TEXT)
                    elif highlight_type == 'restart':
                        label.config(bg=COLOR_RESTART_FLASH, fg=COLOR_CLUE_TEXT)
                    continue

                if is_original_clue:
                    label.config(bg=COLOR_CLUE_BG, fg=COLOR_CLUE_TEXT)
                else:
                    label.config(bg=COLOR_FILLED_BG, fg=COLOR_CLUE_TEXT)

    def _mark_final_solved(self, board):
        for r in range(SIZE):
            for c in range(SIZE):
                label = self.cell_labels[r][c]
                label.config(text=str(board[r][c]))
                if self.puzzle[r][c] != 0:
                    label.config(bg=COLOR_CLUE_BG, fg=COLOR_CLUE_TEXT)
                else:
                    label.config(bg=COLOR_SOLVED_BG, fg=COLOR_SOLVED_TEXT)

    # ------------------------------------------------------------------
    def on_solve_click(self):
        if self.is_solving:
            return
        self.is_solving = True
        self.btn_solve.config(state="disabled", text="⏳ Đang chạy Simulated Annealing...")
        self.info_label.config(text="Đang chạy thuật toán Simulated Annealing ở chế độ ngầm, vui lòng chờ...")

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
        self.btn_solve.config(state="normal", text="▶ Giải bằng Simulated Annealing")

        if self.solution_board is None:
            messagebox.showinfo(
                "Chưa hội tụ",
                "Simulated Annealing là thuật toán xấp xỉ/ngẫu nhiên: không đảm bảo "
                "luôn tìm ra lời giải. Lần chạy này chưa hội tụ về 0 xung đột dù đã "
                f"thử lại {self.stats.get('restarts', 0)} lần. Hãy nhấn 'Đề mới' hoặc "
                "thử lại."
            )
            self.btn_play.config(state="normal" if self.steps else "disabled")
            self.btn_skip.config(state="normal" if self.steps else "disabled")
            self.info_label.config(
                text=f"Chưa hội tụ. Số xung đột còn lại: {self.stats.get('final_h', '?')} | "
                     f"Đã random-restart: {self.stats.get('restarts', 0)} lần."
            )
            self.current_step_index = -1
            return

        self.btn_play.config(state="normal")
        self.btn_skip.config(state="normal")
        self.current_step_index = -1

        info_text = (
            f"Đã giải xong! Tổng số bước thử: {self.stats['steps']:,} | "
            f"Số lần random-restart: {self.stats['restarts']} | "
            f"Thời gian chạy: {self.stats['elapsed_seconds']}s | "
            f"Số bước ghi lại để phát: {len(self.steps):,}\n"
            f"Nhấn 'Phát lại từng bước' để xem trực quan quá trình tối ưu."
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
            if self.solution_board:
                self._mark_final_solved(self.solution_board)
                self.info_label.config(text="Đã phát xong toàn bộ quá trình Simulated Annealing. "
                                             "Bảng hiển thị là lời giải cuối cùng.")
            else:
                self.info_label.config(text="Đã phát xong các bước đã ghi lại (chưa hội tụ về lời giải hoàn chỉnh).")
            return

        step = self.steps[self.current_step_index]

        if step.action_type == 'restart':
            self._render_board(step.board)
            self.info_label.config(text="--- RANDOM-RESTART: chưa hội tụ trước khi nguội, khởi tạo lại trạng thái mới ---")
            self._update_temp_bar(self.solver.T0)
        else:
            cells = [(step.row, step.col1), (step.row, step.col2)]
            self._render_board(step.board, highlight_cells=cells, highlight_type=step.action_type)
            self._update_temp_bar(step.temperature)

            action_desc = {
                'accept_better': "CHẤP NHẬN (lân cận TỐT HƠN, Δ<0)",
                'accept_worse': "CHẤP NHẬN (lân cận TỆ HƠN nhưng vẫn nhận theo xác suất p=exp(-Δ/T))",
                'reject': "TỪ CHỐI (lân cận tệ hơn, không thỏa xác suất)",
            }.get(step.action_type, step.action_type)

            self.info_label.config(
                text=f"Bước {self.current_step_index + 1}/{len(self.steps)} | "
                     f"Hoán đổi ô (hàng {step.row + 1}, cột {step.col1 + 1}) ↔ "
                     f"(hàng {step.row + 1}, cột {step.col2 + 1}) | "
                     f"Số xung đột h(n) = {step.h_value} | {action_desc}"
            )

        self.root.after(self.play_speed_ms, self._play_next_step)

    def on_skip_click(self):
        self.is_playing = False
        self.current_step_index = len(self.steps)
        if self.solution_board:
            self._mark_final_solved(self.solution_board)
            self.info_label.config(text="Đã hiển thị kết quả cuối cùng (bỏ qua phát lại từng bước).")
        else:
            self.info_label.config(text="Chưa có lời giải hoàn chỉnh để hiển thị (thuật toán chưa hội tụ).")
        self.btn_play.config(state="normal")
        self.btn_solve.config(state="normal")

    def on_new_puzzle_click(self):
        if self.is_solving or self.is_playing:
            return
        self.puzzle, self.real_solution = generate_puzzle(num_clues=32, seed=None)
        self.solver = SimulatedAnnealingSolver(
            self.puzzle, T0=2.0, T_min=0.01, alpha=0.9995,
            max_steps=200000, max_restarts=8
        )
        self.steps = []
        self.stats = {}
        self.solution_board = None
        self.current_step_index = -1
        self.btn_play.config(state="disabled")
        self.btn_skip.config(state="disabled")
        self._render_board(self.puzzle)
        self._update_temp_bar(self.solver.T0)
        self.info_label.config(text="Đã sinh đề mới. Nhấn 'Giải bằng Simulated Annealing' để bắt đầu.")


def main():
    root = tk.Tk()
    app = SimulatedAnnealingVisualizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
