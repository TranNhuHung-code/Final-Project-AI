# -*- coding: utf-8 -*-
"""
alpha_beta_solver.py
Cài đặt thuật toán Alpha-Beta Pruning áp dụng cho "SUDOKU BATTLE".
Dựa trên cấu trúc của minimax_solver.py nhưng tối ưu tốc độ duyệt bằng cách cắt tỉa nhánh.
"""

import copy
import random
from sudoku_utils import SIZE, is_valid, find_empty_cells


class AlphaBetaSudokuBattle:
    def __init__(self, puzzle, real_solution, search_depth=3, candidate_cells_per_turn=6):
        self.puzzle = copy.deepcopy(puzzle)
        self.real_solution = real_solution
        self.board = copy.deepcopy(puzzle)
        self.search_depth = search_depth
        self.candidate_cells_per_turn = candidate_cells_per_turn

        self.agent_score = 0
        self.human_score = 0
        self.nodes_evaluated = 0

    def get_empty_cells(self):
        return find_empty_cells(self.board)

    def is_game_over(self):
        return len(self.get_empty_cells()) == 0

    def human_move(self, row, col, value):
        self.board[row][col] = value
        is_correct = (value == self.real_solution[row][col])
        if is_correct:
            self.human_score += 1
        return is_correct

    def agent_move(self, row, col, value):
        self.board[row][col] = value
        is_correct = (value == self.real_solution[row][col])
        if is_correct:
            self.agent_score += 1
        return is_correct

    def _evaluate(self, board, agent_score, human_score, remaining_empty):
        return (agent_score - human_score) + 0.5 * len(remaining_empty)

    def _candidate_moves(self, board, empty_cells, limit):
        scored_cells = []
        for (r, c) in empty_cells:
            valid_values = [v for v in range(1, 10) if is_valid(board, r, c, v)]
            if not valid_values:
                valid_values = list(range(1, 10))
            scored_cells.append((r, c, valid_values))

        scored_cells.sort(key=lambda item: len(item[2]))
        return scored_cells[:limit]

    def _alpha_beta(self, board, agent_score, human_score, depth, alpha, beta, is_agent_turn, trace=None):
        self.nodes_evaluated += 1
        empty_cells = find_empty_cells(board)

        if depth == 0 or not empty_cells:
            return self._evaluate(board, agent_score, human_score, empty_cells)

        candidates = self._candidate_moves(board, empty_cells, self.candidate_cells_per_turn)
        if not candidates:
            return self._evaluate(board, agent_score, human_score, empty_cells)

        if is_agent_turn:
            best_value = float('-inf')
            for (r, c, valid_values) in candidates:
                for v in valid_values:
                    board[r][c] = v
                    correct = (v == self.real_solution[r][c])
                    new_agent_score = agent_score + (1 if correct else 0)

                    value = self._alpha_beta(board, new_agent_score, human_score,
                                           depth - 1, alpha, beta, False)

                    if trace is not None:
                        trace.append({'row': r, 'col': c, 'value': v, 'score': value, 'player': 'agent'})

                    board[r][c] = 0
                    best_value = max(best_value, value)
                    alpha = max(alpha, best_value)
                    if beta <= alpha:
                        break # Beta cut-off
                if beta <= alpha:
                    break
            return best_value
        else:
            best_value = float('inf')
            for (r, c, valid_values) in candidates:
                for v in valid_values:
                    board[r][c] = v
                    correct = (v == self.real_solution[r][c])
                    new_human_score = human_score + (1 if correct else 0)

                    value = self._alpha_beta(board, agent_score, new_human_score,
                                           depth - 1, alpha, beta, True)

                    board[r][c] = 0
                    best_value = min(best_value, value)
                    beta = min(beta, best_value)
                    if beta <= alpha:
                        break # Alpha cut-off
                if beta <= alpha:
                    break
            return best_value

    def agent_choose_move(self):
        empty_cells = find_empty_cells(self.board)
        if not empty_cells:
            return None

        candidates = self._candidate_moves(self.board, empty_cells, self.candidate_cells_per_turn)

        best_value = float('-inf')
        best_move = None
        trace = []
        alpha = float('-inf')
        beta = float('inf')

        for (r, c, valid_values) in candidates:
            for v in valid_values:
                self.board[r][c] = v
                correct = (v == self.real_solution[r][c])
                new_agent_score = self.agent_score + (1 if correct else 0)

                value = self._alpha_beta(self.board, new_agent_score, self.human_score,
                                       self.search_depth - 1, alpha, beta, False)

                trace.append({'row': r, 'col': c, 'value': v, 'score': round(value, 2)})

                self.board[r][c] = 0

                if value > best_value:
                    best_value = value
                    best_move = (r, c, v)
                alpha = max(alpha, best_value)

        trace.sort(key=lambda t: -t['score'])
        return best_move[0], best_move[1], best_move[2], trace
