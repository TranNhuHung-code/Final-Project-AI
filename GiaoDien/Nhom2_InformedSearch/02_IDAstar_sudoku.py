# -*- coding: utf-8 -*-
"""
02_IDAstar_sudoku.py
=====================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: INFORMED SEARCH (Tìm kiếm có thông tin)
Thuật toán trình bày: IDA* (Iterative Deepening A*)
Bài toán áp dụng: Giải Sudoku 9x9
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import tkinter as tk
from base_gui import BaseSudokuApp
from ThuatToan.Nhom2_InformedSearch.idastar_solver import IDAStarSolver

def main():
    root = tk.Tk()
    app = BaseSudokuApp(
        root=root,
        title="02 - Iterative Deepening A* (IDA*)",
        subtitle="Nhóm 2: Informed Search",
        algo_name="IDA*",
        solver_class=IDAStarSolver,
        num_clues=32
    )
    root.mainloop()

if __name__ == "__main__":
    main()
