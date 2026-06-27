# -*- coding: utf-8 -*-
"""
06_Minimax_SudokuBattle.py
============================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: ADVERSARIAL SEARCH (Tìm kiếm đối kháng)
Thuật toán trình bày: Minimax
Bài toán áp dụng: "SUDOKU BATTLE" — biến thể 2 người chơi (Người vs Agent)

----------------------------------------------------------------------
LUẬT CHƠI "SUDOKU BATTLE" (PEAS):
    - Performance measure: số ô điền ĐÚNG (so với lời giải thật) của mỗi
      bên. Hết ô trống, bên nào điền đúng nhiều ô hơn THẮNG.
    - Environment: bàn cờ Sudoku 9x9 với một số ô gợi ý (clue) cho sẵn.
    - Actuators: chọn 1 ô trống + 1 giá trị (1-9) để điền vào, mỗi lượt
      đúng 1 ô.
    - Sensors: cả 2 bên đều thấy toàn bộ bàn cờ hiện tại (fully-observable),
      NHƯNG không ai biết trước lời giải thật — chỉ biết ĐÚNG/SAI sau khi
      đã điền.

    - Trạng thái bắt đầu: bàn cờ với các ô đề bài, điểm Người = Agent = 0.
    - Trạng thái kết thúc: không còn ô trống nào.
    - Đây là trò chơi ZERO-SUM 2 NGƯỜI, LUÂN PHIÊN LƯỢT: Agent đóng vai
      MAX (tối đa hóa hiệu số điểm Agent - điểm Người), Người được giả
      định đóng vai MIN trong quá trình Agent TÍNH TOÁN nước đi (dù
      Người thật chơi tùy ý, Agent vẫn lập kế hoạch theo worst-case).
    - Vì cây trò chơi quá lớn để duyệt hết, Agent dùng MINIMAX CÓ GIỚI
      HẠN ĐỘ SÂU + HÀM ĐÁNH GIÁ ở node lá. Chi tiết: xem file
      minimax_solver.py (MinimaxSudokuBattle).

CÁCH CHƠI:
    1. Bàn cờ Sudoku hiện ra, một số ô đã có giá trị sẵn (đề bài).
    2. Đến lượt Người: CLICK vào 1 ô trống, sau đó nhập số 1-9 ở ô nhập
       liệu, nhấn "Xác nhận điền số".
    3. Đến lượt Agent: Agent tự động dùng Minimax để chọn (ô, số) tốt
       nhất và điền vào (có hiển thị log quá trình suy luận ở khung bên).
    4. Lặp lại cho đến khi hết ô trống. Bên điền đúng nhiều ô hơn thắng.

CÁCH CHẠY:
    python 06_Minimax_SudokuBattle.py

YÊU CẦU: Python 3.x có sẵn thư viện tkinter.
----------------------------------------------------------------------
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import tkinter as tk
from tkinter import messagebox
import time
import threading

from sudoku_utils import SIZE, BOX, generate_puzzle
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

        # num_clues=48 -> khoảng 33 ô trống, đủ để trận đấu không quá dài
        # nhưng vẫn thể hiện rõ sự khác biệt chiến thuật giữa Người và Agent.
        self.puzzle, self.real_solution = generate_puzzle(num_clues=48, seed=None)
        self.game = MinimaxSudokuBattle(self.puzzle, self.real_solution,
                                         search_depth=3, candidate_cells_per_turn=6)

        self.selected_cell = None
        self.is_human_turn = True   # Người đi trước
        self.is_agent_thinking = False
        self.game_over = False

        self._build_ui()
        self._render_board()
        self._update_score_label()

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
        main_frame.pack(padx=12, pady=4)

        # ----- Khung bàn cờ (bên trái) -----
        left_frame = tk.Frame(main_frame, bg=BG)
        left_frame.grid(row=0, column=0, padx=(0, 16))

        score_frame = tk.Frame(left_frame, bg=CARD, highlightbackground=ACCENT, highlightthickness=1)
        score_frame.pack(pady=(0, 10), padx=20, fill="x")

        self.human_score_label = tk.Label(score_frame, text="Player 1 (Bạn): 0 điểm",
                                  font=FONT_TITLE, bg=CARD, fg=COLOR_P1_BG)
        self.human_score_label.pack(side="left", padx=20, pady=10)

        self.agent_score_label = tk.Label(score_frame, text="Player 2 (AI): 0 điểm",
                                  font=FONT_TITLE, bg=CARD, fg=COLOR_P2_BG)
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
                cell.grid(row=r, column=c,
                          padx=(pad_left, pad_right), pady=(pad_top, pad_bottom),
                          sticky="nsew")
                cell.bind("<Button-1>", lambda e, rr=r, cc=c: self.on_cell_click(rr, cc))
                self.cell_labels[r][c] = cell

        # ----- Khung nhập liệu -----
        input_frame = tk.Frame(left_frame, bg=BG)
        input_frame.pack(pady=8)

        tk.Label(input_frame, text="Ô đã chọn:", font=FONT_LABEL,
                 bg=BG, fg=TXT_D).grid(row=0, column=0, padx=4)
        self.selected_cell_label = tk.Label(input_frame, text="(chưa chọn)",
                                             font=FONT_LABEL, bg=BG, fg=TXT_B)
        self.selected_cell_label.grid(row=0, column=1, padx=4)

        tk.Label(input_frame, text="Số (1-9):", font=FONT_LABEL,
                 bg=BG, fg=TXT_D).grid(row=0, column=2, padx=4)
        self.value_entry = tk.Entry(input_frame, width=3, font=FONT_LABEL, bg=CARD, fg=TXT_B, insertbackground=TXT_B)
        self.value_entry.grid(row=0, column=3, padx=4)

        self.btn_confirm = tk.Button(input_frame, text="✓ Xác nhận điền số",
                                      command=self.on_confirm_human_move,
                                      font=FONT_LABEL, bg="#00E473", fg="black",
                                      activebackground="#00C463", relief="flat", padx=10, pady=4)
        self.btn_confirm.grid(row=0, column=4, padx=8)

        self.btn_new_game = tk.Button(left_frame, text="↻ Trận mới",
                                       command=self.on_new_game_click,
                                       font=FONT_LABEL, bg="#FF325A", fg=TXT_B,
                                       activebackground="#CC2848", relief="flat", padx=10, pady=6)
        self.btn_new_game.pack(pady=6)

        self.info_label = tk.Label(left_frame, text="Lượt của Bạn! Click chọn 1 ô trống, nhập số rồi xác nhận.",
                                    font=FONT_LABEL, bg=BG, fg=TXT_B,
                                    justify="left", wraplength=480)
        self.info_label.pack(pady=(6, 4))

        # ----- Khung log suy luận của Agent (bên phải) -----
        right_frame = tk.Frame(main_frame, bg="#111827", bd=1, relief="solid")
        right_frame.grid(row=0, column=1, sticky="ns")

        tk.Label(right_frame, text="🧠 Log suy luận Minimax của Agent",
                 font=("Segoe UI", 12, "bold"), bg="#111827", fg=TXT_B).pack(pady=(8, 4), padx=10)

        self.log_text = tk.Text(right_frame, width=42, height=28, bg="#0b0f14", fg=ACCENT,
                                 font=("Consolas", 9), wrap="word", state="disabled")
        self.log_text.pack(padx=10, pady=(0, 10))

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
    def _render_board(self):
        for r in range(SIZE):
            for c in range(SIZE):
                val = self.game.board[r][c]
                label = self.cell_labels[r][c]
                is_original_clue = self.puzzle[r][c] != 0

                label.config(text=str(val) if val != 0 else "")

                if self.selected_cell == (r, c):
                    label.config(bg=COLOR_SELECTED_BG, fg=COLOR_CLUE_TEXT)
                elif is_original_clue:
                    label.config(bg=COLOR_CLUE_BG, fg=COLOR_CLUE_TEXT)
                elif val == 0:
                    label.config(bg=COLOR_EMPTY_BG, fg=COLOR_CLUE_TEXT)
                # Các ô đã điền (đúng hoặc sai) giữ màu đã được set lúc điền
                # (xem _mark_cell_result), không reset lại ở đây.

    def _mark_cell_result(self, row, col, is_correct, by_agent):
        label = self.cell_labels[row][col]
        if by_agent:
            bg = COLOR_AGENT_CORRECT_BG if is_correct else COLOR_AGENT_WRONG_BG
            fg = COLOR_AGENT_CORRECT_TEXT if is_correct else COLOR_AGENT_WRONG_TEXT
        else:
            bg = COLOR_HUMAN_CORRECT_BG if is_correct else COLOR_HUMAN_WRONG_BG
            fg = COLOR_HUMAN_WRONG_TEXT if not is_correct else COLOR_HUMAN_CORRECT_TEXT
        label.config(bg=bg, fg=fg)

    # ------------------------------------------------------------------
    def on_cell_click(self, row, col):
        if self.game_over or not self.is_human_turn or self.is_agent_thinking:
            return
        if self.game.board[row][col] != 0:
            return  # ô đã có giá trị, không chọn được
        self.selected_cell = (row, col)
        self.selected_cell_label.config(text=f"(hàng {row + 1}, cột {col + 1})")
        self._render_board()

    def on_confirm_human_move(self):
        if self.game_over or not self.is_human_turn or self.is_agent_thinking:
            return
        if self.selected_cell is None:
            messagebox.showinfo("Chưa chọn ô", "Bạn cần click chọn 1 ô trống trước.")
            return

        raw = self.value_entry.get().strip()
        if not raw.isdigit() or not (1 <= int(raw) <= 9):
            messagebox.showinfo("Giá trị không hợp lệ", "Vui lòng nhập một số nguyên từ 1 đến 9.")
            return

        value = int(raw)
        row, col = self.selected_cell

        is_correct = self.game.human_move(row, col, value)
        self._mark_cell_result(row, col, is_correct, by_agent=False)
        self._log(f"👤 Người điền {value} tại (hàng {row+1}, cột {col+1}) "
                  f"-> {'ĐÚNG ✓' if is_correct else 'SAI ✗'}")

        self.selected_cell = None
        self.selected_cell_label.config(text="(chưa chọn)")
        self.value_entry.delete(0, "end")
        self._render_board()
        self._update_score_label()

        if self.game.is_game_over():
            self._end_game()
            return

        self.is_human_turn = False
        self.info_label.config(text="Lượt của Agent... Agent đang suy luận bằng Minimax.")
        self.root.after(300, self._agent_turn)

    def _agent_turn(self):
        self.is_agent_thinking = True

        def run_agent():
            t0 = time.time()
            row, col, value, trace = self.game.agent_choose_move()
            t1 = time.time()

            is_correct = self.game.agent_move(row, col, value)

            self.root.after(0, lambda: self._on_agent_move_done(
                row, col, value, is_correct, trace, t1 - t0))

        threading.Thread(target=run_agent, daemon=True).start()

    def _on_agent_move_done(self, row, col, value, is_correct, trace, elapsed):
        self._mark_cell_result(row, col, is_correct, by_agent=True)
        self._render_board()
        self._update_score_label()

        self._log(f"🤖 Agent (Minimax, độ sâu={self.game.search_depth}) suy luận trong {elapsed:.3f}s, "
                   f"đã đánh giá {self.game.nodes_evaluated:,} node:")
        for t in trace[:5]:
            self._log(f"     • Ô (hàng {t['row']+1}, cột {t['col']+1}) = {t['value']} "
                       f"→ giá trị Minimax = {t['score']}")
        self._log(f"   ➜ Agent CHỌN: điền {value} tại (hàng {row+1}, cột {col+1}) "
                   f"-> {'ĐÚNG ✓' if is_correct else 'SAI ✗'}\n")

        self.is_agent_thinking = False

        if self.game.is_game_over():
            self._end_game()
            return

        self.is_human_turn = True
        self.info_label.config(text="Lượt của Người! Click chọn 1 ô trống, nhập số rồi xác nhận.")

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

    def on_new_game_click(self):
        self.puzzle, self.real_solution = generate_puzzle(num_clues=48, seed=None)
        self.game = MinimaxSudokuBattle(self.puzzle, self.real_solution,
                                         search_depth=3, candidate_cells_per_turn=6)
        self.selected_cell = None
        self.is_human_turn = True
        self.is_agent_thinking = False
        self.game_over = False
        self.selected_cell_label.config(text="(chưa chọn)")
        self.value_entry.delete(0, "end")
        self._render_board()
        self._update_score_label()
        self.info_label.config(text="Trận mới! Lượt của Người. Click chọn 1 ô trống, nhập số rồi xác nhận.")
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")


def main():
    root = tk.Tk()
    app = MinimaxBattleApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
