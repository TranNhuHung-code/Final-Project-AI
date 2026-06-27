# -*- coding: utf-8 -*-
"""
05_ForwardChecking_sudoku.py
==============================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: CSP (Constraint Satisfaction Problem)
Thuật toán trình bày: Backtracking Search + Forward Checking (+ MRV)
Bài toán áp dụng: Giải Sudoku 9x9
"""

import tkinter as tk
from base_gui import BaseSudokuApp
from forward_checking_solver import ForwardCheckingSolver

def main():
    root = tk.Tk()
    app = BaseSudokuApp(
        root=root,
        title="14 - Forward Checking (CSP)",
        subtitle="Nhóm 5: Constraint Satisfaction Problem",
        algo_name="Forward Checking",
        solver_class=ForwardCheckingSolver,
        num_clues=26
    )
    root.mainloop()

if __name__ == "__main__":
    main()
