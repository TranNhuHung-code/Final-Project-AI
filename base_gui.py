# -*- coding: utf-8 -*-
"""
base_gui.py
Lớp giao diện cơ sở (Base UI) cho tất cả các thuật toán giải Sudoku.
Được thiết kế lại theo phong cách Dark/Cyberpunk của nhánh main, 
nhưng sử dụng Tkinter thay vì Pygame.
"""

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import time
import threading

from sudoku_utils import generate_puzzle, SIZE, BOX

# ===================== CẤU HÌNH MÀU SẮC (Cyberpunk Theme) =====================
BG = "#080816"              # Màu nền tối
CARD = "#141630"            # Màu thẻ / panel
CARD_H = "#1E203E"          # Màu thẻ khi hover
ACCENT = "#00C6FF"          # Màu nhấn chính (Cyan)
TXT = "#D7DAE8"             # Màu chữ thường
TXT_D = "#646987"           # Màu chữ mờ
TXT_B = "#FFFFFF"           # Màu chữ trắng sáng

# Màu trạng thái của ô
COLOR_EMPTY_BG = "#1A1C38"
COLOR_CLUE_BG = "#2A2D54"
COLOR_CLUE_TEXT = "#A0A5D0"

COLOR_TRY_BG = "#FFF3B0"    # Màu khi đang thử (vàng)
COLOR_TRY_TEXT = "#946800"
COLOR_BACKTRACK_BG = "#FF325A" # Màu quay lui (đỏ cyberpunk)
COLOR_BACKTRACK_TEXT = "#FFFFFF"

COLOR_SOLVED_BG = "#00E473"    # Màu khi điền xong (xanh lá)
COLOR_SOLVED_TEXT = "#000000"
COLOR_NEW_ITER_FLASH = "#00B9FF"

# Fonts
FONT_CELL = ("Segoe UI", 18, "bold")
FONT_LABEL = ("Segoe UI", 11)
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_LOG = ("Consolas", 10)


class BaseSudokuApp:
    def __init__(self, root, title, subtitle, algo_name, solver_class, num_clues=35):
        self.root = root
        self.root.title(title)
        self.root.configure(bg=BG)
        # Thiết lập kích thước cố định
        self.root.geometry("1100x700")

        self.title_text = title
        self.subtitle_text = subtitle
        self.algo_name = algo_name
        
        self.solver_class = solver_class
        
        self.puzzle, self.real_solution = generate_puzzle(num_clues=num_clues, seed=None)
        self.solver = self.solver_class(self.puzzle)

        self.steps = []
        self.stats = {}
        self.solution_board = None
        self.is_solving = False
        self.is_playing = False
        self.is_paused = False
        self.current_step_index = -1
        self.play_speed_ms = 40

        self._build_ui()
        self._render_board(self.puzzle)

    def _build_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg=BG)
        header_frame.pack(fill=tk.X, pady=(15, 5))
        
        lbl_title = tk.Label(header_frame, text=self.title_text, font=FONT_TITLE, bg=BG, fg=ACCENT)
        lbl_title.pack()
        
        lbl_sub = tk.Label(header_frame, text=self.subtitle_text, font=FONT_LABEL, bg=BG, fg=TXT_D)
        lbl_sub.pack()

        # Body (chia 2 cột: trái là Grid, phải là Controls + Log)
        body_frame = tk.Frame(self.root, bg=BG)
        body_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Cột trái (Grid)
        left_frame = tk.Frame(body_frame, bg=CARD, bd=0, relief="flat", highlightbackground=ACCENT, highlightthickness=1)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # Viền cho bảng Sudoku
        grid_container = tk.Frame(left_frame, bg=CARD)
        grid_container.pack(padx=15, pady=15)

        grid_frame = tk.Frame(grid_container, bg="#2A2D54", bd=2)
        grid_frame.pack()

        self.cell_labels = [[None] * SIZE for _ in range(SIZE)]
        for r in range(SIZE):
            for c in range(SIZE):
                pad_top = 3 if r % BOX == 0 else 1
                pad_left = 3 if c % BOX == 0 else 1
                pad_bottom = 3 if r == SIZE - 1 else 1
                pad_right = 3 if c == SIZE - 1 else 1

                cell = tk.Label(
                    grid_frame, text="", width=3, height=1,
                    font=FONT_CELL, bg=COLOR_EMPTY_BG, fg=TXT_B,
                    relief="flat", borderwidth=0
                )
                cell.grid(row=r, column=c,
                          padx=(pad_left, pad_right), pady=(pad_top, pad_bottom),
                          sticky="nsew")
                self.cell_labels[r][c] = cell

        # Cột phải (Controls + Logs)
        right_frame = tk.Frame(body_frame, bg=BG)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Khu vực điều khiển
        control_frame = tk.Frame(right_frame, bg=CARD, highlightbackground=ACCENT, highlightthickness=1)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        btn_style = {"font": FONT_LABEL, "relief": "flat", "padx": 10, "pady": 5, "cursor": "hand2"}

        self.btn_solve = tk.Button(control_frame, text=f"▶ Giải bằng {self.algo_name}", 
                                   command=self.on_solve_click, bg="#0066FF", fg=TXT_B, activebackground="#0052CC", **btn_style)
        self.btn_solve.grid(row=0, column=0, padx=10, pady=10)

        self.btn_play = tk.Button(control_frame, text="⏵ Phát lại", state="disabled", 
                                  command=self.on_play_click, bg="#00E473", fg="black", activebackground="#00C463", **btn_style)
        self.btn_play.grid(row=0, column=1, padx=5, pady=10)
        
        self.btn_pause = tk.Button(control_frame, text="⏸ Tạm dừng", state="disabled", 
                                   command=self.on_pause_click, bg="#FFBE00", fg="black", activebackground="#D9A200", **btn_style)
        self.btn_pause.grid(row=0, column=2, padx=5, pady=10)

        self.btn_skip = tk.Button(control_frame, text="⏭ Bỏ qua", state="disabled", 
                                  command=self.on_skip_click, bg=TXT_D, fg=TXT_B, activebackground="#4B5563", **btn_style)
        self.btn_skip.grid(row=0, column=3, padx=5, pady=10)

        self.btn_new = tk.Button(control_frame, text="↻ Đề mới", 
                                 command=self.on_new_puzzle_click, bg="#FF325A", fg=TXT_B, activebackground="#CC2848", **btn_style)
        self.btn_new.grid(row=0, column=4, padx=10, pady=10)

        # Tốc độ
        speed_frame = tk.Frame(control_frame, bg=CARD)
        speed_frame.grid(row=1, column=0, columnspan=5, pady=(0, 10), sticky="w", padx=10)
        tk.Label(speed_frame, text="Tốc độ:", font=FONT_LABEL, bg=CARD, fg=TXT_B).pack(side=tk.LEFT)
        self.speed_scale = tk.Scale(speed_frame, from_=1, to=300, orient="horizontal",
                                     length=300, bg=CARD, fg=TXT_B, troughcolor=BG, 
                                     highlightthickness=0, command=self._on_speed_change)
        self.speed_scale.set(self.play_speed_ms)
        self.speed_scale.pack(side=tk.LEFT, padx=10)

        # Khu vực trạng thái
        self.info_label = tk.Label(right_frame, text="Sẵn sàng.", font=FONT_LABEL, bg=BG, fg=ACCENT, justify="left")
        self.info_label.pack(anchor="w", pady=(0, 5))

        # Khu vực Log
        log_frame = tk.Frame(right_frame, bg=CARD, highlightbackground=ACCENT, highlightthickness=1)
        log_frame.pack(fill=tk.BOTH, expand=True)

        lbl_log = tk.Label(log_frame, text="Nhật ký chạy (Log)", font=FONT_LABEL, bg=CARD, fg=TXT_B)
        lbl_log.pack(anchor="w", padx=10, pady=5)

        self.log_text = tk.Text(log_frame, font=FONT_LOG, bg=BG, fg=TXT, state=tk.DISABLED, wrap=tk.WORD, bd=0)
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=(0, 10))

        # Định dạng màu trong Log
        self.log_text.tag_configure("info", foreground=TXT_D)
        self.log_text.tag_configure("try", foreground=COLOR_TRY_BG)
        self.log_text.tag_configure("backtrack", foreground=COLOR_BACKTRACK_BG)
        self.log_text.tag_configure("success", foreground=COLOR_SOLVED_BG)

    def _on_speed_change(self, value):
        self.play_speed_ms = int(value)

    def _log(self, message, tag="info"):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

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
                    if action_type in ('try', 'assign'):
                        label.config(bg=COLOR_TRY_BG, fg=COLOR_TRY_TEXT)
                    elif action_type == 'backtrack':
                        label.config(bg=COLOR_BACKTRACK_BG, fg=COLOR_BACKTRACK_TEXT)
                    elif action_type == 'forward_check_fail':
                        label.config(bg="#FF325A", fg="#FFFFFF", text="✕")
                    elif action_type == 'new_iteration':
                        label.config(bg=COLOR_NEW_ITER_FLASH, fg=COLOR_SOLVED_TEXT)
                    elif action_type == 'swap':
                        label.config(bg=ACCENT, fg="black")
                    continue

                if is_original_clue:
                    label.config(bg=COLOR_CLUE_BG, fg=COLOR_CLUE_TEXT)
                elif val != 0:
                    label.config(bg=COLOR_SOLVED_BG, fg=COLOR_SOLVED_TEXT)
                else:
                    label.config(bg=COLOR_EMPTY_BG, fg=TXT_B)

    def on_solve_click(self):
        if self.is_solving:
            return
        self.is_solving = True
        self._clear_log()
        self._log(f"Bắt đầu giải bằng {self.algo_name}...", "info")
        self.btn_solve.config(state="disabled", text="⏳ Đang giải...")
        self.info_label.config(text=f"Đang chạy thuật toán {self.algo_name}...")

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
        self.btn_solve.config(state="normal", text=f"▶ Giải bằng {self.algo_name}")

        if self.solution_board is None:
            self._log("Không tìm thấy lời giải.", "backtrack")
            messagebox.showwarning("Không tìm thấy lời giải", f"{self.algo_name} không tìm được lời giải.")
            self.info_label.config(text="Không tìm được lời giải.")
            return

        self.btn_play.config(state="normal")
        self.btn_skip.config(state="normal")
        self.current_step_index = -1

        nodes = self.stats.get('nodes_expanded', self.stats.get('nodes', 0))
        time_sec = self.stats.get('elapsed_seconds', 0)
        
        info_text = (
            f"Đã giải xong! Nodes: {nodes:,} | Thời gian: {time_sec}s | Số bước: {len(self.steps):,}"
        )
        self.info_label.config(text=info_text)
        self._log(f"Hoàn thành trong {time_sec}s với {nodes:,} nodes được mở rộng.", "success")

    def on_play_click(self):
        if self.is_playing:
            return
        self.is_playing = True
        self.is_paused = False
        self.btn_play.config(state="disabled")
        self.btn_pause.config(state="normal", text="⏸ Tạm dừng")
        self.btn_solve.config(state="disabled")
        self._play_next_step()

    def on_pause_click(self):
        if not self.is_playing:
            return
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.config(text="▶ Tiếp tục")
            self._log("Đã tạm dừng.", "info")
        else:
            self.btn_pause.config(text="⏸ Tạm dừng")
            self._log("Tiếp tục chạy...", "info")
            self._play_next_step()

    def _play_next_step(self):
        if self.is_paused:
            return
            
        self.current_step_index += 1

        if self.current_step_index >= len(self.steps):
            self._finish_playing()
            return

        step = self.steps[self.current_step_index]
        
        action_type = getattr(step, 'action_type', 'try')
        
        if action_type == 'new_iteration':
            self._render_board(step.board)
            self._log(f"--- Lặp mới: depth={getattr(step, 'depth_limit', '')} ---", "info")
        elif action_type == 'swap':
            self._render_board(step.board, highlight=(step.row, step.col, 'swap'))
            self._log(f"Swap tại ({step.row+1}, {step.col+1})", "try")
        elif action_type == 'info':
             self._render_board(step.board)
             self._log(f"Info: {getattr(step, 'value', '')}", "info")
        else:
            self._render_board(step.board, highlight=(step.row, step.col, action_type))
            if action_type in ('try', 'assign'):
                self._log(f"Thử {step.value} tại ({step.row+1}, {step.col+1})", "try")
            elif action_type == 'backtrack':
                self._log(f"Quay lui tại ({step.row+1}, {step.col+1})", "backtrack")
            elif action_type == 'forward_check_fail':
                self._log(f"Thất bại tại ({step.row+1}, {step.col+1}) do vi phạm domain", "backtrack")

        self.root.after(self.play_speed_ms, self._play_next_step)

    def _finish_playing(self):
        self.is_playing = False
        self.btn_play.config(state="normal", text="⏵ Phát lại")
        self.btn_pause.config(state="disabled")
        self.btn_solve.config(state="normal")
        self._render_board(self.solution_board)
        self.info_label.config(text="Đã phát xong toàn bộ quá trình tìm kiếm.")
        self._log("Kết thúc phát lại.", "success")

    def on_skip_click(self):
        self.is_playing = False
        self.is_paused = False
        self.current_step_index = len(self.steps)
        if self.solution_board:
            self._render_board(self.solution_board)
            self.info_label.config(text="Đã hiển thị kết quả cuối cùng (bỏ qua phát lại).")
            self._log("Bỏ qua đến kết quả cuối cùng.", "success")
        self.btn_play.config(state="normal", text="⏵ Phát lại")
        self.btn_pause.config(state="disabled")
        self.btn_solve.config(state="normal")

    def on_new_puzzle_click(self):
        if self.is_solving or self.is_playing:
            return
        self.puzzle, self.real_solution = generate_puzzle(num_clues=35, seed=None)
        self.solver = self.solver_class(self.puzzle)
        self.steps = []
        self.stats = {}
        self.solution_board = None
        self.current_step_index = -1
        self.btn_play.config(state="disabled")
        self.btn_pause.config(state="disabled")
        self.btn_skip.config(state="disabled")
        self._render_board(self.puzzle)
        self._clear_log()
        self.info_label.config(text="Đã sinh đề mới. Nhấn Giải để bắt đầu.")
        self._log("Đã tạo đề mới.", "info")

class SearchStep:
    def __init__(self, board, row, col, value, action_type, **kwargs):
        import copy
        self.board = copy.deepcopy(board)
        self.row = row
        self.col = col
        self.value = value
        self.action_type = action_type # 'try', 'backtrack', 'swap', 'new_iteration', 'info'
        for k, v in kwargs.items():
            setattr(self, k, v)
