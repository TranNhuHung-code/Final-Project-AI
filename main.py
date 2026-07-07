# -*- coding: utf-8 -*-
"""
main.py - Giao dien chinh quan ly 18 thuat toan giai Sudoku.
Tab 1: Danh sach thuat toan chia 6 nhom, click de mo.
Tab 2: So sanh hieu nang 15 thuat toan tren cung 1 de.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys
import copy
import json
import time
import threading

# Thu muc goc cua project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Them vao sys.path de import duoc cac solver
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from sudoku_utils import generate_puzzle, SIZE, BOX

# ===================== MAU SAC =====================
BG = "#ECEEF3"           # xam xanh nhat - nhe mat
CARD_BG = "#FFFFFF"
CARD_HOVER = "#E8EDF5"   # hover xanh nhat
BORDER = "#C5CAD3"
TXT = "#1A1A2E"          # xanh den dam
TXT_SUB = "#4A4A68"
TXT_LIGHT = "#8888A0"
ACCENT = "#3D5A99"       # xanh duong dam
WHITE = "#FFFFFF"
HEADER_BG = "#2C3E6B"    # xanh dam cho header
HEADER_FG = "#FFFFFF"

# Mau cho o nhap de Sudoku
GRID_BG = "#FAFBFF"      # trang xanh nhat
GRID_CLUE = "#1A1A2E"    # so dam
GRID_EMPTY_FG = "#AAAACC"
GRID_CELL_BORDER = "#B0B8C8"   # vien mong giua cac o
GRID_BOX_BORDER = "#2C3E6B"    # vien dam 3x3 - xanh dam
GRID_SELECT = "#C5D5F0"        # o dang chon

# ===================== DU LIEU THUAT TOAN =====================
GROUPS = [
    {
        "name": "Nhom 1: Uninformed Search",
        "tag": "Tim kiem mu",
        "color": "#4A7CCC",
        "folder": "Nhom1_UninformedSearch",
        "algos": [
            ("BFS", "Breadth-First Search", "07_BFS_sudoku.py"),
            ("DFS", "Depth-First Search", "08_DFS_sudoku.py"),
            ("IDS", "Iterative Deepening Search", "01_IDS_sudoku.py"),
        ]
    },
    {
        "name": "Nhom 2: Informed Search",
        "tag": "Tim kiem co thong tin",
        "color": "#2E8B57",
        "folder": "Nhom2_InformedSearch",
        "algos": [
            ("Greedy", "Greedy Best-First Search", "09_Greedy_sudoku.py"),
            ("A*", "A* Search", "10_AStar_sudoku.py"),
            ("IDA*", "Iterative Deepening A*", "02_IDAstar_sudoku.py"),
        ]
    },
    {
        "name": "Nhom 3: Local Search",
        "tag": "Tim kiem cuc bo",
        "color": "#CC8833",
        "folder": "Nhom3_LocalSearch",
        "algos": [
            ("Hill Climbing", "Hill-Climbing Search", "11_HillClimbing_sudoku.py"),
            ("Local Beam", "Local Beam Search", "12_LocalBeam_sudoku.py"),
            ("Sim. Annealing", "Simulated Annealing", "03_SimulatedAnnealing_sudoku.py"),
        ]
    },
    {
        "name": "Nhom 4: Complex Environments",
        "tag": "Moi truong phuc tap",
        "color": "#CC5533",
        "folder": "Nhom4_ComplexSearch",
        "algos": [
            ("AND-OR", "AND-OR Search", "13_AndOr_sudoku.py"),
            ("Sensorless", "Sensorless Search", "14_Sensorless_sudoku.py"),
            ("Partial Obs.", "Partially Observable", "04_PartiallyObservable_sudoku.py"),
        ]
    },
    {
        "name": "Nhom 5: CSP",
        "tag": "Thoa man rang buoc",
        "color": "#7744AA",
        "folder": "Nhom5_CSP",
        "algos": [
            ("Backtracking", "Backtracking Search", "15_Backtracking_sudoku.py"),
            ("Fwd Checking", "Forward Checking", "05_ForwardChecking_sudoku.py"),
            ("Min-Conflicts", "Min-Conflicts", "16_MinConflicts_sudoku.py"),
        ]
    },
    {
        "name": "Nhom 6: Adversarial Search",
        "tag": "Tim kiem doi khang",
        "color": "#CC3333",
        "folder": "Nhom6_AdversarialSearch",
        "algos": [
            ("Minimax", "Minimax", "06_Minimax_SudokuBattle.py"),
            ("Alpha-Beta", "Alpha-Beta Pruning", "17_AlphaBeta_SudokuBattle.py"),
            ("Expectimax", "Expectimax", "18_Expectimax_SudokuBattle.py"),
        ]
    },
]

# Danh sach 15 solver de benchmark (khong co Nhom 6 - can tuong tac nguoi)
BENCHMARK_SOLVERS = [
    ("BFS",              "Nhom 1", "ThuatToan.Nhom1_UninformedSearch.bfs_solver",              "BFSSolver"),
    ("DFS",              "Nhom 1", "ThuatToan.Nhom1_UninformedSearch.dfs_solver",              "DFSSolver"),
    ("IDS",              "Nhom 1", "ThuatToan.Nhom1_UninformedSearch.ids_solver",              "IDSSolver"),
    ("Greedy",           "Nhom 2", "ThuatToan.Nhom2_InformedSearch.greedy_solver",             "GreedySolver"),
    ("A*",               "Nhom 2", "ThuatToan.Nhom2_InformedSearch.astar_solver",              "AStarSolver"),
    ("IDA*",             "Nhom 2", "ThuatToan.Nhom2_InformedSearch.idastar_solver",            "IDAStarSolver"),
    ("Hill Climbing",    "Nhom 3", "ThuatToan.Nhom3_LocalSearch.hill_climbing_solver",         "HillClimbingSolver"),
    ("Local Beam",       "Nhom 3", "ThuatToan.Nhom3_LocalSearch.local_beam_solver",            "LocalBeamSolver"),
    ("Sim. Annealing",   "Nhom 3", "ThuatToan.Nhom3_LocalSearch.sa_solver",                   "SimulatedAnnealingSolver"),
    ("AND-OR",           "Nhom 4", "ThuatToan.Nhom4_ComplexSearch.and_or_solver",              "AndOrSolver"),
    ("Sensorless",       "Nhom 4", "ThuatToan.Nhom4_ComplexSearch.sensorless_solver",          "SensorlessSolver"),
    ("Partial Obs.",     "Nhom 4", "ThuatToan.Nhom4_ComplexSearch.partial_observable_solver",   "PartiallyObservableSolver"),
    ("Backtracking",     "Nhom 5", "ThuatToan.Nhom5_CSP.backtracking_solver",                 "BacktrackingSolver"),
    ("Fwd Checking",     "Nhom 5", "ThuatToan.Nhom5_CSP.forward_checking_solver",             "ForwardCheckingSolver"),
    ("Min-Conflicts",    "Nhom 5", "ThuatToan.Nhom5_CSP.min_conflicts_solver",                "MinConflictsSolver"),
]

# File tam de chia se de giua main.py va cac cua so con
SHARED_PUZZLE_FILE = os.path.join(BASE_DIR, ".current_puzzle.json")


def save_shared_puzzle(puzzle):
    """Luu de hien tai ra file JSON de cac script con dung chung."""
    try:
        with open(SHARED_PUZZLE_FILE, "w") as f:
            json.dump(puzzle, f)
    except Exception:
        pass


# ===================== WIDGET PHU TRO =====================

class SudokuGrid(tk.Frame):
    """
    O nhap/hien thi de Sudoku 9x9.
    Vien dam 3px o khung 3x3, vien mong 1px giua cac o.
    """
    def __init__(self, parent, cell_size=36, editable=True, **kw):
        super().__init__(parent, bg=GRID_BOX_BORDER, bd=3, relief="solid", **kw)
        self.cell_size = cell_size
        self.editable = editable
        self.selected = None
        self.entries = [[None]*SIZE for _ in range(SIZE)]
        self._build()

    def _build(self):
        # Tao 9 khung 3x3 - moi khung co vien dam bao quanh
        self.box_frames = [[None]*3 for _ in range(3)]
        for br in range(3):
            for bc in range(3):
                # Frame ngoai tao vien dam giua cac box
                box = tk.Frame(self, bg=GRID_CELL_BORDER, bd=0)
                box.grid(row=br, column=bc,
                         padx=(2 if bc > 0 else 0, 0),
                         pady=(2 if br > 0 else 0, 0))
                self.box_frames[br][bc] = box

                for lr in range(3):
                    for lc in range(3):
                        r = br * 3 + lr
                        c = bc * 3 + lc
                        lbl = tk.Label(
                            box, text="", width=2, height=1,
                            font=("Segoe UI", 13, "bold"),
                            bg=GRID_BG, fg=GRID_CLUE,
                            relief="flat", bd=0,
                            cursor="hand2" if self.editable else "",
                        )
                        # Vien mong 1px giua cac o trong cung 1 box
                        lbl.grid(row=lr, column=lc,
                                 padx=(0, 1 if lc < 2 else 0),
                                 pady=(0, 1 if lr < 2 else 0),
                                 ipadx=5, ipady=3)
                        if self.editable:
                            lbl.bind("<Button-1>", lambda e, rr=r, cc=c: self._on_click(rr, cc))
                        self.entries[r][c] = lbl

        # Key binding
        if self.editable:
            self.winfo_toplevel().bind("<Key>", self._on_key, add=True)

    def _on_click(self, r, c):
        if not self.editable:
            return
        # Bo highlight cu
        if self.selected:
            pr, pc = self.selected
            self.entries[pr][pc].config(bg=GRID_BG)
        self.selected = (r, c)
        self.entries[r][c].config(bg=GRID_SELECT)

    def _on_key(self, event):
        if not self.editable or not self.selected:
            return
        r, c = self.selected
        if event.char in "123456789":
            self.entries[r][c].config(text=event.char, fg=GRID_CLUE)
        elif event.keysym in ("BackSpace", "Delete", "0"):
            self.entries[r][c].config(text="", fg=GRID_CLUE)

    def set_board(self, board):
        """Hien thi mot board 9x9 len grid."""
        for r in range(SIZE):
            for c in range(SIZE):
                val = board[r][c]
                if val != 0:
                    self.entries[r][c].config(text=str(val), fg=GRID_CLUE)
                else:
                    self.entries[r][c].config(text="", fg=GRID_EMPTY_FG)
        if self.selected:
            pr, pc = self.selected
            self.entries[pr][pc].config(bg=GRID_BG)
            self.selected = None

    def get_board(self):
        """Doc board 9x9 tu grid. O trong = 0."""
        board = [[0]*SIZE for _ in range(SIZE)]
        for r in range(SIZE):
            for c in range(SIZE):
                txt = self.entries[r][c].cget("text").strip()
                if txt.isdigit() and 1 <= int(txt) <= 9:
                    board[r][c] = int(txt)
        return board

    def clear(self):
        for r in range(SIZE):
            for c in range(SIZE):
                self.entries[r][c].config(text="", fg=GRID_EMPTY_FG, bg=GRID_BG)
        self.selected = None


# ===================== GIAO DIEN CHINH =====================

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver - Do An AI")
        self.root.geometry("1050x680")
        self.root.configure(bg=BG)
        self.root.minsize(950, 620)

        # De Sudoku hien tai (dung chung cho tab 1 va tab 2)
        self.current_puzzle = None
        self.current_difficulty = "Trung binh"
        self._generate_new_puzzle()

        # Trang thai benchmark
        self.is_benchmarking = False

        self._build_ui()
        self.root.eval('tk::PlaceWindow . center')

    def _generate_new_puzzle(self, num_clues=35):
        """Sinh de moi va luu ra file chia se."""
        diff_map = {"De": 45, "Trung binh": 35, "Kho": 25, "Cuc kho": 17}
        num = diff_map.get(self.current_difficulty, 35)
        self.current_puzzle, _ = generate_puzzle(num_clues=num)
        save_shared_puzzle(self.current_puzzle)

    def _build_ui(self):
        # Header - thanh tieu de xanh dam
        hdr = tk.Frame(self.root, bg=HEADER_BG)
        hdr.pack(fill=tk.X)

        hdr_inner = tk.Frame(hdr, bg=HEADER_BG)
        hdr_inner.pack(fill=tk.X, padx=30, pady=(12, 10))

        tk.Label(
            hdr_inner, text="Sudoku Solver",
            font=("Segoe UI", 17, "bold"), bg=HEADER_BG, fg=HEADER_FG
        ).pack(side=tk.LEFT)

        tk.Label(
            hdr_inner, text="Do An Cuoi Ky  |  Tri Tue Nhan Tao  |  18 Thuat Toan",
            font=("Segoe UI", 9), bg=HEADER_BG, fg="#A8B8D8"
        ).pack(side=tk.LEFT, padx=(16, 0), pady=(4, 0))

        # Notebook (2 tab)
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background="#D5DAE5", foreground=TXT,
                        padding=[16, 7], font=("Segoe UI", 10))
        style.map("TNotebook.Tab",
                  background=[("selected", WHITE)],
                  foreground=[("selected", ACCENT)])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Tab 1: Thuat toan
        self.tab_algos = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(self.tab_algos, text="  Thuat toan  ")
        self._build_tab_algos()

        # Tab 2: So sanh
        self.tab_compare = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(self.tab_compare, text="  So sanh  ")
        self._build_tab_compare()

    # =================== TAB 1: THUAT TOAN ===================

    def _build_tab_algos(self):
        container = tk.Frame(self.tab_algos, bg=BG)
        container.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)

        for i in range(3):
            container.columnconfigure(i, weight=1, uniform="col")
        container.rowconfigure(0, weight=1, uniform="row")
        container.rowconfigure(1, weight=1, uniform="row")

        for idx, grp in enumerate(GROUPS):
            row = idx // 3
            col = idx % 3
            self._make_group_card(container, grp, row, col)

    def _make_group_card(self, parent, grp, row, col):
        card = tk.Frame(parent, bg=CARD_BG, highlightbackground=BORDER,
                        highlightthickness=1, bd=0)
        card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

        # Tieu de nhom - co mau nen nhat
        color = grp["color"]
        # Tao mau nen nhat tu mau goc (them do sang)
        title_bar = tk.Frame(card, bg=color)
        title_bar.pack(fill=tk.X)

        tk.Label(
            title_bar, text=grp["name"],
            font=("Segoe UI", 10, "bold"), bg=color, fg="#FFFFFF",
            anchor="w"
        ).pack(side=tk.LEFT, padx=12, pady=(8, 2))

        tk.Label(
            title_bar, text=grp["tag"],
            font=("Segoe UI", 8), bg=color, fg="#DDDDEE",
            anchor="e"
        ).pack(side=tk.RIGHT, padx=12, pady=(8, 2))

        # Khoang cach sau header
        tk.Frame(card, bg=CARD_BG, height=6).pack()

        # Danh sach thuat toan
        for short, full, script in grp["algos"]:
            row_frame = tk.Frame(card, bg=CARD_BG, cursor="hand2")
            row_frame.pack(fill=tk.X, padx=4, pady=1)

            # Dau gach mau
            bar = tk.Frame(row_frame, bg=color, width=3)
            bar.pack(side=tk.LEFT, fill=tk.Y, padx=(6, 0), pady=3)

            lbl_name = tk.Label(
                row_frame, text=short,
                font=("Segoe UI", 9, "bold"), bg=CARD_BG, fg=TXT,
                width=13, anchor="w"
            )
            lbl_name.pack(side=tk.LEFT, padx=(6, 4), pady=5)

            lbl_full = tk.Label(
                row_frame, text=full,
                font=("Segoe UI", 9), bg=CARD_BG, fg=TXT_SUB,
                anchor="w"
            )
            lbl_full.pack(side=tk.LEFT, padx=(0, 6), pady=5)

            # Bind hover + click
            cmd = lambda f=grp["folder"], s=script: self._launch(f, s)
            all_widgets = [row_frame, lbl_name, lbl_full]
            for w in all_widgets:
                w.bind("<Enter>", lambda e, rf=row_frame, ln=lbl_name, lf=lbl_full:
                       self._row_hover(rf, ln, lf, True))
                w.bind("<Leave>", lambda e, rf=row_frame, ln=lbl_name, lf=lbl_full:
                       self._row_hover(rf, ln, lf, False))
                w.bind("<Button-1>", lambda e, c=cmd: c())

        # Padding duoi
        tk.Frame(card, bg=CARD_BG, height=6).pack()

    def _row_hover(self, frame, lbl1, lbl2, entering):
        bg = CARD_HOVER if entering else CARD_BG
        for w in [frame, lbl1, lbl2]:
            w.config(bg=bg)

    def _launch(self, folder, script):
        """Luu de hien tai va mo script con."""
        save_shared_puzzle(self.current_puzzle)
        script_path = os.path.join(BASE_DIR, "GiaoDien", folder, script)
        if not os.path.exists(script_path):
            messagebox.showerror("Loi", f"Khong tim thay:\n{script_path}")
            return
        try:
            subprocess.Popen([sys.executable, script_path], cwd=BASE_DIR)
        except Exception as e:
            messagebox.showerror("Loi", f"Khong mo duoc:\n{e}")

    # =================== TAB 2: SO SANH ===================

    def _build_tab_compare(self):
        main_frame = tk.Frame(self.tab_compare, bg=BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)

        # --- Phan trai: nhap de ---
        left = tk.Frame(main_frame, bg=BG)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 16))

        tk.Label(
            left, text="De Sudoku",
            font=("Segoe UI", 11, "bold"), bg=BG, fg=TXT
        ).pack(anchor="w", pady=(0, 6))

        # Chon do kho + sinh de
        ctrl = tk.Frame(left, bg=BG)
        ctrl.pack(fill=tk.X, pady=(0, 8))

        tk.Label(ctrl, text="Do kho:", font=("Segoe UI", 9), bg=BG, fg=TXT_SUB).pack(side=tk.LEFT)
        self.diff_var = tk.StringVar(value="Trung binh")
        combo = ttk.Combobox(ctrl, textvariable=self.diff_var,
                             values=["De", "Trung binh", "Kho", "Cuc kho"],
                             state="readonly", width=11)
        combo.pack(side=tk.LEFT, padx=6)

        tk.Button(
            ctrl, text="Sinh de moi", command=self._on_generate,
            font=("Segoe UI", 9), bg=CARD_BG, fg=TXT,
            relief="solid", bd=1, padx=8, pady=2, cursor="hand2"
        ).pack(side=tk.LEFT, padx=4)

        tk.Button(
            ctrl, text="Xoa", command=self._on_clear_grid,
            font=("Segoe UI", 9), bg=CARD_BG, fg=TXT_SUB,
            relief="solid", bd=1, padx=8, pady=2, cursor="hand2"
        ).pack(side=tk.LEFT, padx=2)

        # Grid nhap de
        self.puzzle_grid = SudokuGrid(left, cell_size=34, editable=True)
        self.puzzle_grid.pack(pady=(0, 10))
        self.puzzle_grid.set_board(self.current_puzzle)

        # Nut chay so sanh
        self.btn_run = tk.Button(
            left, text="Chay so sanh", command=self._on_run_benchmark,
            font=("Segoe UI", 10, "bold"), bg=HEADER_BG, fg=WHITE,
            relief="flat", padx=16, pady=6, cursor="hand2",
            activebackground="#1E2D50"
        )
        self.btn_run.pack(fill=tk.X, pady=(4, 6))

        # Trang thai
        self.status_label = tk.Label(
            left, text="San sang.", font=("Segoe UI", 8),
            bg=BG, fg=TXT_LIGHT, anchor="w"
        )
        self.status_label.pack(anchor="w")

        # Ghi chu
        tk.Label(
            left,
            text="Nhom 6 (Adversarial) khong ho tro\nso sanh tu dong vi can tuong tac.",
            font=("Segoe UI", 8), bg=BG, fg=TXT_LIGHT,
            justify="left"
        ).pack(anchor="w", pady=(8, 0))

        # --- Phan phai: bang ket qua ---
        right = tk.Frame(main_frame, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            right, text="Ket qua so sanh",
            font=("Segoe UI", 11, "bold"), bg=BG, fg=TXT
        ).pack(anchor="w", pady=(0, 6))

        # Hien thi de dang dung (text ngan gon)
        self.puzzle_info_label = tk.Label(
            right, text="", font=("Segoe UI", 8),
            bg=BG, fg=TXT_SUB, anchor="w", justify="left"
        )
        self.puzzle_info_label.pack(anchor="w", pady=(0, 6))
        self._update_puzzle_info()

        # Treeview bang ket qua
        tree_frame = tk.Frame(right, bg=BG)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("stt", "ten", "nhom", "nodes", "thoi_gian", "ket_qua")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=16)

        self.tree.heading("stt", text="#")
        self.tree.heading("ten", text="Thuat toan")
        self.tree.heading("nhom", text="Nhom")
        self.tree.heading("nodes", text="Nodes")
        self.tree.heading("thoi_gian", text="Thoi gian (s)")
        self.tree.heading("ket_qua", text="Ket qua")

        self.tree.column("stt", width=30, anchor="center", stretch=False)
        self.tree.column("ten", width=150, anchor="w")
        self.tree.column("nhom", width=70, anchor="center")
        self.tree.column("nodes", width=90, anchor="e")
        self.tree.column("thoi_gian", width=100, anchor="e")
        self.tree.column("ket_qua", width=100, anchor="center")

        # Style cho Treeview
        style = ttk.Style()
        style.configure("Treeview",
                        background=WHITE, foreground=TXT,
                        fieldbackground=WHITE,
                        font=("Segoe UI", 9),
                        rowheight=28)
        style.configure("Treeview.Heading",
                        background=HEADER_BG, foreground=HEADER_FG,
                        font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", GRID_SELECT)])

        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Tag mau cho ket qua
        self.tree.tag_configure("solved", foreground="#2E7D32")
        self.tree.tag_configure("failed", foreground="#C62828")
        self.tree.tag_configure("running", foreground="#CC8833")

    def _update_puzzle_info(self):
        """Cap nhat dong text hien thi de dang dung."""
        if self.current_puzzle is None:
            self.puzzle_info_label.config(text="Chua co de.")
            return
        # Dem so o da dien
        clues = sum(1 for r in range(SIZE) for c in range(SIZE) if self.current_puzzle[r][c] != 0)
        empties = SIZE * SIZE - clues
        self.puzzle_info_label.config(
            text=f"De hien tai: {clues} manh moi, {empties} o trong  |  Do kho: {self.current_difficulty}"
        )

    def _on_generate(self):
        if self.is_benchmarking:
            return
        self.current_difficulty = self.diff_var.get()
        self._generate_new_puzzle()
        self.puzzle_grid.set_board(self.current_puzzle)
        self._update_puzzle_info()
        # Xoa ket qua cu
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.status_label.config(text="Da sinh de moi.")

    def _on_clear_grid(self):
        if self.is_benchmarking:
            return
        self.puzzle_grid.clear()
        self.current_puzzle = [[0]*SIZE for _ in range(SIZE)]
        save_shared_puzzle(self.current_puzzle)
        self._update_puzzle_info()

    def _on_run_benchmark(self):
        if self.is_benchmarking:
            return

        # Doc de tu grid (nguoi dung co the da sua tay)
        self.current_puzzle = self.puzzle_grid.get_board()
        save_shared_puzzle(self.current_puzzle)
        self._update_puzzle_info()

        # Kiem tra de co hop le khong (it nhat 1 o da dien)
        clues = sum(1 for r in range(SIZE) for c in range(SIZE) if self.current_puzzle[r][c] != 0)
        if clues == 0:
            messagebox.showwarning("Thieu de", "Ban chua nhap de Sudoku nao.")
            return

        self.is_benchmarking = True
        self.btn_run.config(state="disabled", text="Dang chay...")

        # Xoa ket qua cu
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Chen dong "dang chay" cho tung thuat toan
        self.result_ids = []
        for i, (name, group, _, _) in enumerate(BENCHMARK_SOLVERS):
            iid = self.tree.insert("", "end", values=(i+1, name, group, "-", "-", "Cho..."),
                                   tags=("running",))
            self.result_ids.append(iid)

        # Chay benchmark trong thread rieng
        thread = threading.Thread(target=self._run_all_solvers, daemon=True)
        thread.start()

    def _run_all_solvers(self):
        """Chay tung solver, cap nhat ket qua len UI."""
        puzzle = copy.deepcopy(self.current_puzzle)
        timeout = 30  # giay

        for i, (name, group, module_path, class_name) in enumerate(BENCHMARK_SOLVERS):
            iid = self.result_ids[i]

            # Cap nhat trang thai "Dang chay..."
            self.root.after(0, lambda ii=iid, nm=name:
                            self._update_row(ii, nodes="-", time_s="-", result="Dang chay..."))
            self.root.after(0, lambda nm=name:
                            self.status_label.config(text=f"Dang chay: {nm}..."))

            try:
                # Import dong solver class
                mod = __import__(module_path, fromlist=[class_name])
                solver_cls = getattr(mod, class_name)
                solver = solver_cls(copy.deepcopy(puzzle))

                t0 = time.time()

                # Chay solver voi timeout
                result_container = [None, None, None]
                def run_solver():
                    try:
                        sol, steps, stats = solver.solve()
                        result_container[0] = sol
                        result_container[1] = steps
                        result_container[2] = stats
                    except Exception:
                        pass

                t = threading.Thread(target=run_solver, daemon=True)
                t.start()
                t.join(timeout=timeout)

                elapsed = round(time.time() - t0, 3)

                if t.is_alive():
                    # Timeout
                    self.root.after(0, lambda ii=iid:
                                    self._update_row(ii, nodes="?", time_s=f">{timeout}", result="Timeout", tag="failed"))
                elif result_container[0] is not None:
                    stats = result_container[2] or {}
                    nodes = stats.get('nodes_expanded', stats.get('nodes', '-'))
                    if isinstance(nodes, int):
                        nodes = f"{nodes:,}"
                    self.root.after(0, lambda ii=iid, n=nodes, e=elapsed:
                                    self._update_row(ii, nodes=n, time_s=str(e), result="Giai duoc", tag="solved"))
                else:
                    stats = result_container[2] or {}
                    nodes = stats.get('nodes_expanded', stats.get('nodes', '-'))
                    if isinstance(nodes, int):
                        nodes = f"{nodes:,}"
                    self.root.after(0, lambda ii=iid, n=nodes, e=elapsed:
                                    self._update_row(ii, nodes=n, time_s=str(e), result="Khong giai duoc", tag="failed"))

            except Exception as e:
                self.root.after(0, lambda ii=iid, err=str(e):
                                self._update_row(ii, nodes="-", time_s="-", result=f"Loi: {err[:30]}", tag="failed"))

        # Hoan tat
        self.root.after(0, self._benchmark_done)

    def _update_row(self, iid, nodes, time_s, result, tag=None):
        """Cap nhat 1 dong trong Treeview."""
        vals = list(self.tree.item(iid, "values"))
        vals[3] = nodes
        vals[4] = time_s
        vals[5] = result
        self.tree.item(iid, values=vals, tags=(tag,) if tag else ())

    def _benchmark_done(self):
        self.is_benchmarking = False
        self.btn_run.config(state="normal", text="Chay so sanh")
        self.status_label.config(text="Hoan tat.")


# ===================== MAIN =====================

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
