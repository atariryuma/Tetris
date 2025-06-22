"""
Core Tetris game logic implementation.
"""

import pygame
import random
import time
from typing import List, Tuple, Optional, Dict
from enum import Enum
from constants import *
from input_manager import InputState, Action
from debug_logger import get_debug_logger

class RotationState(Enum):
    """Tetromino rotation states."""
    ZERO = 0
    NINETY = 1
    ONE_EIGHTY = 2
    TWO_SEVENTY = 3

class Tetromino:
    """Represents a Tetris piece."""
    
    def __init__(self, shape_type: str, x: int = 0, y: int = 0):
        self.type = shape_type
        self.shapes = TETROMINOS[shape_type]['shape']
        self.color = TETROMINOS[shape_type]['color']
        self.x = x
        self.y = y
        self.rotation = RotationState.ZERO
        
    def get_shape(self) -> List[str]:
        """Get current shape based on rotation."""
        return self.shapes[self.rotation.value]
    
    def get_blocks(self) -> List[Tuple[int, int]]:
        """Get list of block positions relative to piece position."""
        blocks = []
        shape = self.get_shape()
        
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell != '.' and cell != ' ':
                    blocks.append((self.x + col_idx, self.y + row_idx))
        
        return blocks
    
    def copy(self) -> 'Tetromino':
        """Create a copy of this tetromino."""
        piece = Tetromino(self.type, self.x, self.y)
        piece.rotation = self.rotation
        return piece

class TetrisBoard:
    """Represents the Tetris game board."""
    
    def __init__(self, width: int = BOARD_WIDTH, height: int = BOARD_HEIGHT):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.garbage_animation_rows = []  # Rows being animated
        
    def is_valid_position(self, piece: Tetromino) -> bool:
        """Check if piece position is valid."""
        blocks = piece.get_blocks()
        
        for x, y in blocks:
            # Check bounds
            if x < 0 or x >= self.width or y >= self.height:
                return False
            
            # Check collision with placed blocks
            if y >= 0 and self.grid[y][x] is not None:
                return False
                
        return True
    
    def place_piece(self, piece: Tetromino):
        """Place piece on the board."""
        blocks = piece.get_blocks()
        
        for x, y in blocks:
            if 0 <= y < self.height and 0 <= x < self.width:
                self.grid[y][x] = piece.color
    
    def clear_lines(self) -> List[int]:
        """Clear completed lines and return list of cleared line indices."""
        cleared_lines = []
        
        for y in range(self.height):
            if all(cell is not None for cell in self.grid[y]):
                cleared_lines.append(y)
        
        # Remove cleared lines
        for y in reversed(cleared_lines):
            del self.grid[y]
            self.grid.insert(0, [None for _ in range(self.width)])
        
        return cleared_lines
    
    def add_garbage_lines(self, count: int):
        """Add garbage lines at the bottom."""
        if count <= 0:
            return
            
        # Remove top lines
        for _ in range(min(count, self.height)):
            self.grid.pop(0)
        
        # Add garbage lines at bottom
        for _ in range(count):
            garbage_line = [Colors.GARBAGE] * self.width
            # Add random hole
            hole_pos = random.randint(0, self.width - 1)
            garbage_line[hole_pos] = None
            self.grid.append(garbage_line)
    
    def is_game_over(self) -> bool:
        """Check if game is over (top row has blocks)."""
        return any(cell is not None for cell in self.grid[0])
    
    def get_height_map(self) -> List[int]:
        """Get height map for AI evaluation."""
        heights = []
        
        for x in range(self.width):
            height = 0
            for y in range(self.height):
                if self.grid[y][x] is not None:
                    height = self.height - y
                    break
            heights.append(height)
        
        return heights

class TetrisGame:
    """Main Tetris game logic."""
    
    def __init__(self, player_id: int, mode: str = PlayerMode.HUMAN):
        self.player_id = player_id
        self.mode = mode
        self.debug = get_debug_logger()
        
        if self.debug:
            self.debug.log_info(f"Initializing TetrisGame for player {player_id}, mode: {mode}", f"TetrisGame.__init__")
        
        try:
            self.board = TetrisBoard()
            if self.debug:
                self.debug.log_info(f"TetrisBoard created successfully", f"TetrisGame.__init__")
        except Exception as e:
            if self.debug:
                self.debug.log_error(e, f"TetrisGame.__init__.board_creation")
            raise
        
        # Game state
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        
        # Pieces
        self.current_piece: Optional[Tetromino] = None
        self.next_piece: Optional[Tetromino] = None
        self.held_piece: Optional[Tetromino] = None
        self.can_hold = True
        self.ghost_piece: Optional[Tetromino] = None
        
        # Timing
        self.last_drop_time = 0
        self.drop_interval = DROP_INTERVAL_MS
        self.last_move_time = {
            Action.MOVE_LEFT: 0,
            Action.MOVE_RIGHT: 0,
            Action.SOFT_DROP: 0,
            Action.ROTATE_CW: 0,
            Action.ROTATE_CCW: 0,
            Action.HARD_DROP: 0,
            Action.HOLD: 0
        }
        
        # Initialize first pieces
        try:
            if self.debug:
                self.debug.log_info("Generating initial pieces", f"TetrisGame.__init__")
            self._generate_next_piece()
            self._spawn_piece()
            if self.debug:
                self.debug.log_info("Initial pieces generated successfully", f"TetrisGame.__init__")
        except Exception as e:
            if self.debug:
                self.debug.log_error(e, f"TetrisGame.__init__.piece_generation")
            raise
        
        # Statistics
        self.stats = {
            'pieces_placed': 0,
            'singles': 0,
            'doubles': 0,
            'triples': 0,
            'tetrises': 0,
            't_spins': 0,
            'garbage_sent': 0,
            'garbage_received': 0
        }
    
    def _generate_next_piece(self):
        """Generate next random piece."""
        piece_types = list(TETROMINOS.keys())
        piece_type = random.choice(piece_types)
        spawn_x, spawn_y = TETROMINOS[piece_type]['spawn']
        self.next_piece = Tetromino(piece_type, spawn_x, spawn_y)
    
    def _spawn_piece(self):
        """Spawn the next piece as current piece."""
        self.current_piece = self.next_piece
        self._generate_next_piece()
        self.can_hold = True
        self._update_ghost_piece()
        
        # Check for game over
        if not self.board.is_valid_position(self.current_piece):
            self.game_over = True
    
    def _update_ghost_piece(self):
        """Update ghost piece position."""
        if not self.current_piece:
            self.ghost_piece = None
            return
            
        self.ghost_piece = self.current_piece.copy()
        
        # Drop ghost piece to lowest valid position
        while self.board.is_valid_position(self.ghost_piece):
            self.ghost_piece.y += 1
        self.ghost_piece.y -= 1
    
    def update(self, input_state: InputState, delta_time: float) -> Dict[str, any]:
        """Update game state."""
        if self.game_over or self.paused:
            return {}
        
        current_time = time.time() * 1000
        events = {}
        
        # Handle input
        if self.mode == PlayerMode.HUMAN:
            events.update(self._handle_input(input_state, current_time))
        elif self.mode == PlayerMode.CPU:
            events.update(self._handle_cpu_move(current_time))
        
        # Handle gravity
        if current_time - self.last_drop_time >= self.drop_interval:
            if self._try_move_down():
                self.last_drop_time = current_time
            else:
                # Piece landed
                events.update(self._lock_piece())
        
        return events
    
    def _handle_input(self, input_state: InputState, current_time: float) -> Dict[str, any]:
        """Handle player input."""
        events = {}
        
        # Movement
        if input_state.pressed[Action.MOVE_LEFT]:
            if self._can_perform_action(Action.MOVE_LEFT, current_time):
                if self._try_move(-1, 0):
                    events['piece_moved'] = True
                    self.last_move_time[Action.MOVE_LEFT] = current_time
        
        if input_state.pressed[Action.MOVE_RIGHT]:
            if self._can_perform_action(Action.MOVE_RIGHT, current_time):
                if self._try_move(1, 0):
                    events['piece_moved'] = True
                    self.last_move_time[Action.MOVE_RIGHT] = current_time
        
        if input_state.pressed[Action.SOFT_DROP]:
            if self._can_perform_action(Action.SOFT_DROP, current_time):
                if self._try_move_down():
                    self.score += SCORE_VALUES['SOFT_DROP']
                    events['soft_drop'] = True
                    self.last_move_time[Action.SOFT_DROP] = current_time
        
        # Rotation
        if input_state.pressed[Action.ROTATE_CW]:
            if self._can_perform_action(Action.ROTATE_CW, current_time):
                if self._try_rotate(clockwise=True):
                    events['piece_rotated'] = True
                    self.last_move_time[Action.ROTATE_CW] = current_time
        
        if input_state.pressed[Action.ROTATE_CCW]:
            if self._can_perform_action(Action.ROTATE_CCW, current_time):
                if self._try_rotate(clockwise=False):
                    events['piece_rotated'] = True
                    self.last_move_time[Action.ROTATE_CCW] = current_time
        
        # Hard drop
        if input_state.pressed[Action.HARD_DROP]:
            if self._can_perform_action(Action.HARD_DROP, current_time):
                drop_distance = self._hard_drop()
                self.score += drop_distance * SCORE_VALUES['HARD_DROP']
                events.update(self._lock_piece())
                events['hard_drop'] = True
                self.last_move_time[Action.HARD_DROP] = current_time
        
        # Hold
        if input_state.pressed[Action.HOLD]:
            if self._can_perform_action(Action.HOLD, current_time) and self.can_hold:
                self._hold_piece()
                events['piece_held'] = True
                self.last_move_time[Action.HOLD] = current_time
        
        return events
    
    def _handle_cpu_move(self, current_time: float) -> Dict[str, any]:
        """Handle CPU AI move (simple implementation)."""
        events = {}
        
        # Simple AI: just rotate and move randomly occasionally
        if random.random() < 0.1:  # 10% chance per update
            if random.random() < 0.3:
                if self._try_rotate(clockwise=True):
                    events['piece_rotated'] = True
            elif random.random() < 0.5:
                direction = random.choice([-1, 1])
                if self._try_move(direction, 0):
                    events['piece_moved'] = True
            else:
                if self._try_move_down():
                    events['soft_drop'] = True
        
        return events
    
    def _can_perform_action(self, action: Action, current_time: float) -> bool:
        """Check if action can be performed based on timing."""
        return current_time - self.last_move_time[action] >= INPUT_INTERVAL_MS
    
    def _try_move(self, dx: int, dy: int) -> bool:
        """Try to move current piece."""
        if not self.current_piece:
            return False
            
        test_piece = self.current_piece.copy()
        test_piece.x += dx
        test_piece.y += dy
        
        if self.board.is_valid_position(test_piece):
            self.current_piece.x = test_piece.x
            self.current_piece.y = test_piece.y
            self._update_ghost_piece()
            return True
        
        return False
    
    def _try_move_down(self) -> bool:
        """Try to move current piece down."""
        return self._try_move(0, 1)
    
    def _try_rotate(self, clockwise: bool = True) -> bool:
        """Try to rotate current piece with wall kicks."""
        if not self.current_piece:
            return False
        
        # Get rotation direction
        old_rotation = self.current_piece.rotation
        new_rotation_value = (old_rotation.value + (1 if clockwise else -1)) % 4
        new_rotation = RotationState(new_rotation_value)
        
        # Try rotation
        test_piece = self.current_piece.copy()
        test_piece.rotation = new_rotation
        
        # Get wall kick data
        piece_group = 'I' if self.current_piece.type == 'I' else 'JLSTZ'
        kick_key = f"{old_rotation.value}->{new_rotation.value}"
        
        if piece_group in WALL_KICK_DATA and kick_key in WALL_KICK_DATA[piece_group]:
            kicks = WALL_KICK_DATA[piece_group][kick_key]
        else:
            kicks = [(0, 0)]  # Fallback to no kick
        
        # Try each wall kick offset
        for dx, dy in kicks:
            test_piece.x = self.current_piece.x + dx
            test_piece.y = self.current_piece.y + dy
            
            if self.board.is_valid_position(test_piece):
                self.current_piece.x = test_piece.x
                self.current_piece.y = test_piece.y
                self.current_piece.rotation = new_rotation
                self._update_ghost_piece()
                return True
        
        return False
    
    def _hard_drop(self) -> int:
        """Hard drop current piece and return drop distance."""
        if not self.current_piece:
            return 0
            
        drop_distance = 0
        while self._try_move_down():
            drop_distance += 1
        
        return drop_distance
    
    def _hold_piece(self):
        """Hold current piece."""
        if not self.current_piece or not self.can_hold:
            return
        
        if self.held_piece is None:
            # First hold
            self.held_piece = Tetromino(self.current_piece.type)
            self._spawn_piece()
        else:
            # Swap with held piece
            old_held = self.held_piece
            self.held_piece = Tetromino(self.current_piece.type)
            
            # Restore held piece as current
            spawn_x, spawn_y = TETROMINOS[old_held.type]['spawn']
            self.current_piece = Tetromino(old_held.type, spawn_x, spawn_y)
            self._update_ghost_piece()
        
        self.can_hold = False
    
    def _lock_piece(self) -> Dict[str, any]:
        """Lock current piece to board and handle line clears."""
        if not self.current_piece:
            return {}
        
        events = {}
        
        # Place piece on board
        self.board.place_piece(self.current_piece)
        self.stats['pieces_placed'] += 1
        events['piece_locked'] = True
        
        # Check for line clears
        cleared_lines = self.board.clear_lines()
        if cleared_lines:
            events['lines_cleared'] = len(cleared_lines)
            events['cleared_line_indices'] = cleared_lines
            
            # Update statistics and score
            self.lines_cleared += len(cleared_lines)
            self._update_score_for_lines(len(cleared_lines))
            self._update_stats_for_lines(len(cleared_lines))
            
            # Check for level up
            if self.lines_cleared >= self.level * 10:
                self.level += 1
                self._update_drop_speed()
                events['level_up'] = True
        
        # Spawn next piece
        self._spawn_piece()
        
        return events
    
    def _update_score_for_lines(self, line_count: int):
        """Update score based on lines cleared."""
        if line_count == 1:
            self.score += SCORE_VALUES['SINGLE'] * self.level
        elif line_count == 2:
            self.score += SCORE_VALUES['DOUBLE'] * self.level
        elif line_count == 3:
            self.score += SCORE_VALUES['TRIPLE'] * self.level
        elif line_count == 4:
            self.score += SCORE_VALUES['TETRIS'] * self.level
    
    def _update_stats_for_lines(self, line_count: int):
        """Update statistics for line clears."""
        if line_count == 1:
            self.stats['singles'] += 1
        elif line_count == 2:
            self.stats['doubles'] += 1
        elif line_count == 3:
            self.stats['triples'] += 1
        elif line_count == 4:
            self.stats['tetrises'] += 1
    
    def _update_drop_speed(self):
        """Update drop speed based on level."""
        self.drop_interval = max(
            MIN_DROP_INTERVAL,
            int(DROP_INTERVAL_MS * (LEVEL_SPEED_MULTIPLIER ** (self.level - 1)))
        )
    
    def add_garbage(self, lines: int) -> bool:
        """Add garbage lines from attack. Returns True if successful."""
        if self.game_over or lines <= 0:
            return False
        
        self.board.add_garbage_lines(lines)
        self.stats['garbage_received'] += lines
        
        # Check if current piece is now invalid
        if self.current_piece and not self.board.is_valid_position(self.current_piece):
            self.game_over = True
            return False
        
        self._update_ghost_piece()
        return True
    
    def get_attack_power(self, lines_cleared: int) -> int:
        """Calculate attack power based on lines cleared."""
        if lines_cleared == 2:
            return 1
        elif lines_cleared == 3:
            return 2
        elif lines_cleared == 4:
            return 4
        return 0
    
    def reset(self):
        """Reset game to initial state."""
        self.board = TetrisBoard()
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        
        self.current_piece = None
        self.next_piece = None
        self.held_piece = None
        self.can_hold = True
        self.ghost_piece = None
        
        self.last_drop_time = 0
        self.drop_interval = DROP_INTERVAL_MS
        self.last_move_time = {action: 0 for action in self.last_move_time.keys()}
        
        self.stats = {key: 0 for key in self.stats.keys()}
        
        # Initialize pieces
        self._generate_next_piece()
        self._spawn_piece()
    
    def pause(self):
        """Pause the game."""
        self.paused = True
    
    def resume(self):
        """Resume the game."""
        self.paused = False
        # Reset timing to prevent time accumulation
        self.last_drop_time = time.time() * 1000
    
    def get_board_state(self) -> List[List[Optional[Tuple[int, int, int]]]]:
        """Get current board state for rendering."""
        return self.board.grid
    
    def get_game_info(self) -> Dict[str, any]:
        """Get current game information."""
        return {
            'score': self.score,
            'lines': self.lines_cleared,
            'level': self.level,
            'game_over': self.game_over,
            'paused': self.paused,
            'current_piece': self.current_piece,
            'next_piece': self.next_piece,
            'held_piece': self.held_piece,
            'ghost_piece': self.ghost_piece,
            'stats': self.stats.copy(),
            'mode': self.mode
        }
