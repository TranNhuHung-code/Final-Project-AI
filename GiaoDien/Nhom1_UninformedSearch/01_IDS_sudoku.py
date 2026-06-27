# -*- coding: utf-8 -*-
"""
01_IDS_sudoku.py
================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: UNINFORMED SEARCH (Tìm kiếm mù / không thông tin)
Thuật toán trình bày: Iterative Deepening Search (IDS)
Bài toán áp dụng: Giải Sudoku 9x9
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import tkinter as tk
from base_gui import BaseSudokuApp
from ThuatToan.Nhom1_UninformedSearch.ids_solver import IDSSolver

def main():
    root = tk.Tk()
    app = BaseSudokuApp(
        root=root,
        title="01 - Iterative Deepening Search (IDS)",
        subtitle="Nhóm 1: Uninformed Search",
        algo_name="IDS",
        solver_class=IDSSolver,
        num_clues=42
    )
    root.mainloop()

if __name__ == "__main__":
    main()
