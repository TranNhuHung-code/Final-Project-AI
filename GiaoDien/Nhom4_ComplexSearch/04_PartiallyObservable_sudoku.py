# -*- coding: utf-8 -*-
"""
04_PartiallyObservable_sudoku.py
==================================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: SEARCHING IN COMPLEX ENVIRONMENTS
Thuật toán trình bày: Searching for Partially Observable Problems
Bài toán áp dụng: Giải Sudoku 9x9 (mô phỏng agent có sensor hạn chế)
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import tkinter as tk
from base_gui import BaseSudokuApp, COLOR_CLUE_BG, COLOR_CLUE_TEXT, COLOR_SELECTED_BG, TXT_B, SIZE
from ThuatToan.Nhom4_ComplexSearch.partial_observable_solver import PartiallyObservableSolver

# Specific Colors
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

class PartiallyObservableApp(BaseSudokuApp):
    def __init__(self, root):
        super().__init__(
            root=root,
            title="04 - Partially Observable Search",
            subtitle="Nhóm 4: Complex Environments",
            algo_name="Partially Observable",
            solver_class=PartiallyObservableSolver,
            num_clues=30
        )
        self.play_speed_ms = 250 # Slower speed for this algorithm
        self.speed_scale.set(self.play_speed_ms)

    def _set_difficulty(self):
        # Override to ensure real_solution is passed
        from sudoku_utils import generate_puzzle
        if self.is_solving or self.is_playing: return
        diff_map = {"Dễ": 45, "Trung bình": 35, "Khó": 25, "Cực Khó": 17}
        num = diff_map.get(self.diff_var.get(), 30)
        
        self.puzzle, self.real_solution = generate_puzzle(num_clues=num, seed=None)
        self.solver = self.solver_class(self.puzzle, self.real_solution)
        self._reset_state()
        self._render_board(self.puzzle)
        self._clear_log()
        self._log(f"Đã tạo đề mới (Độ khó: {self.diff_var.get()}, {num} manh mối)", "system")

    def toggle_edit_mode(self):
        super().toggle_edit_mode()
        if not self.edit_mode:
            # Edit mode off, we need to solve the puzzle to get real_solution
            from ThuatToan.Nhom1_UninformedSearch.ids_solver import IDSSolver
            ids = IDSSolver(self.puzzle)
            solution, _, _ = ids.solve()
            if solution:
                self.real_solution = solution
                self.solver = self.solver_class(self.puzzle, self.real_solution)
                self._log("Đã tính toán lời giải thật sự cho bảng tự nhập.", "system")
            else:
                self._log("Đề tự nhập không hợp lệ, không thể tìm lời giải.", "error")

    def _domain_text(self, domain_set):
        if len(domain_set) == 1:
            return str(next(iter(domain_set)))
        return "".join(str(v) for v in sorted(domain_set))

    def _render_board(self, board, highlight=None):
        if not board or (isinstance(board[0][0], int)):
            # Render normal numbers (e.g. init puzzle or edit mode)
            super()._render_board(board, highlight)
            return

        domains = board
        observed = None
        affected = []

        if highlight is not None:
            if isinstance(highlight, tuple) and len(highlight) == 2:
                observed = highlight
            elif isinstance(highlight, list):
                affected = highlight

        for r in range(SIZE):
            for c in range(SIZE):
                label = self.cell_labels[r][c]
                is_clue = hasattr(self, 'puzzle') and self.puzzle[r][c] != 0
                domain = domains[r][c]

                # Edit mode check
                if getattr(self, 'edit_mode', False) and getattr(self, 'selected_cell', None) == (r, c):
                    label.config(bg=COLOR_SELECTED_BG, fg=TXT_B)
                    continue

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

    def _play_next_step(self):
        if self.is_paused or not self.is_playing: return
            
        current = int(self.progress_scale.get())
        if current >= len(self.steps):
            self._finish_playing()
            return

        step = self.steps[current]
        action_type = getattr(step, 'action_type', 'init')
        domains = step.board

        if action_type == 'init':
            self._render_board(domains)
            self._log(f"Trạng thái Domain ban đầu. Các ô trống còn {getattr(step, 'detail', 0)} ô chưa biết.", "system")
        elif action_type == 'observe':
            self._render_board(domains, highlight=step.row)  # step.row is (row, col)
            r, c = step.row
            self._log(f"Sensor quan sát ô ({r+1}, {c+1}) = {step.col}", "try")
        elif action_type == 'propagate':
            self._render_board(domains, highlight=step.value) # step.value is affected_cells
            r, c = step.row
            num_affected = len(step.value)
            self._log(f"Lan truyền từ ô ({r+1}, {c+1}). Thu hẹp domain của {num_affected} ô.", "info")
        elif action_type == 'solved':
            self._render_board(domains)
            self._log("Đã biết toàn bộ bảng!", "success")

        # Trace Log
        if hasattr(step, 'detail') and step.detail:
            tag = action_type if action_type in ('try', 'backtrack', 'success', 'info', 'system') else 'info'
            self._log_trace(f"[{current+1}/{len(self.steps)}] {action_type.upper()}: còn {step.detail} ô ẩn.", tag)

        self.progress_scale.set(current + 1)
        self.root.after(self.play_speed_ms, self._play_next_step)

def main():
    root = tk.Tk()
    app = PartiallyObservableApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
