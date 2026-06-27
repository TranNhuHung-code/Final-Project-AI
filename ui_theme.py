# -*- coding: utf-8 -*-
"""
ui_theme.py
===========
Module chứa cấu hình giao diện dùng chung cho toàn bộ 18 app thuật toán.
Thiết kế Dark Theme hiện đại, lấy cảm hứng từ nhánh main (Pygame).

Import module này trong mỗi app Tkinter để đảm bảo giao diện thống nhất.
"""

import tkinter as tk
from tkinter import ttk

# ======================== PALETTE MÀU ========================
# --- Nền ---
BG          = "#0a0a16"     # Nền chính (rất tối)
BG2         = "#0e0e1c"     # Nền phụ
CARD        = "#141428"     # Card / panel
CARD_HOVER  = "#1c1c36"     # Card hover

# --- Accent ---
ACCENT      = "#00c6ff"     # Xanh neon chính
ACCENT_DIM  = "#007fa3"     # Xanh neon nhạt
SUCCESS     = "#00e676"     # Xanh lá
ERROR       = "#ff5252"     # Đỏ
WARN        = "#ffab00"     # Vàng cam
INFO        = "#448aff"     # Xanh dương

# --- Text ---
TXT         = "#d8d8e8"     # Text chính
TXT_DIM     = "#6a6a88"     # Text phụ / mờ
TXT_BRIGHT  = "#ffffff"     # Text sáng hoàn toàn

# --- Grid ---
GRID_LINE       = "#22223a"
GRID_LINE_THICK = "#3a3a6a"

# --- Cell ---
CELL_CLUE_BG     = "#1a1a34"
CELL_CLUE_FG     = "#b0b0cc"
CELL_EMPTY_BG    = "#101024"
CELL_TRY_BG      = "#0a2a1a"
CELL_TRY_FG      = "#00e676"
CELL_BT_BG       = "#2a0a0a"
CELL_BT_FG       = "#ff5252"
CELL_SOLVED_BG   = "#0a1a3a"
CELL_SOLVED_FG   = "#00c6ff"
CELL_SWAP_BG     = "#2a1a00"
CELL_SWAP_FG     = "#ffab00"
CELL_CONFLICT_BG = "#3a0a1a"
CELL_CONFLICT_FG = "#ff1744"
CELL_SELECTED_BG = "#1a2a4a"
CELL_SELECTED_FG = "#82b1ff"

# --- Accent theo nhóm thuật toán ---
GROUP_COLORS = {
    1: "#2979ff",   # Uninformed Search – Blue
    2: "#00c853",   # Informed Search – Green
    3: "#ff9100",   # Local Search – Orange
    4: "#aa00ff",   # Complex Environments – Purple
    5: "#ff1744",   # CSP – Red
    6: "#00bcd4",   # Adversarial Search – Cyan
}
GROUP_COLORS_DIM = {
    1: "#1a3a6a",
    2: "#0a3a1a",
    3: "#3a2a0a",
    4: "#2a0a3a",
    5: "#3a0a1a",
    6: "#0a2a3a",
}

GROUP_NAMES = {
    1: "Uninformed Search",
    2: "Informed Search",
    3: "Local Search",
    4: "Complex Environments",
    5: "CSP",
    6: "Adversarial Search",
}

# --- Button ---
BTN_PRIMARY_BG    = "#1a3a6a"
BTN_PRIMARY_FG    = "#82b1ff"
BTN_SUCCESS_BG    = "#0a3a1a"
BTN_SUCCESS_FG    = "#69f0ae"
BTN_DANGER_BG     = "#3a0a1a"
BTN_DANGER_FG     = "#ff5252"
BTN_NEUTRAL_BG    = "#1a1a2e"
BTN_NEUTRAL_FG    = "#8888a8"
BTN_WARN_BG       = "#3a2a0a"
BTN_WARN_FG       = "#ffab00"

# ======================== FONTS ========================
FONT_TITLE  = ("Segoe UI", 18, "bold")
FONT_HEAD   = ("Segoe UI", 14, "bold")
FONT_SUB    = ("Segoe UI", 12)
FONT_BODY   = ("Segoe UI", 11)
FONT_SM     = ("Segoe UI", 10)
FONT_XS     = ("Segoe UI", 9)
FONT_CELL   = ("Consolas", 20, "bold")
FONT_CELL_SM = ("Consolas", 10)
FONT_BTN    = ("Segoe UI", 11, "bold")
FONT_MONO   = ("Consolas", 10)
FONT_LOG    = ("Consolas", 9)

# ======================== KÍCH THƯỚC ========================
SIZE = 9
BOX = 3
CELL_SIZE = 52
GRID_PAD = 3       # Padding quanh grid (viền dày)
CELL_PAD = 1       # Padding giữa các ô thường
BOX_PAD = 3        # Padding giữa các khối 3×3


# ======================== HELPER FUNCTIONS ========================

def create_styled_button(parent, text, command, bg=BTN_PRIMARY_BG, fg=BTN_PRIMARY_FG,
                          width=None, font=FONT_BTN, state="normal"):
    """Tạo button với style thống nhất."""
    btn = tk.Button(
        parent, text=text, command=command,
        font=font, bg=bg, fg=fg,
        activebackground=ACCENT_DIM, activeforeground=TXT_BRIGHT,
        relief="flat", bd=0, padx=14, pady=8,
        cursor="hand2", state=state,
    )
    if width:
        btn.config(width=width)
    return btn


def create_info_label(parent, text="", font=FONT_BODY, fg=TXT, anchor="w", justify="left"):
    """Tạo label thông tin với style thống nhất."""
    return tk.Label(
        parent, text=text, font=font, bg=BG, fg=fg,
        anchor=anchor, justify=justify,
    )


def create_card_frame(parent, bg=CARD):
    """Tạo frame dạng card với nền tối."""
    return tk.Frame(parent, bg=bg, bd=0, highlightthickness=0)


def apply_window_style(root, title, width=1100, height=750):
    """Áp dụng style chuẩn cho cửa sổ chính."""
    root.title(title)
    root.configure(bg=BG)
    root.geometry(f"{width}x{height}")
    root.resizable(True, True)
    # Đặt icon nếu có
    try:
        root.iconbitmap(default="")
    except Exception:
        pass


def build_sudoku_grid(parent, puzzle, cell_size=CELL_SIZE):
    """
    Xây dựng grid Sudoku 9×9 dùng Label.
    Trả về list 2D cell_labels[r][c].
    """
    grid_frame = tk.Frame(parent, bg=GRID_LINE_THICK, bd=0)

    cell_labels = [[None] * SIZE for _ in range(SIZE)]
    for r in range(SIZE):
        for c in range(SIZE):
            pad_top    = BOX_PAD if r % BOX == 0 else CELL_PAD
            pad_left   = BOX_PAD if c % BOX == 0 else CELL_PAD
            pad_bottom = BOX_PAD if r == SIZE - 1 else 0
            pad_right  = BOX_PAD if c == SIZE - 1 else 0

            is_clue = puzzle[r][c] != 0
            text = str(puzzle[r][c]) if is_clue else ""
            bg_color = CELL_CLUE_BG if is_clue else CELL_EMPTY_BG
            fg_color = CELL_CLUE_FG if is_clue else TXT_DIM

            lbl = tk.Label(
                grid_frame, text=text,
                width=3, height=1,
                font=FONT_CELL, bg=bg_color, fg=fg_color,
                relief="flat", bd=0,
            )
            lbl.grid(
                row=r, column=c,
                padx=(pad_left, pad_right),
                pady=(pad_top, pad_bottom),
                sticky="nsew",
            )
            cell_labels[r][c] = lbl

    return grid_frame, cell_labels


def render_board(cell_labels, board, puzzle, highlight=None):
    """
    Cập nhật toàn bộ grid theo board hiện tại.
    highlight: (row, col, action_type) — 'try', 'backtrack', 'solved', 'swap', ...
    """
    for r in range(SIZE):
        for c in range(SIZE):
            val = board[r][c]
            lbl = cell_labels[r][c]
            is_clue = puzzle[r][c] != 0
            text = str(val) if val != 0 else ""
            lbl.config(text=text)

            if highlight and highlight[0] == r and highlight[1] == c:
                action = highlight[2]
                if action == 'try':
                    lbl.config(bg=CELL_TRY_BG, fg=CELL_TRY_FG)
                elif action == 'backtrack':
                    lbl.config(bg=CELL_BT_BG, fg=CELL_BT_FG)
                elif action == 'solved':
                    lbl.config(bg=CELL_SOLVED_BG, fg=CELL_SOLVED_FG)
                elif action == 'swap':
                    lbl.config(bg=CELL_SWAP_BG, fg=CELL_SWAP_FG)
                elif action == 'conflict':
                    lbl.config(bg=CELL_CONFLICT_BG, fg=CELL_CONFLICT_FG)
                elif action == 'selected':
                    lbl.config(bg=CELL_SELECTED_BG, fg=CELL_SELECTED_FG)
                elif action == 'new_iteration':
                    lbl.config(bg="#0a2a2a", fg=ACCENT)
                continue

            if is_clue:
                lbl.config(bg=CELL_CLUE_BG, fg=CELL_CLUE_FG)
            elif val != 0:
                lbl.config(bg=CELL_SOLVED_BG, fg=CELL_SOLVED_FG)
            else:
                lbl.config(bg=CELL_EMPTY_BG, fg=TXT_DIM)


def render_board_multi_highlight(cell_labels, board, puzzle, highlights=None):
    """
    Cập nhật grid với NHIỀU ô được highlight cùng lúc.
    highlights: dict {(row, col): action_type}
    """
    if highlights is None:
        highlights = {}
    for r in range(SIZE):
        for c in range(SIZE):
            val = board[r][c]
            lbl = cell_labels[r][c]
            is_clue = puzzle[r][c] != 0
            text = str(val) if val != 0 else ""
            lbl.config(text=text)

            if (r, c) in highlights:
                action = highlights[(r, c)]
                color_map = {
                    'try':       (CELL_TRY_BG, CELL_TRY_FG),
                    'backtrack': (CELL_BT_BG, CELL_BT_FG),
                    'solved':    (CELL_SOLVED_BG, CELL_SOLVED_FG),
                    'swap':      (CELL_SWAP_BG, CELL_SWAP_FG),
                    'conflict':  (CELL_CONFLICT_BG, CELL_CONFLICT_FG),
                    'selected':  (CELL_SELECTED_BG, CELL_SELECTED_FG),
                }
                bg, fg = color_map.get(action, (CELL_SOLVED_BG, CELL_SOLVED_FG))
                lbl.config(bg=bg, fg=fg)
            elif is_clue:
                lbl.config(bg=CELL_CLUE_BG, fg=CELL_CLUE_FG)
            elif val != 0:
                lbl.config(bg=CELL_SOLVED_BG, fg=CELL_SOLVED_FG)
            else:
                lbl.config(bg=CELL_EMPTY_BG, fg=TXT_DIM)
