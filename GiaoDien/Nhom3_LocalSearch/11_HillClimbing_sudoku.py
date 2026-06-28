# -*- coding: utf-8 -*-
"""
11_HillClimbing_sudoku.py
================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: LOCAL SEARCH
Thuật toán trình bày: Hill Climbing
Bài toán áp dụng: Giải Sudoku 9x9
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import tkinter as tk
from base_gui import BaseSudokuApp
from ThuatToan.Nhom3_LocalSearch.hill_climbing_solver import HillClimbingSolver

def main():
    root = tk.Tk()
    app = BaseSudokuApp(
        root=root,
        title="11 - Hill Climbing Search",
        subtitle="Nhóm 3: Local Search",
        algo_name="Hill Climbing",
        solver_class=HillClimbingSolver,
        num_clues=40
    )
    root.mainloop()

if __name__ == "__main__":
    main()
