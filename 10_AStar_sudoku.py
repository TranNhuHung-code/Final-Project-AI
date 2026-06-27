# -*- coding: utf-8 -*-
"""
10_AStar_sudoku.py
================
ĐỒ ÁN CUỐI KỲ - MÔN TRÍ TUỆ NHÂN TẠO
Nhóm thuật toán: INFORMED SEARCH
Thuật toán trình bày: A* Search
"""
import tkinter as tk
from base_gui import BaseSudokuApp
from astar_solver import AStarSolver

def main():
    root = tk.Tk()
    app = BaseSudokuApp(
        root=root,
        title="10 - A* Search",
        subtitle="Nhóm 2: Informed Search",
        algo_name="A*",
        solver_class=AStarSolver,
        num_clues=45
    )
    root.mainloop()

if __name__ == "__main__":
    main()
