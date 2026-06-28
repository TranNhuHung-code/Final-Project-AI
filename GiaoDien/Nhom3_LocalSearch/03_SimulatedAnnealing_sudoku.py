# -*- coding: utf-8 -*-
"""
03_SimulatedAnnealing_sudoku.py
================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: LOCAL SEARCH
Thuật toán trình bày: Simulated Annealing
Bài toán áp dụng: Giải Sudoku 9x9
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import tkinter as tk
from base_gui import BaseSudokuApp
from ThuatToan.Nhom3_LocalSearch.sa_solver import SimulatedAnnealingSolver

def main():
    root = tk.Tk()
    app = BaseSudokuApp(
        root=root,
        title="03 - Simulated Annealing",
        subtitle="Nhóm 3: Local Search",
        algo_name="Simulated Annealing",
        solver_class=SimulatedAnnealingSolver,
        num_clues=40
    )
    root.mainloop()

if __name__ == "__main__":
    main()
