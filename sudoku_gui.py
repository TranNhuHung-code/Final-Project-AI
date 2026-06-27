import pygame
import sys
import os
import time
import math
import random
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from search_algorithms.core.sudoku import (
    SudokuProblem, SudokuHelper,
    VERY_EASY_BOARD, EASY_BOARD, MEDIUM_BOARD, HARD_BOARD, SOLUTION,
)

pygame.init()
pygame.font.init()

W, H = 1440, 860
FPS = 60

FN = 'segoeui'
F_TITLE = pygame.font.SysFont(FN, 38, True)
F_HEAD = pygame.font.SysFont(FN, 30, True)
F_SUB = pygame.font.SysFont(FN, 22, True)
F_BODY = pygame.font.SysFont(FN, 17)
F_SM = pygame.font.SysFont(FN, 14)
F_XS = pygame.font.SysFont(FN, 12)
F_CELL = pygame.font.SysFont(FN, 28, True)
F_CELL_SM = pygame.font.SysFont(FN, 11)
F_LOG = pygame.font.SysFont('consolas', 13)
F_BTN = pygame.font.SysFont(FN, 15, True)
F_NUM = pygame.font.SysFont(FN, 44, True)

BG = (8, 8, 22)
BG2 = (14, 14, 32)
CARD = (20, 22, 48)
CARD_H = (30, 32, 62)
PANEL = (16, 18, 40)
TAB_BG = (26, 28, 56)
TAB_ACT = (38, 40, 78)
ACCENT = (0, 198, 255)
TXT = (215, 218, 232)
TXT_D = (100, 105, 135)
TXT_B = (255, 255, 255)
GRID = (40, 42, 72)
GRID_T = (65, 68, 105)
C_GIVEN = (195, 198, 218)
C_PLACED = (0, 210, 255)
C_BT = (255, 50, 90)
SUC = (0, 228, 115)
ERR = (255, 50, 90)
WARN = (255, 190, 0)
INFO = (0, 185, 255)
MINT = (0, 255, 168)
GOLD = (255, 215, 0)

GC = {
    1: (41, 128, 255),
    2: (0, 200, 83),
    3: (255, 145, 0),
    4: (156, 39, 176),
    5: (244, 67, 54),
    6: (0, 188, 212),
}

GROUPS_DATA = [
    {
        'id': 1, 'name': 'Uninformed Search',
        'vn': 'Tim kiem khong co thong tin',
        'desc': 'BFS, DFS, IDS\nKhong su dung heuristic',
        'board': VERY_EASY_BOARD, 'diff': 'Very Easy (8 o trong)',
        'algos': [
            {'id': 'bfs', 'name': 'BFS', 'full': 'Breadth-First Search',
             'desc': 'Frontier: Queue (FIFO)\nDuyet theo chieu rong'},
            {'id': 'dfs', 'name': 'DFS', 'full': 'Depth-First Search',
             'desc': 'Frontier: Stack (LIFO)\nQuay lui khi gap ngo cut'},
            {'id': 'ids', 'name': 'IDS', 'full': 'Iterative Deepening',
             'desc': 'DFS lap lai voi depth tang dan\nKet hop uu diem BFS + DFS'},
        ],
    },
    {
        'id': 2, 'name': 'Informed Search',
        'vn': 'Tim kiem co thong tin',
        'desc': 'Greedy, A*, IDA*\nSu dung heuristic h(n)',
        'board': EASY_BOARD, 'diff': 'Easy (15 o trong)',
        'algos': [
            {'id': 'greedy', 'name': 'Greedy', 'full': 'Greedy Best-First',
             'desc': 'Uu tien h(n) nho nhat\nNhanh nhung khong optimal'},
            {'id': 'astar', 'name': 'A*', 'full': 'A* Search',
             'desc': 'f(n) = g(n) + h(n)\nOptimal + admissible'},
            {'id': 'ida_star', 'name': 'IDA*', 'full': 'IDA* Search',
             'desc': 'IDS + A*\nBo nho O(bd) nhu DFS'},
        ],
    },
    {
        'id': 3, 'name': 'Local Search',
        'vn': 'Tim kiem cuc bo',
        'desc': 'Hill Climbing, Beam, SA\nSwap trong khoi 3x3',
        'board': MEDIUM_BOARD, 'diff': 'Medium (25 o trong)',
        'algos': [
            {'id': 'hill_climbing', 'name': 'Hill Climbing', 'full': 'Steepest-Ascent Hill Climbing',
             'desc': 'Chon neighbor tot nhat\nRestart khi bi ket'},
            {'id': 'beam_search', 'name': 'Beam Search', 'full': 'Local Beam Search (k=5)',
             'desc': 'Duy tri k trang thai\nChia se thong tin'},
            {'id': 'sa', 'name': 'Sim. Annealing', 'full': 'Simulated Annealing',
             'desc': 'Chap nhan xau hon voi\nxac suat giam theo nhiet do'},
        ],
    },
    {
        'id': 4, 'name': 'Complex Environments',
        'vn': 'Moi truong phuc tap',
        'desc': 'AND-OR, Sensorless,\nPartial Observable',
        'board': EASY_BOARD, 'diff': 'Easy (15 o trong)',
        'algos': [
            {'id': 'and_or', 'name': 'AND-OR', 'full': 'AND-OR Search',
             'desc': 'OR = chon gia tri\nAND = tat ca o con lai'},
            {'id': 'sensorless', 'name': 'Sensorless', 'full': 'Sensorless (Conformant)',
             'desc': 'Belief state\nPlan cho moi kha nang'},
            {'id': 'partial_obs', 'name': 'Partial Obs.', 'full': 'Partially Observable',
             'desc': 'Quan sat mot phan\nCap nhat belief state'},
        ],
    },
    {
        'id': 5, 'name': 'CSP',
        'vn': 'Rang buoc (CSP)',
        'desc': 'Backtracking, Forward Check,\nMin-Conflicts',
        'board': HARD_BOARD, 'diff': 'Hard (45 o trong)',
        'algos': [
            {'id': 'backtracking', 'name': 'Backtracking', 'full': 'Backtracking Search',
             'desc': 'DFS + kiem tra rang buoc\nMRV heuristic'},
            {'id': 'forward_checking', 'name': 'Forward Check', 'full': 'Forward Checking',
             'desc': 'Backtracking + domain update\nPhat hien som mau thuan'},
            {'id': 'min_conflicts', 'name': 'Min-Conflicts', 'full': 'Min-Conflicts',
             'desc': 'Local search tren CSP\nGiam xung dot toi thieu'},
        ],
    },
    {
        'id': 6, 'name': 'Adversarial Search',
        'vn': 'Tim kiem doi khang',
        'desc': 'Minimax, Alpha-Beta,\nExpectimax',
        'board': VERY_EASY_BOARD, 'diff': 'Very Easy (8 o trong)',
        'algos': [
            {'id': 'minimax', 'name': 'Minimax', 'full': 'Minimax',
             'desc': 'MAX chon tot nhat\nMIN chon xau nhat'},
            {'id': 'alpha_beta', 'name': 'Alpha-Beta', 'full': 'Alpha-Beta Pruning',
             'desc': 'Minimax + cat tia\nalpha >= beta -> cat'},
            {'id': 'expectimax', 'name': 'Expectimax', 'full': 'Expectimax',
             'desc': 'MAX + CHANCE node\nDoi thu ngau nhien'},
        ],
    },
]

ALGO_NAMES = {}
ALGO_GROUP = {}
for g in GROUPS_DATA:
    for a in g['algos']:
        ALGO_NAMES[a['id']] = a['full']
        ALGO_GROUP[a['id']] = g['id']

ALGO_REG = {
    'bfs':       ('search_algorithms.group1_uninformed', 'bfs', 'tree'),
    'dfs':       ('search_algorithms.group1_uninformed', 'dfs', 'tree'),
    'ids':       ('search_algorithms.group1_uninformed', 'ids', 'tree'),
    'greedy':    ('search_algorithms.group2_informed', 'greedy_best_first', 'tree'),
    'astar':     ('search_algorithms.group2_informed', 'astar', 'tree'),
    'ida_star':  ('search_algorithms.group2_informed', 'ida_star', 'tree'),
    'hill_climbing': ('search_algorithms.group3_local', 'hill_climbing', 'local'),
    'beam_search':   ('search_algorithms.group3_local', 'local_beam_search', 'beam'),
    'sa':            ('search_algorithms.group3_local', 'simulated_annealing', 'local'),
    'and_or':        ('search_algorithms.group4_complex', 'and_or_search', 'dict'),
    'sensorless':    ('search_algorithms.group4_complex', 'sensorless_search', 'dict'),
    'partial_obs':   ('search_algorithms.group4_complex', 'partial_observable_search', 'dict'),
    'backtracking':      ('search_algorithms.group5_csp', 'backtracking_search', 'dict'),
    'forward_checking':  ('search_algorithms.group5_csp', 'forward_checking', 'dict'),
    'min_conflicts':     ('search_algorithms.group5_csp', 'min_conflicts', 'dict'),
    'minimax':     ('search_algorithms.group6_adversarial', 'minimax', 'adv'),
    'alpha_beta':  ('search_algorithms.group6_adversarial', 'alpha_beta', 'adv'),
    'expectimax':  ('search_algorithms.group6_adversarial', 'expectimax', 'adv'),
}

BT_ALGOS = {
    'dfs': 'Depth-First Search',
    'ids': 'Iterative Deepening',
    'ida_star': 'IDA*',
    'and_or': 'AND-OR Search',
    'sensorless': 'Sensorless Search',
    'partial_obs': 'Partial Observable',
    'backtracking': 'Backtracking (CSP)',
    'forward_checking': 'Forward Checking',
}


def blend(c1, c2, t):
    t = max(0, min(1, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def ease_out(t):
    return 1 - (1 - t) ** 3


def run_algorithm(board_tuple, algo_id):
    mod_path, func_name, atype = ALGO_REG[algo_id]
    mod = __import__(mod_path, fromlist=[func_name])
    func = getattr(mod, func_name)
    if atype == 'tree':
        problem = SudokuProblem(board_tuple)
        r = func(problem)
        return {
            'found': r.found,
            'board': r.solution.state if r.found else board_tuple,
            'nodes_explored': r.nodes_expanded,
            'frontier': r.max_frontier_size,
            'path_length': r.path_length if r.found else 0,
        }
    elif atype == 'local':
        return func(board_tuple)
    elif atype == 'beam':
        return func(board_tuple, k=5)
    elif atype == 'dict':
        return func(board_tuple)
    elif atype == 'adv':
        return func(board_tuple, max_depth=4)
    return {'found': False}


def record_backtrack_steps(board_tuple, algo_name, use_fc=False, max_steps=2000):
    board = list(board_tuple)
    given = set(i for i in range(81) if board_tuple[i] != 0)
    empty = SudokuHelper.get_empty_cells(board_tuple)
    empty.sort(key=lambda rc: len(SudokuHelper.get_valid_values(board_tuple, rc[0], rc[1])))

    steps = []
    stats = {'nodes': 0, 'bt': 0}
    found = [False]

    steps.append({'type': 'info', 'row': -1, 'col': -1, 'value': 0,
                  'board': board_tuple,
                  'msg': f'{algo_name}: {len(empty)} o trong'})

    def solve(idx):
        if found[0] or len(steps) >= max_steps:
            return
        if idx >= len(empty):
            found[0] = True
            steps.append({'type': 'success', 'row': -1, 'col': -1, 'value': 0,
                         'board': tuple(board),
                         'msg': f'Tim thay! Nodes: {stats["nodes"]}, Backtracks: {stats["bt"]}'})
            return

        r, c = empty[idx]
        valid = SudokuHelper.get_valid_values(tuple(board), r, c)
        stats['nodes'] += 1

        if not valid:
            steps.append({'type': 'info', 'row': r, 'col': c, 'value': 0,
                         'board': tuple(board),
                         'msg': f'R{r+1}C{c+1}: Dead-end!'})
            return

        for v in valid:
            board[r * 9 + c] = v
            steps.append({'type': 'place', 'row': r, 'col': c, 'value': v,
                         'board': tuple(board),
                         'msg': f'R{r+1}C{c+1} = {v}'})

            if use_fc:
                wipeout = False
                for pr, pc in SudokuHelper.get_peers(r, c):
                    if board[pr * 9 + pc] == 0:
                        if not SudokuHelper.get_valid_values(tuple(board), pr, pc):
                            wipeout = True
                            steps.append({'type': 'info', 'row': pr, 'col': pc, 'value': 0,
                                         'board': tuple(board),
                                         'msg': f'Domain wipeout R{pr+1}C{pc+1}!'})
                            break
                if wipeout:
                    board[r * 9 + c] = 0
                    stats['bt'] += 1
                    steps.append({'type': 'backtrack', 'row': r, 'col': c, 'value': v,
                                 'board': tuple(board),
                                 'msg': f'R{r+1}C{c+1} = {v} QUAY LUI (FC)'})
                    continue

            solve(idx + 1)
            if found[0]:
                return

            board[r * 9 + c] = 0
            stats['bt'] += 1
            steps.append({'type': 'backtrack', 'row': r, 'col': c, 'value': v,
                         'board': tuple(board),
                         'msg': f'R{r+1}C{c+1} = {v} QUAY LUI'})

    solve(0)
    if not found[0] and len(steps) < max_steps:
        steps.append({'type': 'fail', 'row': -1, 'col': -1, 'value': 0,
                     'msg': 'Khong tim thay loi giai!', 'board': board_tuple})
    return steps


def record_forward_steps(board_tuple, algo_id):
    steps = []
    name = ALGO_NAMES.get(algo_id, algo_id)
    steps.append({'type': 'info', 'row': -1, 'col': -1, 'value': 0,
                  'board': board_tuple, 'msg': f'{name}: Dang chay...'})

    t0 = time.time()
    try:
        result = run_algorithm(board_tuple, algo_id)
    except Exception as e:
        steps.append({'type': 'fail', 'row': -1, 'col': -1, 'value': 0,
                     'board': board_tuple, 'msg': f'Loi: {e}'})
        return steps
    elapsed = time.time() - t0

    fnd = result.get('found', False)
    sol = result.get('board', board_tuple)
    if isinstance(sol, list):
        sol = tuple(sol)

    if fnd and sol:
        current = list(board_tuple)
        for i in range(81):
            if board_tuple[i] == 0 and sol[i] != 0:
                r, c = i // 9, i % 9
                v = sol[i]
                current[r * 9 + c] = v
                steps.append({'type': 'place', 'row': r, 'col': c, 'value': v,
                             'board': tuple(current), 'msg': f'R{r+1}C{c+1} = {v}'})

        parts = [f'Tim thay loi giai! Time: {elapsed:.4f}s']
        nd = result.get('nodes_explored', result.get('nodes', None))
        if nd is not None:
            parts.append(f'Nodes: {nd}')
        bt = result.get('backtracks', result.get('bt', None))
        if bt is not None:
            parts.append(f'Backtracks: {bt}')
        st = result.get('steps', None)
        if st is not None:
            parts.append(f'Steps: {st}')
        fr = result.get('frontier', result.get('max_frontier_size', None))
        if fr is not None:
            parts.append(f'Frontier: {fr}')
        pr = result.get('pruned', None)
        if pr is not None:
            parts.append(f'Pruned: {pr}')

        steps.append({'type': 'success', 'row': -1, 'col': -1, 'value': 0,
                     'board': sol, 'msg': ' | '.join(parts)})
    else:
        msg = f'Khong tim thay. Time: {elapsed:.4f}s'
        cost = result.get('cost', result.get('conflicts_remaining', None))
        if cost is not None:
            msg += f' | Cost: {cost}'
        steps.append({'type': 'fail', 'row': -1, 'col': -1, 'value': 0,
                     'board': board_tuple, 'msg': msg})
    return steps


def get_steps(board_tuple, algo_id):
    if algo_id in BT_ALGOS:
        fc = algo_id == 'forward_checking'
        return record_backtrack_steps(board_tuple, BT_ALGOS[algo_id], use_fc=fc)
    return record_forward_steps(board_tuple, algo_id)


SAMPLE_BOARDS = [
    ('Very Easy', VERY_EASY_BOARD),
    ('Easy', EASY_BOARD),
    ('Medium', MEDIUM_BOARD),
    ('Hard', HARD_BOARD),
]

ALL_ALGOS_FLAT = []
for g in GROUPS_DATA:
    for a in g['algos']:
        ALL_ALGOS_FLAT.append((g['id'], a['id'], a['name'], a['full']))


class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("18 AI Search Algorithms — Sudoku Solver")
        self.clock = pygame.time.Clock()
        self.running = True

        self.bg_surf = pygame.Surface((W, H))
        for y in range(H):
            t = y / H
            r = int(8 + t * 10)
            g = int(8 + t * 10)
            b = int(22 + t * 14)
            pygame.draw.line(self.bg_surf, (r, g, b), (0, y), (W, y))

        self.state = 'home'
        self.sel_group = None
        self.sel_algo = None
        self.sel_board = None

        self.steps = []
        self.step_idx = 0
        self.anim_running = False
        self.anim_done = False
        self.anim_paused = False
        self.speed = 15
        self.last_step_t = 0
        self.board_state = None
        self.given_cells = set()
        self.cell_anims = {}
        self.log_entries = []
        self.log_scroll = 0
        self.stats_data = {}

        self.active_tab = 0
        self.edit_mode = False
        self.edit_board = list(VERY_EASY_BOARD)
        self.edit_selected = None
        self.edit_algo_idx = 0
        self.edit_result_log = []

        self.slider_drag = False
        self.hover_cards = {}
        self.transition_alpha = 0
        self.transition_target = None

    def run(self):
        while self.running:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    self.running = False
                    break
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    if self.state == 'solve':
                        self.state = 'group'
                        self._reset_solve()
                    elif self.state == 'group':
                        self.state = 'home'
                    else:
                        self.running = False

            if not self.running:
                break

            self.screen.blit(self.bg_surf, (0, 0))

            if self.state == 'home':
                self._draw_home(events)
            elif self.state == 'group':
                self._draw_group(events)
            elif self.state == 'solve':
                self._draw_solve(events)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def _reset_solve(self):
        self.steps = []
        self.step_idx = 0
        self.anim_running = False
        self.anim_done = False
        self.anim_paused = False
        self.board_state = None
        self.cell_anims = {}
        self.log_entries = []
        self.log_scroll = 0
        self.stats_data = {}
        self.active_tab = 0
        self.edit_mode = False
        self.edit_selected = None
        self.edit_result_log = []

    def _draw_home(self, events):
        mouse = pygame.mouse.get_pos()
        click = any(e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 for e in events)

        title = F_TITLE.render("18 AI SEARCH ALGORITHMS", True, TXT_B)
        sub = F_SUB.render("Sudoku Solver — Final Project AI", True, ACCENT)
        self.screen.blit(title, (W // 2 - title.get_width() // 2, 28))
        self.screen.blit(sub, (W // 2 - sub.get_width() // 2, 72))

        line_y = 108
        pygame.draw.line(self.screen, blend(ACCENT, BG, 0.6), (80, line_y), (W - 80, line_y), 1)

        card_w = 400
        card_h = 290
        gap_x = 40
        gap_y = 30
        start_x = (W - 3 * card_w - 2 * gap_x) // 2
        start_y = 130

        for i, grp in enumerate(GROUPS_DATA):
            col = i % 3
            row = i // 3
            x = start_x + col * (card_w + gap_x)
            y = start_y + row * (card_h + gap_y)
            rect = pygame.Rect(x, y, card_w, card_h)
            hovered = rect.collidepoint(mouse)

            if hovered and click:
                self.sel_group = grp
                self.state = 'group'

            gc = GC[grp['id']]
            bg_c = CARD_H if hovered else CARD
            pygame.draw.rect(self.screen, bg_c, rect, border_radius=14)

            accent_rect = pygame.Rect(x, y, 6, card_h)
            pygame.draw.rect(self.screen, gc, accent_rect, border_radius=3)

            if hovered:
                glow = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                pygame.draw.rect(glow, (*gc, 30), (0, 0, card_w, card_h), border_radius=14)
                self.screen.blit(glow, (x, y))
                pygame.draw.rect(self.screen, gc, rect, 2, border_radius=14)

            num_surf = F_NUM.render(f"0{grp['id']}", True, blend(gc, BG, 0.3))
            self.screen.blit(num_surf, (x + card_w - num_surf.get_width() - 18, y + 12))

            name = F_HEAD.render(grp['name'], True, TXT_B)
            self.screen.blit(name, (x + 22, y + 20))

            vn = F_BODY.render(grp['vn'], True, gc)
            self.screen.blit(vn, (x + 22, y + 56))

            desc_lines = grp['desc'].split('\n')
            for j, line in enumerate(desc_lines):
                dt = F_SM.render(line, True, TXT_D)
                self.screen.blit(dt, (x + 22, y + 86 + j * 20))

            pygame.draw.line(self.screen, blend(gc, CARD, 0.5), (x + 22, y + 140), (x + card_w - 22, y + 140), 1)

            for k, algo in enumerate(grp['algos']):
                ay = y + 155 + k * 42
                badge = pygame.Rect(x + 22, ay, 80, 28)
                pygame.draw.rect(self.screen, blend(gc, BG, 0.6), badge, border_radius=6)
                nt = F_BTN.render(algo['name'], True, gc)
                self.screen.blit(nt, nt.get_rect(center=badge.center))
                ft = F_SM.render(algo['full'], True, TXT_D)
                self.screen.blit(ft, (x + 112, ay + 6))

            diff_t = F_XS.render(grp['diff'], True, blend(gc, TXT_D, 0.5))
            self.screen.blit(diff_t, (x + 22, y + card_h - 24))

        foot = F_XS.render("Click vao nhom de xem chi tiet  |  ESC = quay lai", True, TXT_D)
        self.screen.blit(foot, (W // 2 - foot.get_width() // 2, H - 28))

    def _draw_group(self, events):
        if not self.sel_group:
            self.state = 'home'
            return

        mouse = pygame.mouse.get_pos()
        click = any(e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 for e in events)
        grp = self.sel_group
        gc = GC[grp['id']]

        back_rect = pygame.Rect(30, 20, 100, 36)
        bh = back_rect.collidepoint(mouse)
        pygame.draw.rect(self.screen, CARD_H if bh else CARD, back_rect, border_radius=8)
        bt = F_BTN.render("<  Quay lai", True, TXT if bh else TXT_D)
        self.screen.blit(bt, bt.get_rect(center=back_rect.center))
        if bh and click:
            self.state = 'home'
            return

        gnum = F_NUM.render(f"0{grp['id']}", True, blend(gc, BG, 0.4))
        self.screen.blit(gnum, (W - gnum.get_width() - 40, 15))

        gname = F_TITLE.render(grp['name'], True, TXT_B)
        self.screen.blit(gname, (160, 18))
        gvn = F_BODY.render(grp['vn'], True, gc)
        self.screen.blit(gvn, (160, 60))

        pygame.draw.line(self.screen, blend(gc, BG, 0.5), (40, 95), (W - 40, 95), 1)

        board_y = 115
        board_label = F_SM.render(f"Board: {grp['diff']}", True, TXT_D)
        self.screen.blit(board_label, (50, board_y))
        self._draw_mini_board(50, board_y + 22, grp['board'], 28)

        card_w = 380
        card_h = 440
        gap = 30
        total_w = 3 * card_w + 2 * gap
        sx = (W - total_w) // 2
        sy = 120

        for i, algo in enumerate(grp['algos']):
            x = sx + i * (card_w + gap)
            y = sy
            rect = pygame.Rect(x, y, card_w, card_h)
            hovered = rect.collidepoint(mouse)

            bg_c = CARD_H if hovered else CARD
            pygame.draw.rect(self.screen, bg_c, rect, border_radius=14)

            if hovered:
                glow = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                pygame.draw.rect(glow, (*gc, 25), (0, 0, card_w, card_h), border_radius=14)
                self.screen.blit(glow, (x, y))
                pygame.draw.rect(self.screen, gc, rect, 2, border_radius=14)

            idx_t = F_NUM.render(str(grp['id'] * 3 - 2 + i), True, blend(gc, BG, 0.25))
            self.screen.blit(idx_t, (x + card_w - idx_t.get_width() - 16, y + 10))

            nt = F_HEAD.render(algo['name'], True, TXT_B)
            self.screen.blit(nt, (x + 24, y + 20))
            ft = F_BODY.render(algo['full'], True, gc)
            self.screen.blit(ft, (x + 24, y + 58))

            pygame.draw.line(self.screen, blend(gc, CARD, 0.4), (x + 24, y + 88), (x + card_w - 24, y + 88), 1)

            desc_lines = algo['desc'].split('\n')
            for j, line in enumerate(desc_lines):
                dt = F_SM.render(line, True, TXT_D)
                self.screen.blit(dt, (x + 24, y + 100 + j * 22))

            self._draw_mini_board(x + 24, y + 160, grp['board'], 22)

            run_rect = pygame.Rect(x + 24, y + card_h - 60, card_w - 48, 42)
            rh = run_rect.collidepoint(mouse)
            rc = gc if rh else blend(gc, CARD, 0.4)
            pygame.draw.rect(self.screen, rc, run_rect, border_radius=10)
            if rh:
                pygame.draw.rect(self.screen, gc, run_rect, 2, border_radius=10)
            rt = F_SUB.render("RUN", True, TXT_B if rh else TXT)
            self.screen.blit(rt, rt.get_rect(center=run_rect.center))

            if rh and click:
                self.sel_algo = algo
                self.sel_board = grp['board']
                self._start_solve(algo['id'], grp['board'])
                self.state = 'solve'

        foot = F_XS.render("Click RUN de chay thuat toan  |  ESC = quay lai", True, TXT_D)
        self.screen.blit(foot, (W // 2 - foot.get_width() // 2, H - 28))

    def _start_solve(self, algo_id, board):
        self._reset_solve()
        self.board_state = list(board)
        self.given_cells = set(i for i in range(81) if board[i] != 0)
        self.anim_running = True
        self.last_step_t = time.time()

        def worker():
            try:
                self.steps = get_steps(board, algo_id)
            except Exception as e:
                self.steps = [{'type': 'fail', 'msg': f'Loi: {e}', 'board': board}]
            self.anim_running = False

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _draw_solve(self, events):
        if not self.sel_algo:
            self.state = 'group'
            return

        mouse = pygame.mouse.get_pos()
        click = any(e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 for e in events)
        grp = self.sel_group
        gc = GC[grp['id']]

        back_rect = pygame.Rect(15, 12, 80, 32)
        bh = back_rect.collidepoint(mouse)
        pygame.draw.rect(self.screen, CARD_H if bh else CARD, back_rect, border_radius=8)
        bt = F_BTN.render("< Back", True, TXT if bh else TXT_D)
        self.screen.blit(bt, bt.get_rect(center=back_rect.center))
        if bh and click:
            self.state = 'group'
            self._reset_solve()
            return

        algo_name = self.sel_algo['full']
        nt = F_HEAD.render(algo_name, True, TXT_B)
        self.screen.blit(nt, (110, 10))
        gt = F_SM.render(f"Nhom {grp['id']}: {grp['name']}", True, gc)
        self.screen.blit(gt, (110, 44))

        self._draw_speed_control(events, mouse, click)

        pause_rect = pygame.Rect(880, 14, 90, 30)
        ph = pause_rect.collidepoint(mouse)
        pygame.draw.rect(self.screen, CARD_H if ph else CARD, pause_rect, border_radius=8)
        ptxt = "Tiep tuc" if self.anim_paused else "Tam dung"
        pt = F_BTN.render(ptxt, True, WARN if self.anim_paused else TXT)
        self.screen.blit(pt, pt.get_rect(center=pause_rect.center))
        if ph and click:
            self.anim_paused = not self.anim_paused

        reset_rect = pygame.Rect(980, 14, 70, 30)
        rh = reset_rect.collidepoint(mouse)
        pygame.draw.rect(self.screen, CARD_H if rh else CARD, reset_rect, border_radius=8)
        rt = F_BTN.render("Reset", True, ERR if rh else TXT_D)
        self.screen.blit(rt, rt.get_rect(center=reset_rect.center))
        if rh and click:
            self._start_solve(self.sel_algo['id'], self.sel_board)

        pygame.draw.line(self.screen, blend(gc, BG, 0.5), (15, 58), (W - 15, 58), 1)

        self._update_animation()

        BX, BY = 30, 72
        CS = 52
        if self.board_state:
            self._draw_board(BX, BY, self.board_state, self.given_cells, self.cell_anims, CS, gc)

        self._draw_stats(BX, BY + CS * 9 + 18, CS * 9, gc)

        PX = BX + CS * 9 + 30
        PY = 62
        PW = W - PX - 15
        PH = H - PY - 15
        self._draw_panel(PX, PY, PW, PH, events, mouse, click, gc)

    def _draw_speed_control(self, events, mouse, click):
        lbl = F_SM.render(f"Toc do: {self.speed} steps/s", True, TXT_D)
        self.screen.blit(lbl, (620, 8))
        slider_rect = pygame.Rect(620, 30, 240, 16)
        pygame.draw.rect(self.screen, CARD, slider_rect, border_radius=8)
        ratio = (self.speed - 1) / 99
        fill_w = int(240 * ratio)
        if fill_w > 0:
            pygame.draw.rect(self.screen, blend(ACCENT, CARD, 0.3), (620, 30, fill_w, 16), border_radius=8)
        handle_x = 620 + fill_w
        pygame.draw.circle(self.screen, ACCENT, (handle_x, 38), 9)
        pygame.draw.circle(self.screen, TXT_B, (handle_x, 38), 5)

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if slider_rect.inflate(20, 20).collidepoint(mouse):
                    self.slider_drag = True
            if e.type == pygame.MOUSEBUTTONUP:
                self.slider_drag = False

        if self.slider_drag:
            rx = max(0, min(240, mouse[0] - 620))
            self.speed = max(1, min(100, int(1 + rx / 240 * 99)))

    def _update_animation(self):
        if self.anim_paused or self.anim_done:
            return
        if not self.steps or self.anim_running:
            return
        if self.step_idx >= len(self.steps):
            self.anim_done = True
            return

        now = time.time()
        delay = 1.0 / max(1, self.speed)
        if now - self.last_step_t >= delay:
            step = self.steps[self.step_idx]
            self._process_step(step)
            self.step_idx += 1
            self.last_step_t = now

    def _process_step(self, step):
        t = step.get('type', 'info')
        r = step.get('row', -1)
        c = step.get('col', -1)
        v = step.get('value', 0)
        msg = step.get('msg', '')
        board = step.get('board')

        if board:
            self.board_state = list(board)

        now = time.time()
        idx = self.step_idx

        if t == 'place':
            self.cell_anims[(r, c)] = {'type': 'place', 'start': now, 'dur': 0.4, 'value': v}
            self.log_entries.append({'msg': f'[{idx}] {msg}', 'color': SUC})
            self.stats_data['last_action'] = f'Place R{r+1}C{c+1}={v}'
        elif t == 'backtrack':
            self.cell_anims[(r, c)] = {'type': 'backtrack', 'start': now, 'dur': 0.5, 'value': v}
            self.log_entries.append({'msg': f'[{idx}] {msg}', 'color': ERR})
            bt_count = self.stats_data.get('backtracks', 0) + 1
            self.stats_data['backtracks'] = bt_count
            self.stats_data['last_action'] = f'Backtrack R{r+1}C{c+1}'
        elif t == 'swap':
            self.cell_anims[(r, c)] = {'type': 'swap', 'start': now, 'dur': 0.35}
            r2 = step.get('row2', -1)
            c2 = step.get('col2', -1)
            if r2 >= 0:
                self.cell_anims[(r2, c2)] = {'type': 'swap', 'start': now, 'dur': 0.35}
            self.log_entries.append({'msg': f'[{idx}] {msg}', 'color': INFO})
        elif t == 'success':
            self.log_entries.append({'msg': f'  {msg}', 'color': MINT})
            self.anim_done = True
            self.stats_data['result'] = 'Tim thay loi giai!'
        elif t == 'fail':
            self.log_entries.append({'msg': f'  {msg}', 'color': ERR})
            self.anim_done = True
            self.stats_data['result'] = 'Khong tim thay'
        elif t == 'info':
            self.log_entries.append({'msg': f'[{idx}] {msg}', 'color': WARN})
            if r >= 0:
                self.cell_anims[(r, c)] = {'type': 'info', 'start': now, 'dur': 0.3}

        self.stats_data['steps'] = self.step_idx + 1

    def _draw_board(self, bx, by, board, given, anims, cs, gc):
        board_w = cs * 9
        board_h = cs * 9
        bg_rect = pygame.Rect(bx - 4, by - 4, board_w + 8, board_h + 8)
        pygame.draw.rect(self.screen, (12, 12, 30), bg_rect, border_radius=8)

        now = time.time()
        expired = []
        for key, anim in anims.items():
            if now - anim['start'] > anim['dur'] * 2:
                expired.append(key)
        for key in expired:
            del anims[key]

        for r in range(9):
            for c in range(9):
                x = bx + c * cs
                y = by + r * cs
                idx = r * 9 + c
                val = board[idx]
                cell_rect = pygame.Rect(x, y, cs, cs)

                cb = (18, 18, 42) if (r // 3 + c // 3) % 2 == 0 else (22, 22, 48)

                anim = anims.get((r, c))
                anim_active = anim and (now - anim['start']) < anim['dur']

                if anim_active:
                    prog = min(1.0, (now - anim['start']) / anim['dur'])
                    ep = ease_out(prog)
                    if anim['type'] == 'place':
                        cb = blend(cb, SUC, 0.35 * (1 - ep))
                    elif anim['type'] == 'backtrack':
                        cb = blend(cb, ERR, 0.5 * (1 - ep))
                    elif anim['type'] == 'swap':
                        cb = blend(cb, INFO, 0.3 * (1 - ep))
                    elif anim['type'] == 'info':
                        cb = blend(cb, WARN, 0.3 * (1 - ep))

                pygame.draw.rect(self.screen, cb, cell_rect)

                if self.edit_mode and self.edit_selected == (r, c):
                    pygame.draw.rect(self.screen, gc, cell_rect, 3)

                if val != 0:
                    if idx in given:
                        color = C_GIVEN
                    elif anim_active and anim['type'] == 'backtrack':
                        fade = min(1.0, (now - anim['start']) / anim['dur'])
                        color = blend(ERR, cb, fade)
                    elif anim_active and anim['type'] == 'place':
                        color = blend(SUC, C_PLACED, ease_out(min(1.0, (now - anim['start']) / anim['dur'])))
                    else:
                        color = C_PLACED

                    scale = 1.0
                    if anim_active and anim['type'] == 'place':
                        prog = min(1.0, (now - anim['start']) / anim['dur'])
                        scale = 0.5 + 0.5 * ease_out(prog)

                    f = F_CELL if idx in given else pygame.font.SysFont(FN, max(10, int(28 * scale)), True)
                    txt = f.render(str(val), True, color)
                    txt_rect = txt.get_rect(center=(x + cs // 2, y + cs // 2))
                    self.screen.blit(txt, txt_rect)

        for i in range(10):
            thick = 3 if i % 3 == 0 else 1
            color = GRID_T if i % 3 == 0 else GRID
            pygame.draw.line(self.screen, color, (bx, by + i * cs), (bx + 9 * cs, by + i * cs), thick)
            pygame.draw.line(self.screen, color, (bx + i * cs, by), (bx + i * cs, by + 9 * cs), thick)

        corner_len = 8
        corners = [(bx, by), (bx + board_w, by), (bx, by + board_h), (bx + board_w, by + board_h)]
        for cx, cy in corners:
            dx = 1 if cx == bx else -1
            dy = 1 if cy == by else -1
            pygame.draw.line(self.screen, gc, (cx, cy), (cx + corner_len * dx, cy), 2)
            pygame.draw.line(self.screen, gc, (cx, cy), (cx, cy + corner_len * dy), 2)

    def _draw_mini_board(self, bx, by, board, cs):
        for r in range(9):
            for c in range(9):
                x = bx + c * cs
                y = by + r * cs
                val = board[r * 9 + c]
                cb = (18, 18, 42) if (r // 3 + c // 3) % 2 == 0 else (22, 22, 48)
                pygame.draw.rect(self.screen, cb, (x, y, cs, cs))
                if val != 0:
                    f = pygame.font.SysFont(FN, max(8, cs - 8))
                    txt = f.render(str(val), True, C_GIVEN)
                    self.screen.blit(txt, txt.get_rect(center=(x + cs // 2, y + cs // 2)))

        for i in range(10):
            thick = 2 if i % 3 == 0 else 1
            color = GRID_T if i % 3 == 0 else GRID
            pygame.draw.line(self.screen, color, (bx, by + i * cs), (bx + 9 * cs, by + i * cs), thick)
            pygame.draw.line(self.screen, color, (bx + i * cs, by), (bx + i * cs, by + 9 * cs), thick)

    def _draw_stats(self, x, y, w, gc):
        panel_h = 120
        pygame.draw.rect(self.screen, PANEL, (x, y, w, panel_h), border_radius=10)

        st = F_BTN.render("STATS", True, gc)
        self.screen.blit(st, (x + 12, y + 8))
        pygame.draw.line(self.screen, blend(gc, PANEL, 0.5), (x + 12, y + 30), (x + w - 12, y + 30), 1)

        col1_x = x + 14
        col2_x = x + w // 2 + 10
        row_h = 20
        sy = y + 38

        items_l = [
            ("Steps:", str(self.stats_data.get('steps', 0))),
            ("Backtracks:", str(self.stats_data.get('backtracks', 0))),
            ("Progress:", f"{self.step_idx}/{len(self.steps)}" if self.steps else "0/0"),
        ]
        items_r = [
            ("Speed:", f"{self.speed} st/s"),
            ("Status:", "Dang chay..." if not self.anim_done else self.stats_data.get('result', '---')),
        ]

        for i, (label, val) in enumerate(items_l):
            lt = F_SM.render(label, True, TXT_D)
            vt = F_SM.render(val, True, TXT)
            self.screen.blit(lt, (col1_x, sy + i * row_h))
            self.screen.blit(vt, (col1_x + lt.get_width() + 6, sy + i * row_h))

        for i, (label, val) in enumerate(items_r):
            lt = F_SM.render(label, True, TXT_D)
            color = SUC if 'Tim thay' in val else (ERR if 'Khong' in val else TXT)
            vt = F_SM.render(val, True, color)
            self.screen.blit(lt, (col2_x, sy + i * row_h))
            self.screen.blit(vt, (col2_x + lt.get_width() + 6, sy + i * row_h))

        if self.stats_data.get('backtracks', 0) > 0:
            bt_count = self.stats_data['backtracks']
            bar_y = sy + 3 * row_h + 4
            bar_w = min(w - 28, bt_count * 2)
            pygame.draw.rect(self.screen, blend(ERR, PANEL, 0.6), (col1_x, bar_y, w - 28, 8), border_radius=4)
            pygame.draw.rect(self.screen, ERR, (col1_x, bar_y, min(bar_w, w - 28), 8), border_radius=4)

    def _draw_panel(self, px, py, pw, ph, events, mouse, click, gc):
        pygame.draw.rect(self.screen, PANEL, (px, py, pw, ph), border_radius=12)

        tab_names = ["Log Dap An", "Chay Tay"]
        tab_w = pw // 2
        tab_h = 34

        for i, tn in enumerate(tab_names):
            tx = px + i * tab_w
            tr = pygame.Rect(tx, py, tab_w, tab_h)
            active = self.active_tab == i
            tc = TAB_ACT if active else TAB_BG
            pygame.draw.rect(self.screen, tc, tr,
                           border_top_left_radius=12 if i == 0 else 0,
                           border_top_right_radius=12 if i == 1 else 0)
            if active:
                pygame.draw.line(self.screen, gc, (tx + 4, py + tab_h - 2), (tx + tab_w - 4, py + tab_h - 2), 2)
            icon = "[ ]" if i == 0 else "[#]"
            tt = F_BTN.render(f"{icon} {tn}", True, TXT_B if active else TXT_D)
            self.screen.blit(tt, tt.get_rect(center=tr.center))

            if tr.collidepoint(mouse) and click:
                self.active_tab = i
                self.edit_mode = (i == 1)

        content_y = py + tab_h + 4
        content_h = ph - tab_h - 4

        if self.active_tab == 0:
            self._draw_log_tab(px + 4, content_y, pw - 8, content_h, events, mouse, gc)
        else:
            self._draw_manual_tab(px + 4, content_y, pw - 8, content_h, events, mouse, click, gc)

    def _draw_log_tab(self, x, y, w, h, events, mouse, gc):
        clip_rect = pygame.Rect(x, y, w, h)

        line_h = 19
        total_h = len(self.log_entries) * line_h
        max_scroll = max(0, total_h - h + 20)

        for e in events:
            if e.type == pygame.MOUSEWHEEL and clip_rect.collidepoint(mouse):
                self.log_scroll -= e.y * 50
                self.log_scroll = max(0, min(max_scroll, self.log_scroll))

        if not self.anim_done and total_h > h:
            self.log_scroll = max_scroll

        self.screen.set_clip(clip_rect)

        if not self.log_entries:
            if self.anim_running:
                wt = F_BODY.render("Dang chuan bi...", True, TXT_D)
            else:
                wt = F_BODY.render("Click RUN de bat dau", True, TXT_D)
            self.screen.blit(wt, (x + 12, y + 20))
        else:
            for i, entry in enumerate(self.log_entries):
                ly = y + i * line_h - self.log_scroll
                if ly < y - line_h or ly > y + h:
                    continue
                msg = entry['msg']
                color = entry['color']
                if len(msg) > 80:
                    msg = msg[:77] + "..."
                txt = F_LOG.render(msg, True, color)
                self.screen.blit(txt, (x + 8, ly + 2))

        self.screen.set_clip(None)

        if total_h > h:
            sb_h = max(30, int(h * h / max(1, total_h)))
            sb_y = y + int((h - sb_h) * self.log_scroll / max(1, max_scroll))
            pygame.draw.rect(self.screen, blend(gc, PANEL, 0.5), (x + w - 6, sb_y, 4, sb_h), border_radius=2)

        count_t = F_XS.render(f"{len(self.log_entries)} entries", True, TXT_D)
        self.screen.blit(count_t, (x + w - count_t.get_width() - 12, y + h - 16))

    def _draw_manual_tab(self, x, y, w, h, events, mouse, click, gc):
        cy = y + 8

        sec_t = F_BTN.render("Load mau:", True, TXT)
        self.screen.blit(sec_t, (x + 10, cy))
        cy += 24

        for i, (name, board) in enumerate(SAMPLE_BOARDS):
            bw = (w - 30) // 4
            bx = x + 5 + i * (bw + 5)
            br = pygame.Rect(bx, cy, bw, 28)
            bh = br.collidepoint(mouse)
            pygame.draw.rect(self.screen, CARD_H if bh else CARD, br, border_radius=6)
            bt = F_SM.render(name, True, gc if bh else TXT_D)
            self.screen.blit(bt, bt.get_rect(center=br.center))
            if bh and click:
                self.edit_board = list(board)
                self.board_state = list(board)
                self.given_cells = set(i for i in range(81) if board[i] != 0)
                self.edit_selected = None
        cy += 38

        pygame.draw.line(self.screen, blend(gc, PANEL, 0.4), (x + 10, cy), (x + w - 10, cy), 1)
        cy += 8

        sec2 = F_BTN.render("Chon thuat toan:", True, TXT)
        self.screen.blit(sec2, (x + 10, cy))
        cy += 24

        visible_algos = 6
        algo_h = 32
        clip_algo = pygame.Rect(x, cy, w, visible_algos * algo_h + 4)
        self.screen.set_clip(clip_algo)

        for i, (gid, aid, aname, afull) in enumerate(ALL_ALGOS_FLAT):
            ar = pygame.Rect(x + 5, cy + i * algo_h, w - 10, algo_h - 2)
            selected = i == self.edit_algo_idx
            ah = ar.collidepoint(mouse)
            ac = TAB_ACT if selected else (CARD_H if ah else CARD)
            pygame.draw.rect(self.screen, ac, ar, border_radius=6)
            if selected:
                pygame.draw.rect(self.screen, GC[gid], ar, 2, border_radius=6)
            badge_r = pygame.Rect(ar.x + 4, ar.y + 4, 24, 22)
            pygame.draw.rect(self.screen, blend(GC[gid], CARD, 0.5), badge_r, border_radius=4)
            gn = F_XS.render(str(gid), True, GC[gid])
            self.screen.blit(gn, gn.get_rect(center=badge_r.center))
            at = F_SM.render(f"{aname} — {afull}", True, TXT_B if selected else TXT_D)
            self.screen.blit(at, (ar.x + 34, ar.y + 8))
            if ah and click:
                self.edit_algo_idx = i

        self.screen.set_clip(None)
        cy += visible_algos * algo_h + 10

        for e in events:
            if e.type == pygame.MOUSEWHEEL and clip_algo.collidepoint(mouse):
                pass

        pygame.draw.line(self.screen, blend(gc, PANEL, 0.4), (x + 10, cy), (x + w - 10, cy), 1)
        cy += 10

        self._draw_manual_board_input(x + 10, cy, w - 20, events, mouse, click, gc)
        cy += 220

        run_r = pygame.Rect(x + 10, cy, w - 20, 40)
        rh = run_r.collidepoint(mouse)
        rc = gc if rh else blend(gc, PANEL, 0.5)
        pygame.draw.rect(self.screen, rc, run_r, border_radius=10)
        if rh:
            glow = pygame.Surface((run_r.w, run_r.h), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*gc, 40), (0, 0, run_r.w, run_r.h), border_radius=10)
            self.screen.blit(glow, run_r.topleft)
        rt = F_SUB.render("RUN", True, TXT_B)
        self.screen.blit(rt, rt.get_rect(center=run_r.center))

        if rh and click:
            _, aid, _, _ = ALL_ALGOS_FLAT[self.edit_algo_idx]
            board_tuple = tuple(self.edit_board)
            self.sel_board = board_tuple
            self.sel_algo = {'id': aid, 'full': ALGO_NAMES[aid], 'name': aid}
            self.active_tab = 0
            self.edit_mode = False
            self._start_solve(aid, board_tuple)

        cy += 50

        if self.edit_result_log:
            for i, entry in enumerate(self.edit_result_log[-5:]):
                et = F_LOG.render(entry['msg'], True, entry['color'])
                self.screen.blit(et, (x + 10, cy + i * 18))

    def _draw_manual_board_input(self, x, y, w, events, mouse, click, gc):
        label = F_SM.render("Click o tren bang chinh (ben trai) de nhap so. Phim 1-9 dat so, Delete xoa.", True, TXT_D)
        self.screen.blit(label, (x, y))
        y += 20

        cs = 22
        bx_off = (w - cs * 9) // 2
        for r in range(9):
            for c in range(9):
                cx = x + bx_off + c * cs
                cy_cell = y + r * cs
                idx = r * 9 + c
                val = self.edit_board[idx]
                cell_r = pygame.Rect(cx, cy_cell, cs, cs)

                orig_given = VERY_EASY_BOARD[idx] != 0
                cb = (18, 18, 42) if (r // 3 + c // 3) % 2 == 0 else (22, 22, 48)
                if self.edit_selected == (r, c):
                    cb = blend(gc, cb, 0.3)

                pygame.draw.rect(self.screen, cb, cell_r)

                if val != 0:
                    fc = C_GIVEN if orig_given else C_PLACED
                    ft = pygame.font.SysFont(FN, cs - 6, True)
                    vt = ft.render(str(val), True, fc)
                    self.screen.blit(vt, vt.get_rect(center=cell_r.center))

        for i in range(10):
            thick = 2 if i % 3 == 0 else 1
            color = GRID_T if i % 3 == 0 else GRID
            lx = x + bx_off
            ly = y
            pygame.draw.line(self.screen, color, (lx, ly + i * cs), (lx + 9 * cs, ly + i * cs), thick)
            pygame.draw.line(self.screen, color, (lx + i * cs, ly), (lx + i * cs, ly + 9 * cs), thick)

        if self.edit_mode:
            CS_MAIN = 52
            BX_MAIN = 30
            BY_MAIN = 72
            for e in events:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    mx, my = e.pos
                    if BX_MAIN <= mx < BX_MAIN + 9 * CS_MAIN and BY_MAIN <= my < BY_MAIN + 9 * CS_MAIN:
                        sc = (mx - BX_MAIN) // CS_MAIN
                        sr = (my - BY_MAIN) // CS_MAIN
                        if 0 <= sr < 9 and 0 <= sc < 9:
                            self.edit_selected = (sr, sc)
                if e.type == pygame.KEYDOWN and self.edit_selected:
                    sr, sc = self.edit_selected
                    idx = sr * 9 + sc
                    if e.key in (pygame.K_DELETE, pygame.K_BACKSPACE, pygame.K_0):
                        self.edit_board[idx] = 0
                        self.board_state = list(self.edit_board)
                    elif pygame.K_1 <= e.key <= pygame.K_9:
                        self.edit_board[idx] = e.key - pygame.K_0
                        self.board_state = list(self.edit_board)
                        self.given_cells = set(i for i in range(81) if self.edit_board[i] != 0)
                    elif e.key in (pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4,
                                   pygame.K_KP5, pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, pygame.K_KP9):
                        self.edit_board[idx] = e.key - pygame.K_KP1 + 1
                        self.board_state = list(self.edit_board)
                        self.given_cells = set(i for i in range(81) if self.edit_board[i] != 0)
                    elif e.key == pygame.K_TAB or e.key == pygame.K_RIGHT:
                        nc = sc + 1 if sc < 8 else 0
                        nr = sr + (1 if sc == 8 else 0)
                        if nr < 9:
                            self.edit_selected = (nr, nc)
                    elif e.key == pygame.K_LEFT:
                        nc = sc - 1 if sc > 0 else 8
                        nr = sr - (1 if sc == 0 else 0)
                        if nr >= 0:
                            self.edit_selected = (nr, nc)
                    elif e.key == pygame.K_DOWN and sr < 8:
                        self.edit_selected = (sr + 1, sc)
                    elif e.key == pygame.K_UP and sr > 0:
                        self.edit_selected = (sr - 1, sc)


if __name__ == '__main__':
    app = App()
    app.run()
