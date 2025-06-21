"""
CPU AI implementation for Tetris.
"""

import random
import copy
from typing import List, Tuple, Optional, Dict
from tetris_game import TetrisGame, Tetromino, TetrisBoard, RotationState
from constants import *

class TetrisAI:
    """AI player for Tetris with configurable difficulty."""
    
    def __init__(self, difficulty: str = 'medium'):
        self.difficulty = difficulty
        self.weights = self._get_weights_for_difficulty(difficulty)
        
    def _get_weights_for_difficulty(self, difficulty: str) -> Dict[str, float]:
        """Get evaluation weights based on difficulty level."""
        if difficulty == 'easy':
            return {
                'height_weight': -0.5,
                'lines_weight': 0.7,
                'holes_weight': -0.3,
                'bumpiness_weight': -0.1,
                'well_weight': -0.2
            }
        elif difficulty == 'medium':
            return {
                'height_weight': -0.8,
                'lines_weight': 1.0,
                'holes_weight': -0.5,
                'bumpiness_weight': -0.3,
                'well_weight': -0.4
            }
        elif difficulty == 'hard':
            return {
                'height_weight': -1.2,
                'lines_weight': 1.5,
                'holes_weight': -0.8,
                'bumpiness_weight': -0.5,
                'well_weight': -0.6
            }
        else:  # expert
            return {
                'height_weight': -1.5,
                'lines_weight': 2.0,
                'holes_weight': -1.0,
                'bumpiness_weight': -0.8,
                'well_weight': -0.8
            }
    
    def get_best_move(self, game: TetrisGame) -> Optional[Tuple[int, int, int]]:
        """
        Get the best move for current piece.
        Returns (x, y, rotation) or None if no valid move.
        """
        if not game.current_piece:
            return None
        
        best_move = None
        best_score = float('-inf')
        
        # Try all possible positions and rotations
        for rotation in range(4):
            test_piece = game.current_piece.copy()
            test_piece.rotation = RotationState(rotation)
            
            # Try all horizontal positions
            for x in range(-3, game.board.width + 3):
                test_piece.x = x
                test_piece.y = game.current_piece.y
                
                # Skip if piece is obviously out of bounds
                if not self._is_potentially_valid(test_piece, game.board):
                    continue
                
                # Drop piece to bottom
                while game.board.is_valid_position(test_piece):
                    test_piece.y += 1
                test_piece.y -= 1
                
                # Check if final position is valid
                if not game.board.is_valid_position(test_piece):
                    continue
                
                # Evaluate this position
                score = self._evaluate_position(test_piece, game.board)
                
                if score > best_score:
                    best_score = score
                    best_move = (test_piece.x, test_piece.y, rotation)
        
        return best_move
    
    def _is_potentially_valid(self, piece: Tetromino, board: TetrisBoard) -> bool:
        """Quick check if piece could potentially be valid."""
        shape = piece.get_shape()
        piece_width = len(shape[0])
        
        # Check if piece could fit horizontally
        if piece.x + piece_width < 0 or piece.x >= board.width:
            return False
        
        return True
    
    def _evaluate_position(self, piece: Tetromino, board: TetrisBoard) -> float:
        """Evaluate a piece placement position."""
        # Create temporary board with piece placed
        temp_board = self._create_temp_board(piece, board)
        
        # Clear lines and get number cleared
        lines_cleared = self._count_clearable_lines(temp_board)
        temp_board = self._clear_lines(temp_board)
        
        # Calculate metrics
        height = self._calculate_aggregate_height(temp_board)
        holes = self._calculate_holes(temp_board)
        bumpiness = self._calculate_bumpiness(temp_board)
        wells = self._calculate_wells(temp_board)
        
        # Calculate weighted score
        score = (
            self.weights['height_weight'] * height +
            self.weights['lines_weight'] * lines_cleared +
            self.weights['holes_weight'] * holes +
            self.weights['bumpiness_weight'] * bumpiness +
            self.weights['well_weight'] * wells
        )
        
        # Add randomness for variety (more randomness on easier difficulties)
        if self.difficulty == 'easy':
            randomness = random.uniform(-0.5, 0.5)
        elif self.difficulty == 'medium':
            randomness = random.uniform(-0.2, 0.2)
        else:
            randomness = random.uniform(-0.1, 0.1)
        
        return score + randomness
    
    def _create_temp_board(self, piece: Tetromino, board: TetrisBoard) -> List[List[bool]]:
        """Create temporary board with piece placed."""
        temp_board = []
        
        # Copy original board
        for row in board.grid:
            temp_row = [cell is not None for cell in row]
            temp_board.append(temp_row)
        
        # Place piece
        blocks = piece.get_blocks()
        for x, y in blocks:
            if 0 <= y < len(temp_board) and 0 <= x < len(temp_board[0]):
                temp_board[y][x] = True
        
        return temp_board
    
    def _count_clearable_lines(self, board: List[List[bool]]) -> int:
        """Count how many lines can be cleared."""
        lines_cleared = 0
        
        for row in board:
            if all(row):
                lines_cleared += 1
        
        return lines_cleared
    
    def _clear_lines(self, board: List[List[bool]]) -> List[List[bool]]:
        """Clear complete lines from board."""
        new_board = []
        width = len(board[0]) if board else 0
        
        for row in board:
            if not all(row):
                new_board.append(row[:])
        
        # Add empty lines at top
        while len(new_board) < len(board):
            new_board.insert(0, [False] * width)
        
        return new_board
    
    def _calculate_aggregate_height(self, board: List[List[bool]]) -> int:
        """Calculate sum of column heights."""
        total_height = 0
        width = len(board[0]) if board else 0
        height = len(board)
        
        for x in range(width):
            column_height = 0
            for y in range(height):
                if board[y][x]:
                    column_height = height - y
                    break
            total_height += column_height
        
        return total_height
    
    def _calculate_holes(self, board: List[List[bool]]) -> int:
        """Calculate number of holes (empty cells with filled cells above)."""
        holes = 0
        width = len(board[0]) if board else 0
        height = len(board)
        
        for x in range(width):
            found_block = False
            for y in range(height):
                if board[y][x]:
                    found_block = True
                elif found_block and not board[y][x]:
                    holes += 1
        
        return holes
    
    def _calculate_bumpiness(self, board: List[List[bool]]) -> int:
        """Calculate bumpiness (sum of height differences between adjacent columns)."""
        heights = self._get_column_heights(board)
        bumpiness = 0
        
        for i in range(len(heights) - 1):
            bumpiness += abs(heights[i] - heights[i + 1])
        
        return bumpiness
    
    def _calculate_wells(self, board: List[List[bool]]) -> int:
        """Calculate wells (empty columns surrounded by filled blocks)."""
        heights = self._get_column_heights(board)
        wells = 0
        
        for i, height in enumerate(heights):
            left_height = heights[i - 1] if i > 0 else float('inf')
            right_height = heights[i + 1] if i < len(heights) - 1 else float('inf')
            
            well_depth = min(left_height, right_height) - height
            if well_depth > 0:
                wells += well_depth * (well_depth + 1) // 2  # Triangular number
        
        return wells
    
    def _get_column_heights(self, board: List[List[bool]]) -> List[int]:
        """Get height of each column."""
        heights = []
        width = len(board[0]) if board else 0
        height = len(board)
        
        for x in range(width):
            column_height = 0
            for y in range(height):
                if board[y][x]:
                    column_height = height - y
                    break
            heights.append(column_height)
        
        return heights

class SimpleCPU:
    """Simple CPU implementation that makes random but somewhat intelligent moves."""
    
    def __init__(self):
        self.move_probability = 0.05  # 5% chance to make a move each update
        self.prefer_center = True
        
    def should_make_move(self) -> bool:
        """Determine if CPU should make a move this update."""
        return random.random() < self.move_probability
    
    def get_random_move(self, game: TetrisGame) -> str:
        """Get a random but somewhat intelligent move."""
        if not game.current_piece:
            return 'none'
        
        moves = ['left', 'right', 'rotate_cw', 'soft_drop']
        
        # Prefer moves toward center
        if self.prefer_center:
            center = game.board.width // 2
            if game.current_piece.x < center:
                moves.extend(['right'] * 2)  # Weight right moves
            elif game.current_piece.x > center:
                moves.extend(['left'] * 2)   # Weight left moves
        
        # Occasionally hard drop
        if random.random() < 0.1:
            moves.append('hard_drop')
        
        # Occasionally hold
        if random.random() < 0.05 and game.can_hold:
            moves.append('hold')
        
        return random.choice(moves)

class AdaptiveCPU:
    """CPU that adapts its strategy based on game state."""
    
    def __init__(self, base_difficulty: str = 'medium'):
        self.ai = TetrisAI(base_difficulty)
        self.simple_cpu = SimpleCPU()
        self.last_decision_time = 0
        self.decision_interval = 500  # ms between AI decisions
        self.current_plan = None
        self.plan_step = 0
        
    def update(self, game: TetrisGame, current_time: float) -> Optional[str]:
        """Update CPU and return next action."""
        if current_time - self.last_decision_time >= self.decision_interval:
            self._make_new_plan(game)
            self.last_decision_time = current_time
        
        return self._execute_plan(game)
    
    def _make_new_plan(self, game: TetrisGame):
        """Make a new movement plan."""
        if not game.current_piece:
            self.current_plan = None
            return
        
        # Use AI to find best position
        best_move = self.ai.get_best_move(game)
        if not best_move:
            self.current_plan = None
            return
        
        target_x, target_y, target_rotation = best_move
        current_x = game.current_piece.x
        current_rotation = game.current_piece.rotation.value
        
        # Create plan to reach target
        plan = []
        
        # Rotation first
        rotation_diff = (target_rotation - current_rotation) % 4
        if rotation_diff == 1:
            plan.append('rotate_cw')
        elif rotation_diff == 2:
            plan.extend(['rotate_cw', 'rotate_cw'])
        elif rotation_diff == 3:
            plan.append('rotate_ccw')
        
        # Then horizontal movement
        x_diff = target_x - current_x
        if x_diff > 0:
            plan.extend(['right'] * abs(x_diff))
        elif x_diff < 0:
            plan.extend(['left'] * abs(x_diff))
        
        # Finally drop
        plan.append('hard_drop')
        
        self.current_plan = plan
        self.plan_step = 0
    
    def _execute_plan(self, game: TetrisGame) -> Optional[str]:
        """Execute current plan step by step."""
        if not self.current_plan or self.plan_step >= len(self.current_plan):
            # No plan or plan finished, use simple CPU
            if self.simple_cpu.should_make_move():
                return self.simple_cpu.get_random_move(game)
            return None
        
        # Execute next step of plan
        action = self.current_plan[self.plan_step]
        self.plan_step += 1
        
        return action