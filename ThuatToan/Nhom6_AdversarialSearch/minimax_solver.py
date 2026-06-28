# -*- coding: utf-8 -*-
import copy
import random
from sudoku_utils import SIZE, is_valid, find_empty_cells

class MinimaxSudokuBattle:
    """
    SUDOKU BATTLE (Luật Mới: ÉP ĐỐI THỦ GIẢI Ô CHỈ ĐỊNH)
    - Người chơi luân phiên: Người điền xong 1 ô -> Được quyền CHỈ ĐỊNH 1 ô trống bất kỳ trên bàn cờ bắt Agent phải giải.
    - Điền sai: Bị -1 điểm (bị ghi nhận 1 lỗi). Tối đa 5 lỗi (5 điểm) là thua ngay lập tức.
    - Điền đúng: Bàn cờ được cập nhật.
    - Hết ô trống: Trận đấu hòa hoặc ai ít lỗi hơn thắng (mặc định hòa 0 nếu không ai đạt 5 lỗi).
    """
    def __init__(self, puzzle, real_solution, search_depth=2):
        self.puzzle = copy.deepcopy(puzzle)
        self.real_solution = real_solution
        self.board = copy.deepcopy(puzzle)
        self.search_depth = search_depth
        
        self.human_mistakes = 0
        self.agent_mistakes = 0
        self.nodes_evaluated = 0

    def get_empty_cells(self):
        return find_empty_cells(self.board)

    def is_game_over(self):
        if self.human_mistakes >= 5 or self.agent_mistakes >= 5:
            return True
        return len(self.get_empty_cells()) == 0

    def human_move(self, row, col, value):
        is_correct = (value == self.real_solution[row][col])
        if is_correct:
            self.board[row][col] = value
        else:
            self.human_mistakes += 1
        return is_correct

    def agent_move(self, row, col, value):
        is_correct = (value == self.real_solution[row][col])
        if is_correct:
            self.board[row][col] = value
        else:
            self.agent_mistakes += 1
        return is_correct

    def _hardness(self, board, r, c):
        # Đánh giá độ khó của 1 ô = số lượng ứng viên hợp lệ còn lại. Càng nhiều số hợp lệ thì người chơi càng dễ đoán sai.
        return sum(1 for v in range(1, 10) if is_valid(board, r, c, v))

    def _minimax(self, board, depth, is_max_turn):
        self.nodes_evaluated += 1
        empty_cells = find_empty_cells(board)
        if depth == 0 or not empty_cells:
            return 0

        if is_max_turn:
            best_val = float('-inf')
            for r, c in empty_cells:
                # Immediate reward: Agent ép Human vào ô (r,c), nhận được "độ khó" của ô này
                hardness = self._hardness(board, r, c)
                
                board[r][c] = self.real_solution[r][c] # Mô phỏng Human giải đúng
                val = hardness + self._minimax(board, depth - 1, False)
                board[r][c] = 0
                
                if val > best_val: best_val = val
            return best_val
        else:
            best_val = float('inf')
            for r, c in empty_cells:
                # Immediate penalty: Human ép Agent vào ô (r,c), Agent bị "trừ" độ khó của ô này
                hardness = self._hardness(board, r, c)
                
                board[r][c] = self.real_solution[r][c] # Mô phỏng Agent giải đúng
                val = -hardness + self._minimax(board, depth - 1, True)
                board[r][c] = 0
                
                if val < best_val: best_val = val
            return best_val

    def agent_choose_target(self):
        """
        Agent tính toán và chọn ra ô trống tốt nhất (gây khó dễ nhất) để ép Người chơi giải.
        Trả về (row, col, trace)
        """
        empty_cells = find_empty_cells(self.board)
        if not empty_cells:
            return None

        candidates = []
        for r, c in empty_cells:
            candidates.append((r, c, self._hardness(self.board, r, c)))
        
        # Lọc ra top 6 ô khó nhất để Minimax duyệt nhằm tối ưu thời gian (giảm branching factor)
        candidates.sort(key=lambda x: x[2], reverse=True)
        candidates = candidates[:6]

        best_val = float('-inf')
        best_move = None
        trace = []

        for r, c, hardness in candidates:
            self.board[r][c] = self.real_solution[r][c]
            val = hardness + self._minimax(self.board, self.search_depth - 1, False)
            self.board[r][c] = 0
            
            trace.append({'row': r, 'col': c, 'score': val, 'hardness': hardness})
            if val > best_val:
                best_val = val
                best_move = (r, c)
                
        if best_move is None:
            best_move = (candidates[0][0], candidates[0][1])

        nodes = self.nodes_evaluated
        self.nodes_evaluated = 0
        return best_move[0], best_move[1], trace, nodes
