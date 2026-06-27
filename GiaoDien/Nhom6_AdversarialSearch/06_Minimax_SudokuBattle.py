# -*- coding: utf-8 -*-
"""
06_Minimax_SudokuBattle.py
============================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: ADVERSARIAL SEARCH (Tìm kiếm đối kháng)
Thuật toán trình bày: Minimax
Bài toán áp dụng: "SUDOKU BATTLE" — biến thể 2 người chơi (Người vs Agent)
"""

import sys
import os
import copy
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading

from sudoku_utils import SIZE, BOX, generate_puzzle, _fill_full_board
from ThuatToan.Nhom6_AdversarialSearch.minimax_solver import MinimaxSudokuBattle


# ===================== CẤU HÌNH MÀU SẮC (Cyberpunk Theme) =====================
BG = "#080816"              
CARD = "#141630"            
ACCENT = "#00C6FF"          
TXT = "#D7DAE8"             
TXT_D = "#646987"           
TXT_B = "#FFFFFF"           

COLOR_CLUE_TEXT = "#A0A5D0"
COLOR_CLUE_BG = "#2A2D54"
COLOR_EMPTY_BG = "#1A1C38"
COLOR_P1_BG = "#00E473"     
COLOR_P1_TEXT = "#000000"
COLOR_P2_BG = "#FF325A"     
COLOR_P2_TEXT = "#FFFFFF"
COLOR_WIN_FLASH = "#00B9FF"
COLOR_AGENT_CORRECT_TEXT = "#1d4ed8"
COLOR_AGENT_WRONG_BG = "#ffe3b3"
COLOR_AGENT_WRONG_TEXT = "#8a4b00"
COLOR_SELECTED_BG = "#2c3e50"
COLOR_AGENT_CORRECT_BG = "#d1fae5"
COLOR_HUMAN_CORRECT_BG = "#d1fae5"
COLOR_HUMAN_WRONG_BG = "#ffe3b3"
COLOR_HUMAN_WRONG_TEXT = "#8a4b00"
COLOR_HUMAN_CORRECT_TEXT = "#1d4ed8"


FONT_CELL = ("Segoe UI", 16, "bold")
FONT_LABEL = ("Segoe UI", 12)
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SCORE = ("Segoe UI", 14, "bold")


class MinimaxBattleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Battle - Minimax (Người vs Agent)")
        self.root.configure(bg=BG)
        self.root.minsize(1050, 750)

        self.edit_mode = False
        self.moves_history = []
        
        self._build_ui()
        self.on_new_game_click()
        
        self.root.bind("<Key>", self.on_key_press)

    # ------------------------------------------------------------------
    def _build_ui(self):
        title = tk.Label(self.root, text="Sudoku Battle: You vs Minimax AI",
                          font=FONT_TITLE, bg=BG, fg=ACCENT)
        title.pack(pady=(12, 4))

        subtitle = tk.Label(
            self.root,
            text="Nhóm 6: Adversarial Search   |   Bạn đi trước (Màu Xanh), AI đi sau (Màu Đỏ)",
            font=FONT_LABEL, bg=BG, fg=TXT_D
        )
        subtitle.pack(pady=(0, 10))

        main_frame = tk.Frame(self.root, bg=BG)
        main_frame.pack(padx=12, pady=4, fill="both", expand=True)

        # ----- Khung bàn cờ (bên trái) -----
        left_frame = tk.Frame(main_frame, bg=BG)
        left_frame.grid(row=0, column=0, padx=(0, 16), sticky="n")

        score_frame = tk.Frame(left_frame, bg=CARD, highlightbackground=ACCENT, highlightthickness=1)
        score_frame.pack(pady=(0, 10), padx=20, fill="x")

        self.human_score_label = tk.Label(score_frame, text="👤 Người: 0", font=FONT_TITLE, bg=CARD, fg=COLOR_P1_BG)
        self.human_score_label.pack(side="left", padx=20, pady=10)

        self.agent_score_label = tk.Label(score_frame, text="🤖 Agent: 0", font=FONT_TITLE, bg=CARD, fg=COLOR_P2_BG)
        self.agent_score_label.pack(side="right", padx=20, pady=10)

        grid_frame = tk.Frame(left_frame, bg="#2A2D54", bd=2)
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
                    relief="flat", borderwidth=0, cursor="hand2"
                )
                cell.grid(row=r, column=c, padx=(pad_left, pad_right), pady=(pad_top, pad_bottom), sticky="nsew")
                cell.bind("<Button-1>", lambda e, rr=r, cc=c: self.on_cell_click(rr, cc))
                self.cell_labels[r][c] = cell

        # ----- Khung Controls Mới -----
        controls_frame = tk.Frame(left_frame, bg=BG)
        controls_frame.pack(pady=4)

        self.diff_var = tk.StringVar(value="Trung bình")
        combo_diff = ttk.Combobox(controls_frame, textvariable=self.diff_var, values=["Dễ", "Trung bình", "Khó"], state="readonly", width=10)
        combo_diff.pack(side="left", padx=4)
        combo_diff.bind("<<ComboboxSelected>>", lambda e: self.on_new_game_click())

        self.btn_new_game = tk.Button(controls_frame, text="↻ Trận mới", command=self.on_new_game_click,
                                       font=FONT_LABEL, bg="#FFBE00", fg="black", activebackground="#D9A200", relief="flat", padx=6, pady=2)
        self.btn_new_game.pack(side="left", padx=4)

        self.btn_edit = tk.Button(controls_frame, text="Tự nhập đề", command=self.toggle_edit_mode,
                                       font=FONT_LABEL, bg="#9D4EDD", fg=TXT_B, activebackground="#7B2CBF", relief="flat", padx=6, pady=2)
        self.btn_edit.pack(side="left", padx=4)

        self.btn_undo = tk.Button(controls_frame, text="↶ Lùi nước", command=self.undo_move,
                                       font=FONT_LABEL, bg=TXT_D, fg=TXT_B, activebackground="#4B5563", relief="flat", padx=6, pady=2)
        self.btn_undo.pack(side="left", padx=4)

        self.btn_stop = tk.Button(controls_frame, text="⏹ Dừng", command=self.on_stop_click, state="disabled",
                                       font=FONT_LABEL, bg="#FF325A", fg=TXT_B, activebackground="#CC2848", relief="flat", padx=6, pady=2)
        self.btn_stop.pack(side="left", padx=4)

        self.info_label = tk.Label(left_frame, text="Lượt của Bạn! Click chọn 1 ô trống, gõ phím số (1-9) để điền.",
                                    font=FONT_LABEL, bg=BG, fg=TXT_B, justify="left", wraplength=480)
        self.info_label.pack(pady=(12, 4))

        # ----- Khung log suy luận của Agent (bên phải) -----
        right_frame = tk.Frame(main_frame, bg="#111827", bd=1, relief="solid")
        right_frame.grid(row=0, column=1, sticky="nsew")
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        tk.Label(right_frame, text="🧠 Log hệ thống & Suy luận",
                 font=("Segoe UI", 12, "bold"), bg="#111827", fg=TXT_B).pack(pady=(8, 4), padx=10)

        self.log_text = tk.Text(right_frame, bg="#0b0f14", fg=ACCENT,
                                 font=("Consolas", 10), wrap="word", state="disabled")
        self.log_text.pack(padx=10, pady=(0, 10), fill="both", expand=True)

    # ------------------------------------------------------------------
    def _log(self, text):
        self.log_text.config(state="normal")
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _update_score_label(self):
        self.human_score_label.config(text=f"👤 Người: {self.game.human_score}")
        self.agent_score_label.config(text=f"🤖 Agent: {self.game.agent_score}")

    # ------------------------------------------------------------------
    def on_new_game_click(self):
        if getattr(self, 'edit_mode', False): return
        diff_map = {"Dễ": 40, "Trung bình": 30, "Khó": 20}
        num = diff_map.get(self.diff_var.get(), 30)
        
        self.puzzle, self.real_solution = generate_puzzle(num_clues=num, seed=None)
        self._start_game_with_puzzle()
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
        self._log(f"[HỆ THỐNG] Đã tạo trận mới (Độ khó: {self.diff_var.get()})")
        
    def _start_game_with_puzzle(self):
        self.game = MinimaxSudokuBattle(self.puzzle, self.real_solution, search_depth=2, candidate_cells_per_turn=6)
        self.moves_history = []
        self.selected_cell = None
        self.is_human_turn = True
        self.is_agent_thinking = False
        self.game_over = False
        self._render_board()
        self._update_score_label()
        self.info_label.config(text="Trận mới! Lượt của Bạn. Click chọn 1 ô trống, gõ phím số (1-9) để điền.")

    def toggle_edit_mode(self):
        if getattr(self, 'is_agent_thinking', False): return
        
        if not self.edit_mode:
            self.edit_mode = True
            self.btn_edit.config(text="✓ Xác nhận đề", bg="#00E473", fg="black")
            self.btn_new_game.config(state="disabled")
            self.btn_confirm.config(state="disabled")
            self.btn_undo.config(state="disabled")
            
            # Clear board
            self.puzzle = [[0]*9 for _ in range(9)]
            self.moves_history = []
            self.selected_cell = None
            self.game_over = True 
            self._render_board()
            self.info_label.config(text="Chế độ nhập đề. Click vào ô và gõ phím số (1-9). Bấm Xác nhận khi xong.")
            self._log("\n[HỆ THỐNG] --- VÀO CHẾ ĐỘ NHẬP ĐỀ TAY ---")
        else:
            temp = copy.deepcopy(self.puzzle)
            if not _fill_full_board(temp):
                messagebox.showerror("Lỗi", "Đề bài bạn nhập KHÔNG HỢP LỆ (hoặc không có lời giải). Vui lòng sửa lại.")
                return
            
            self.real_solution = temp
            self.edit_mode = False
            self.btn_edit.config(text="Tự nhập đề", bg="#9D4EDD", fg=TXT_B)
            self.btn_new_game.config(state="normal")
            self.btn_confirm.config(state="normal")
            self.btn_undo.config(state="normal")
            
            self._start_game_with_puzzle()
            self._log("\n[HỆ THỐNG] Đã xác nhận đề tự nhập. Trận đấu bắt đầu!")

    def undo_move(self):
        if self.is_agent_thinking or self.edit_mode: return
        if not self.moves_history: return
        
        if len(self.moves_history) >= 2:
            self.moves_history = self.moves_history[:-2]
        else:
            self.moves_history = []
            
        self.game = MinimaxSudokuBattle(self.puzzle, self.real_solution, search_depth=2, candidate_cells_per_turn=6)
        for m in self.moves_history:
            if m['by_agent']:
                self.game.agent_move(m['row'], m['col'], m['val'])
            else:
                self.game.human_move(m['row'], m['col'], m['val'])
                
        self.selected_cell = None
        self.game_over = False
        self.is_human_turn = True
        self._render_board()
        self._update_score_label()
        self.info_label.config(text="Đã lùi nước. Lượt của Bạn!")
        self._log("\n[HỆ THỐNG] Đã lùi lại nước đi trước đó.\n")

    # ------------------------------------------------------------------
    def _render_board(self):
        for r in range(SIZE):
            for c in range(SIZE):
                val = self.puzzle[r][c] if self.edit_mode else self.game.board[r][c]
                label = self.cell_labels[r][c]
                is_original_clue = self.puzzle[r][c] != 0

                label.config(text=str(val) if val != 0 else "")

                if self.edit_mode and self.selected_cell == (r, c):
                    label.config(bg=COLOR_SELECTED_BG, fg=TXT_B)
                elif not self.edit_mode and self.selected_cell == (r, c):
                    label.config(bg=COLOR_SELECTED_BG, fg=COLOR_CLUE_TEXT)
                elif is_original_clue:
                    label.config(bg=COLOR_CLUE_BG, fg=COLOR_CLUE_TEXT)
                elif val == 0:
                    label.config(bg=COLOR_EMPTY_BG, fg=COLOR_CLUE_TEXT)
                else:
                    if not self.edit_mode:
                        # Find if it was human or agent
                        bg = COLOR_EMPTY_BG
                        fg = TXT_B
                        for m in self.moves_history:
                            if m['row'] == r and m['col'] == c:
                                if m['by_agent']:
                                    bg = COLOR_AGENT_CORRECT_BG if m['correct'] else COLOR_AGENT_WRONG_BG
                                    fg = COLOR_AGENT_CORRECT_TEXT if m['correct'] else COLOR_AGENT_WRONG_TEXT
                                else:
                                    bg = COLOR_HUMAN_CORRECT_BG if m['correct'] else COLOR_HUMAN_WRONG_BG
                                    fg = COLOR_HUMAN_CORRECT_TEXT if m['correct'] else COLOR_HUMAN_WRONG_TEXT
                        label.config(bg=bg, fg=fg)

    def on_cell_click(self, row, col):
        if self.edit_mode:
            self.selected_cell = (row, col)
            self._render_board()
            return
            
        if self.game_over or not self.is_human_turn or self.is_agent_thinking:
            return
        if self.game.board[row][col] != 0:
            return  
        self.selected_cell = (row, col)
        self._render_board()

    def on_key_press(self, event):
        if not self.selected_cell: return
        r, c = self.selected_cell

        if self.edit_mode:
            if event.char in "123456789":
                self.puzzle[r][c] = int(event.char)
                self._render_board()
            elif event.keysym in ("BackSpace", "Delete", "0"):
                self.puzzle[r][c] = 0
                self._render_board()
        else:
            if self.game_over or not self.is_human_turn or self.is_agent_thinking:
                return
            if event.char in "123456789":
                value = int(event.char)
                is_correct = self.game.human_move(r, c, value)
                self.moves_history.append({'row': r, 'col': c, 'val': value, 'by_agent': False, 'correct': is_correct})
                
                self._log(f"👤 Người điền {value} tại (hàng {r+1}, cột {c+1}) -> {'ĐÚNG ✓' if is_correct else 'SAI ✗'}")

                self.selected_cell = None
                self._render_board()
                self._update_score_label()

                if self.game.is_game_over():
                    self._end_game()
                    return

                self.is_human_turn = False
                self.info_label.config(text="Lượt của Agent... Agent đang suy luận.")
                self.root.after(300, self._agent_turn)

    def on_stop_click(self):
        if not getattr(self, 'is_agent_thinking', False): return
        self._log("Đang dừng Agent...", "error")
        if hasattr(self, 'agent_thread') and self.agent_thread.is_alive():
            import ctypes
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self.agent_thread.ident), ctypes.py_object(SystemExit))
        
        self.is_agent_thinking = False
        self.is_human_turn = True
        self.btn_stop.config(state="disabled")
        self.info_label.config(text="Đã dừng Agent. Lượt của Bạn!")
        self._log("Agent đã bị người dùng dừng lại.", "error")

    def _agent_turn(self):
        self.is_agent_thinking = True
        self.btn_stop.config(state="normal")

        def run_agent():
            t0 = time.time()
            row, col, value, trace = self.game.agent_choose_move()
            t1 = time.time()
            is_correct = self.game.agent_move(row, col, value)
            self.root.after(0, lambda: self._on_agent_move_done(row, col, value, is_correct, trace, t1 - t0))

        self.agent_thread = threading.Thread(target=run_agent, daemon=True)
        self.agent_thread.start()

    def _on_agent_move_done(self, row, col, value, is_correct, trace, elapsed):
        self.btn_stop.config(state="disabled")
        self.moves_history.append({'row': row, 'col': col, 'val': value, 'by_agent': True, 'correct': is_correct})
        self._render_board()
        self._update_score_label()

        self._log(f"🤖 Agent (Minimax, độ sâu={self.game.search_depth}) suy luận trong {elapsed:.3f}s:")
        self._log(f"   ➜ Agent CHỌN: điền {value} tại (hàng {row+1}, cột {col+1}) -> {'ĐÚNG ✓' if is_correct else 'SAI ✗'}\n")

        self.is_agent_thinking = False

        if self.game.is_game_over():
            self._end_game()
            return

        self.is_human_turn = True
        self.info_label.config(text="Lượt của Bạn! Click chọn 1 ô trống, gõ phím số (1-9) để điền.")

    def _end_game(self):
        self.game_over = True
        h, a = self.game.human_score, self.game.agent_score
        if h > a:
            result_text = f"🎉 NGƯỜI THẮNG! ({h} - {a})"
        elif a > h:
            result_text = f"🤖 AGENT THẮNG! ({a} - {h})"
        else:
            result_text = f"🤝 HÒA! ({h} - {a})"

        self.info_label.config(text=f"TRẬN ĐẤU KẾT THÚC — {result_text}")
        self._log(f"\n=== KẾT THÚC TRẬN ĐẤU: {result_text} ===")
        messagebox.showinfo("Kết thúc trận đấu", result_text)


def main():
    root = tk.Tk()
    app = MinimaxBattleApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

