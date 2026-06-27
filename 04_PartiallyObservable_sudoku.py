# -*- coding: utf-8 -*-
"""
04_PartiallyObservable_sudoku.py
==================================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: SEARCHING IN COMPLEX ENVIRONMENTS (Tìm kiếm trong môi trường phức tạp)
Thuật toán trình bày: Searching for Partially Observable Problems
                       (Tìm kiếm trong môi trường quan sát được một phần)
Bài toán áp dụng: Giải Sudoku 9x9 (mô phỏng agent có sensor hạn chế)

----------------------------------------------------------------------
MÔ TẢ BÀI TOÁN (PEAS):
    - Performance measure: Suy luận ra đúng toàn bộ bảng Sudoku, số lượt
      QUAN SÁT TRỰC TIẾP (percept) cần dùng càng ít càng tốt.
    - Environment: Bảng Sudoku 9x9. Agent KHÔNG nhìn thấy toàn bộ bảng —
      đây là điểm khác biệt cốt lõi so với các nhóm thuật toán trước
      (BFS/DFS/A*/IDA*/SA đều giả định fully-observable).
    - Actuators: "Yêu cầu quan sát" 1 ô bất kỳ còn chưa biết chắc giá trị.
    - Sensors: Tại mỗi lượt, sensor CHỈ trả về giá trị chính xác của
      ĐÚNG MỘT ô được agent chọn quan sát (ví dụ: camera quét từng ô một).

    - Belief state (trạng thái niềm tin): vì agent không biết chắc toàn
      bộ bảng, ta không thể biểu diễn trạng thái là 1 bảng cụ thể, mà
      phải biểu diễn là tập DOMAIN (miền giá trị khả dĩ) cho từng ô.
      Trạng thái bắt đầu: domain của ô đề bài (clue) = {giá trị đã cho},
      domain của ô trống = mọi giá trị 1-9 còn hợp lệ theo luật Sudoku.
    - Trạng thái mục tiêu: belief state thu hẹp về DUY NHẤT 1 khả năng,
      tức MỌI ô đều có domain kích thước 1 (agent đã biết/suy luận chắc
      chắn toàn bộ bảng).
    - Các bước để tìm ra Solution:
        1) Quan sát (percept) giá trị thật của 1 ô ngẫu nhiên còn chưa
           chắc -> domain ô đó thu về {giá trị quan sát được}.
        2) Lan truyền ràng buộc (constraint propagation): loại giá trị
           đó khỏi domain của các ô cùng hàng/cột/khung 3x3.
        3) Lặp lại "domino effect": bất kỳ ô nào domain bị thu hẹp về
           đúng 1 giá trị thì coi như đã biết chắc, tiếp tục lan truyền.
        4) Lặp lại bước 1-3 cho đến khi belief state chỉ còn 1 khả năng.
      Chi tiết: xem file partial_observable_solver.py.

CÁCH CHẠY:
    python 04_PartiallyObservable_sudoku.py

YÊU CẦU: Python 3.x có sẵn thư viện tkinter.
----------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import messagebox
import time
import threading

from sudoku_utils import SIZE, BOX, generate_puzzle
from partial_observable_solver import PartiallyObservableSolver


# ===================== CẤU HÌNH MÀU SẮC (Cyberpunk Theme) =====================
BG = "#080816"              
CARD = "#141630"            
ACCENT = "#00C6FF"          
TXT = "#D7DAE8"             
TXT_D = "#646987"           
TXT_B = "#FFFFFF"           

COLOR_CLUE_TEXT = "#A0A5D0"
COLOR_CLUE_BG = "#2A2D54"
COLOR_UNKNOWN_BG = "#1A1C38"        
COLOR_UNKNOWN_TEXT = "#646987"
COLOR_OBSERVED_BG = "#00C6FF"       
COLOR_OBSERVED_TEXT = "#000000"
COLOR_PROPAGATED_BG = "#FFF3B0"     
COLOR_PROPAGATED_TEXT = "#946800"
COLOR_SOLVED_BG = "#00E473"
COLOR_SOLVED_TEXT = "#000000"

FONT_CELL = ("Segoe UI", 16, "bold")
FONT_DOMAIN = ("Segoe UI", 8)
FONT_LABEL = ("Segoe UI", 12)
FONT_TITLE = ("Segoe UI", 16, "bold")


class PartiallyObservableVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Partially Observable Search - giải Sudoku 9x9")
        self.root.configure(bg=BG)

        self.puzzle, self.real_solution = generate_puzzle(num_clues=30, seed=None)
        self.solver = PartiallyObservableSolver(self.puzzle, self.real_solution)

        self.steps = []
        self.stats = {}
        self.solution_board = None
        self.is_solving = False
        self.is_playing = False
        self.current_step_index = -1
        self.play_speed_ms = 250  # ít bước hơn các thuật toán khác -> tốc độ chậm hơn để dễ quan sát

        self._build_ui()
        self._render_initial_domains()

    # ------------------------------------------------------------------
    def _build_ui(self):
        title = tk.Label(self.root, text="Partially Observable Search | Sudoku 9x9",
                          font=FONT_TITLE, bg=BG, fg=ACCENT)
        title.pack(pady=(12, 4))

        subtitle = tk.Label(
            self.root,
            text="Nhóm 4: Searching in Complex Environments   |   Đồ án cuối kỳ môn Trí Tuệ Nhân Tạo",
            font=FONT_LABEL, bg=BG, fg=TXT_D
        )
        subtitle.pack(pady=(0, 4))

        note = tk.Label(
            self.root,
            text="Agent chỉ được sensor cho quan sát ĐÚNG 1 Ô/lượt — các ô còn lại phải SUY LUẬN qua lan truyền ràng buộc.",
            font=("Segoe UI", 10, "italic"), bg=BG, fg=TXT_D
        )
        note.pack(pady=(0, 10))

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
                    grid_frame, text="", width=5, height=2,
                    font=FONT_DOMAIN, bg=COLOR_UNKNOWN_BG, fg=COLOR_UNKNOWN_TEXT,
                    relief="flat", borderwidth=0, justify="center"
                )
                cell.grid(row=r, column=c,
                          padx=(pad_left, pad_right), pady=(pad_top, pad_bottom),
                          sticky="nsew")
                self.cell_labels[r][c] = cell

        control_frame = tk.Frame(self.root, bg=CARD, highlightbackground=ACCENT, highlightthickness=1)
        control_frame.pack(pady=10)

        self.btn_solve = tk.Button(control_frame, text="▶ Giải (chạy ngầm)",
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
        self.speed_scale = tk.Scale(speed_frame, from_=20, to=1000, orient="horizontal",
                                     length=220, bg=BG, fg=TXT_B,
                                     troughcolor=CARD, highlightthickness=0,
                                     command=self._on_speed_change)
        self.speed_scale.set(self.play_speed_ms)
        self.speed_scale.pack(side="left")

        self.info_label = tk.Label(self.root, text="Nhấn 'Giải' để bắt đầu.",
                                    font=FONT_LABEL, bg=BG, fg=TXT_B,
                                    justify="left")
        self.info_label.pack(pady=(4, 12))

    def _on_speed_change(self, value):
        self.play_speed_ms = int(value)

    # ------------------------------------------------------------------
    def _domain_text(self, domain_set):
        """Hiển thị domain: nếu chỉ 1 giá trị -> in to; nếu nhiều giá trị
        -> in nhỏ danh sách các khả năng còn lại."""
        if len(domain_set) == 1:
            return str(next(iter(domain_set)))
        return "".join(str(v) for v in sorted(domain_set))

    def _render_initial_domains(self):
        domains = self.solver._init_domains()
        for r in range(SIZE):
            for c in range(SIZE):
                if self.puzzle[r][c] != 0:
                    self.cell_labels[r][c].config(
                        text=str(self.puzzle[r][c]), font=FONT_CELL,
                        bg=COLOR_CLUE_BG, fg=COLOR_CLUE_TEXT
                    )
                else:
                    self.cell_labels[r][c].config(
                        text=self._domain_text(domains[r][c]), font=FONT_DOMAIN,
                        bg=COLOR_UNKNOWN_BG, fg=COLOR_UNKNOWN_TEXT
                    )

    def _render_domains(self, domains, observed=None, affected=None):
        affected = affected or []
        for r in range(SIZE):
            for c in range(SIZE):
                label = self.cell_labels[r][c]
                is_clue = self.puzzle[r][c] != 0
                domain = domains[r][c]

                if is_clue:
                    label.config(text=str(self.puzzle[r][c]), font=FONT_CELL,
                                 bg=COLOR_CLUE_BG, fg=COLOR_CLUE_TEXT)
                    continue

                if observed is not None and (r, c) == observed:
                    label.config(text=self._domain_text(domain), font=FONT_CELL,
                                 bg=COLOR_OBSERVED_BG, fg=COLOR_OBSERVED_TEXT)
                elif (r, c) in affected:
                    label.config(text=self._domain_text(domain), font=FONT_DOMAIN,
                                 bg=COLOR_PROPAGATED_BG, fg=COLOR_PROPAGATED_TEXT)
                elif len(domain) == 1:
                    label.config(text=self._domain_text(domain), font=FONT_CELL,
                                 bg=COLOR_SOLVED_BG, fg=COLOR_SOLVED_TEXT)
                else:
                    label.config(text=self._domain_text(domain), font=FONT_DOMAIN,
                                 bg=COLOR_UNKNOWN_BG, fg=COLOR_UNKNOWN_TEXT)

    def _render_final_solution(self, board):
        for r in range(SIZE):
            for c in range(SIZE):
                label = self.cell_labels[r][c]
                label.config(text=str(board[r][c]), font=FONT_CELL)
                if self.puzzle[r][c] != 0:
                    label.config(bg=COLOR_CLUE_BG, fg=COLOR_CLUE_TEXT)
                else:
                    label.config(bg=COLOR_SOLVED_BG, fg=COLOR_SOLVED_TEXT)

    # ------------------------------------------------------------------
    def on_solve_click(self):
        if self.is_solving:
            return
        self.is_solving = True
        self.btn_solve.config(state="disabled", text="⏳ Đang chạy...")
        self.info_label.config(text="Agent đang quan sát từng ô và suy luận belief state, vui lòng chờ...")

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
        self.btn_solve.config(state="normal", text="▶ Giải (chạy ngầm)")

        if self.solution_board is None:
            messagebox.showwarning("Chưa suy luận xong",
                                    "Agent chưa thu hẹp được belief state về 1 lời giải duy nhất "
                                    "trong số lượt quan sát cho phép.")
            self.info_label.config(text="Chưa suy luận ra lời giải hoàn chỉnh.")
            return

        self.btn_play.config(state="normal")
        self.btn_skip.config(state="normal")
        self.current_step_index = -1

        empty_cells = 81 - self.stats['cells_given_as_clue']
        info_text = (
            f"Agent đã suy luận xong toàn bộ bảng! Số ô đề bài: {self.stats['cells_given_as_clue']} | "
            f"Số ô trống: {empty_cells} | "
            f"Số ô agent CHỈ CẦN QUAN SÁT TRỰC TIẾP: {self.stats['observations_made']} "
            f"({empty_cells - self.stats['observations_made']} ô còn lại được SUY LUẬN nhờ lan truyền ràng buộc) | "
            f"Thời gian: {self.stats['elapsed_seconds']}s\n"
            f"Nhấn 'Phát lại từng bước' để xem trực quan quá trình quan sát & suy luận."
        )
        self.info_label.config(text=info_text)

    def on_play_click(self):
        if self.is_playing or not self.steps:
            return
        self.is_playing = True
        self.btn_play.config(state="disabled")
        self.btn_solve.config(state="disabled")
        self._render_initial_domains()
        self._play_next_step()

    def _play_next_step(self):
        self.current_step_index += 1

        if self.current_step_index >= len(self.steps):
            self.is_playing = False
            self.btn_play.config(state="normal", text="⏵ Phát lại từng bước")
            if self.solution_board:
                self._render_final_solution(self.solution_board)
            self.info_label.config(text="Đã phát xong toàn bộ quá trình quan sát & suy luận belief state.")
            return

        step = self.steps[self.current_step_index]

        if step.action_type == 'init':
            self._render_domains(step.domains)
            self.info_label.config(
                text=f"Trạng thái belief ban đầu: {step.num_unknown_cells} ô chưa biết chắc "
                     f"(sau khi lan truyền ràng buộc từ các ô đề bài)."
            )
        elif step.action_type == 'observe':
            self._render_domains(step.domains, observed=step.observed_cell)
            self.info_label.config(
                text=f"Bước {self.current_step_index + 1}/{len(self.steps)} | "
                     f"🔍 SENSOR QUAN SÁT ô (hàng {step.observed_cell[0] + 1}, "
                     f"cột {step.observed_cell[1] + 1}) = {step.observed_value} | "
                     f"Số ô còn chưa biết chắc: {step.num_unknown_cells}"
            )
        elif step.action_type == 'propagate':
            self._render_domains(step.domains, observed=step.observed_cell,
                                  affected=step.affected_cells)
            self.info_label.config(
                text=f"Bước {self.current_step_index + 1}/{len(self.steps)} | "
                     f"⚡ LAN TRUYỀN RÀNG BUỘC: {len(step.affected_cells)} ô bị thu hẹp domain "
                     f"(màu vàng) | Số ô còn chưa biết chắc: {step.num_unknown_cells}"
            )
        elif step.action_type == 'solved':
            self._render_domains(step.domains)
            self.info_label.config(text="✅ Belief state đã thu hẹp về DUY NHẤT 1 lời giải!")

        self.root.after(self.play_speed_ms, self._play_next_step)

    def on_skip_click(self):
        self.is_playing = False
        self.current_step_index = len(self.steps)
        if self.solution_board:
            self._render_final_solution(self.solution_board)
            self.info_label.config(text="Đã hiển thị kết quả cuối cùng (bỏ qua phát lại từng bước).")
        self.btn_play.config(state="normal")
        self.btn_solve.config(state="normal")

    def on_new_puzzle_click(self):
        if self.is_solving or self.is_playing:
            return
        self.puzzle, self.real_solution = generate_puzzle(num_clues=30, seed=None)
        self.solver = PartiallyObservableSolver(self.puzzle, self.real_solution)
        self.steps = []
        self.stats = {}
        self.solution_board = None
        self.current_step_index = -1
        self.btn_play.config(state="disabled")
        self.btn_skip.config(state="disabled")
        self._render_initial_domains()
        self.info_label.config(text="Đã sinh đề mới. Nhấn 'Giải' để bắt đầu.")


def main():
    root = tk.Tk()
    app = PartiallyObservableVisualizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
