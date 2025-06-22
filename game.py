"""
Complete Tetris Game Implementation
Professional-grade game engine with clean architecture.
"""

import pygame
import random
import time
from enum import Enum
from typing import List, Tuple, Optional, Dict
from audio import SimpleAudio

# Game Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60

BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BLOCK_SIZE = 30

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)

# Tetromino colors
PIECE_COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': PURPLE,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE
}

# Tetromino shapes
TETROMINOES = {
    'I': [
        ['....', 'IIII', '....', '....'],
        ['..I.', '..I.', '..I.', '..I.'],
        ['....', '....', 'IIII', '....'],
        ['.I..', '.I..', '.I..', '.I..']
    ],
    'O': [
        ['.OO.', '.OO.', '....', '....'],
        ['.OO.', '.OO.', '....', '....'],
        ['.OO.', '.OO.', '....', '....'],
        ['.OO.', '.OO.', '....', '....']
    ],
    'T': [
        ['.T..', '.TT.', '..T.', '....'],
        ['.TT.', '..T.', '.TT.', '....'],
        ['..T.', '..T.', '..T.', '....'],
        ['....', '....', '....', '....']
    ],
    'S': [
        ['.SS.', '..S.', '....', '....'],
        ['SS..', '..S.', '.SS.', '....'],
        ['....', '.SS.', 'SS..', '....'],
        ['....', '....', '....', '....']
    ],
    'Z': [
        ['ZZ..', '..Z.', '....', '....'],
        ['.ZZ.', '.ZZ.', 'ZZ..', '....'],
        ['....', '.Z..', '.ZZ.', '....'],
        ['....', '....', '....', '....']
    ],
    'J': [
        ['J...', '.JJ.', '..J.', '....'],
        ['JJJ.', '..J.', 'JJJ.', '....'],
        ['....', '..J.', '...J', '....'],
        ['....', '....', '....', '....']
    ],
    'L': [
        ['..L.', '.L..', '....', '....'],
        ['LLL.', '.L..', '..L.', '....'],
        ['....', '.LL.', 'LLL.', '....'],
        ['....', '....', '....', '....']
    ]
}

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"

class Piece:
    """Represents a Tetris piece."""
    
    def __init__(self, piece_type: str, x: int = 4, y: int = 0):
        self.type = piece_type
        self.x = x
        self.y = y
        self.rotation = 0
        self.color = PIECE_COLORS[piece_type]
    
    def get_shape(self) -> List[str]:
        """Get current shape based on rotation."""
        return TETROMINOES[self.type][self.rotation]
    
    def get_blocks(self) -> List[Tuple[int, int]]:
        """Get list of block positions."""
        blocks = []
        shape = self.get_shape()
        
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell != '.' and cell != ' ':
                    blocks.append((self.x + col_idx, self.y + row_idx))
        
        return blocks
    
    def copy(self) -> 'Piece':
        """Create a copy of this piece."""
        piece = Piece(self.type, self.x, self.y)
        piece.rotation = self.rotation
        return piece

class TetrisBoard:
    """Game board for Tetris."""
    
    def __init__(self):
        self.width = BOARD_WIDTH
        self.height = BOARD_HEIGHT
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
    
    def is_valid_position(self, piece: Piece) -> bool:
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
    
    def place_piece(self, piece: Piece):
        """Place piece on the board."""
        blocks = piece.get_blocks()
        
        for x, y in blocks:
            if 0 <= y < self.height and 0 <= x < self.width:
                self.grid[y][x] = piece.color
    
    def clear_lines(self) -> int:
        """Clear completed lines and return count."""
        lines_cleared = 0
        y = self.height - 1
        
        while y >= 0:
            if all(cell is not None for cell in self.grid[y]):
                # Clear this line
                del self.grid[y]
                self.grid.insert(0, [None for _ in range(self.width)])
                lines_cleared += 1
            else:
                y -= 1
        
        return lines_cleared
    
    def is_game_over(self) -> bool:
        """Check if game is over."""
        return any(cell is not None for cell in self.grid[0])

class InputManager:
    """Handles keyboard and controller input."""
    
    def __init__(self):
        self.keys_pressed = set()
        self.keys_just_pressed = set()
        self.controllers = []
        
        # Initialize controllers
        pygame.joystick.init()
        for i in range(pygame.joystick.get_count()):
            controller = pygame.joystick.Joystick(i)
            controller.init()
            self.controllers.append(controller)
            print(f"Controller {i}: {controller.get_name()}")
    
    def update(self):
        """Update input state."""
        self.keys_just_pressed.clear()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                self.keys_just_pressed.add(event.key)
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
        
        return True
    
    def is_pressed(self, key: int) -> bool:
        """Check if key is currently pressed."""
        return key in self.keys_pressed
    
    def is_just_pressed(self, key: int) -> bool:
        """Check if key was just pressed this frame."""
        return key in self.keys_just_pressed

class Renderer:
    """Handles all rendering."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
    
    def clear(self):
        """Clear the screen."""
        self.screen.fill(BLACK)
    
    def draw_board(self, board: TetrisBoard, offset_x: int = 50, offset_y: int = 50):
        """Draw the game board."""
        # Draw board background
        board_rect = pygame.Rect(offset_x, offset_y, 
                                board.width * BLOCK_SIZE, 
                                board.height * BLOCK_SIZE)
        pygame.draw.rect(self.screen, GRAY, board_rect, 2)
        
        # Draw placed blocks
        for y in range(board.height):
            for x in range(board.width):
                if board.grid[y][x] is not None:
                    self.draw_block(x, y, board.grid[y][x], offset_x, offset_y)
    
    def draw_piece(self, piece: Piece, offset_x: int = 50, offset_y: int = 50):
        """Draw a piece."""
        blocks = piece.get_blocks()
        for x, y in blocks:
            if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
                self.draw_block(x, y, piece.color, offset_x, offset_y)
    
    def draw_block(self, x: int, y: int, color: Tuple[int, int, int], 
                   offset_x: int = 0, offset_y: int = 0):
        """Draw a single block."""
        rect = pygame.Rect(offset_x + x * BLOCK_SIZE, 
                          offset_y + y * BLOCK_SIZE,
                          BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, WHITE, rect, 1)
    
    def draw_text(self, text: str, x: int, y: int, font=None, color=WHITE):
        """Draw text at specified position."""
        if font is None:
            font = self.font_medium
        
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
    
    def draw_menu(self):
        """Draw main menu."""
        title = "TETRIS"
        subtitle = "Press SPACE to start"
        
        self.draw_text(title, WINDOW_WIDTH // 2 - 80, 200, self.font_large)
        self.draw_text(subtitle, WINDOW_WIDTH // 2 - 120, 300, self.font_medium)
        self.draw_text("Controls:", 50, 400, self.font_medium)
        self.draw_text("← → : Move", 50, 430, self.font_small)
        self.draw_text("↓ : Soft drop", 50, 450, self.font_small)
        self.draw_text("↑ : Hard drop", 50, 470, self.font_small)
        self.draw_text("Z : Rotate", 50, 490, self.font_small)
        self.draw_text("ESC : Pause", 50, 510, self.font_small)
    
    def draw_game_over(self, score: int):
        """Draw game over screen."""
        self.draw_text("GAME OVER", WINDOW_WIDTH // 2 - 100, 200, self.font_large, RED)
        self.draw_text(f"Score: {score}", WINDOW_WIDTH // 2 - 60, 300, self.font_medium)
        self.draw_text("Press R to restart", WINDOW_WIDTH // 2 - 100, 350, self.font_medium)

class TetrisGame:
    """Main game class."""
    
    def __init__(self):
        # Initialize display
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        
        # Game systems
        self.input_manager = InputManager()
        self.renderer = Renderer(self.screen)
        self.audio = SimpleAudio()
        
        # Game state
        self.state = GameState.MENU
        self.board = TetrisBoard()
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.fall_time = 0
        self.fall_speed = 500  # milliseconds
        
        # Generate first pieces
        self.spawn_new_piece()
        self.generate_next_piece()
    
    def spawn_new_piece(self):
        """Spawn a new piece."""
        if self.next_piece:
            self.current_piece = self.next_piece
        else:
            piece_type = random.choice(list(TETROMINOES.keys()))
            self.current_piece = Piece(piece_type)
        
        self.generate_next_piece()
        
        # Check for game over
        if not self.board.is_valid_position(self.current_piece):
            self.state = GameState.GAME_OVER
            self.audio.play('game_over')
    
    def generate_next_piece(self):
        """Generate the next piece."""
        piece_type = random.choice(list(TETROMINOES.keys()))
        self.next_piece = Piece(piece_type)
    
    def move_piece(self, dx: int, dy: int) -> bool:
        """Try to move the current piece."""
        if not self.current_piece:
            return False
        
        test_piece = self.current_piece.copy()
        test_piece.x += dx
        test_piece.y += dy
        
        if self.board.is_valid_position(test_piece):
            self.current_piece.x = test_piece.x
            self.current_piece.y = test_piece.y
            self.audio.play('move')
            return True
        
        return False
    
    def rotate_piece(self) -> bool:
        """Try to rotate the current piece."""
        if not self.current_piece:
            return False
        
        test_piece = self.current_piece.copy()
        test_piece.rotation = (test_piece.rotation + 1) % 4
        
        if self.board.is_valid_position(test_piece):
            self.current_piece.rotation = test_piece.rotation
            self.audio.play('rotate')
            return True
        
        return False
    
    def hard_drop(self):
        """Drop piece to bottom."""
        if not self.current_piece:
            return
        
        while self.move_piece(0, 1):
            self.score += 2
        
        self.audio.play('drop')
        self.lock_piece()
    
    def lock_piece(self):
        """Lock the current piece to the board."""
        if not self.current_piece:
            return
        
        self.board.place_piece(self.current_piece)
        
        # Clear lines
        lines = self.board.clear_lines()
        if lines > 0:
            self.lines_cleared += lines
            self.score += lines * 100 * self.level
            self.audio.play('line')
            
            # Increase level every 10 lines
            new_level = (self.lines_cleared // 10) + 1
            if new_level > self.level:
                self.level = new_level
                self.fall_speed = max(50, self.fall_speed - 50)
        
        # Spawn new piece
        self.spawn_new_piece()
    
    def update_game(self, dt: int):
        """Update game logic."""
        if self.state != GameState.PLAYING:
            return
        
        # Handle falling
        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            if not self.move_piece(0, 1):
                self.lock_piece()
            self.fall_time = 0
    
    def handle_input(self):
        """Handle game input."""
        if not self.input_manager.update():
            return False
        
        if self.state == GameState.MENU:
            if self.input_manager.is_just_pressed(pygame.K_SPACE):
                self.start_new_game()
        
        elif self.state == GameState.PLAYING:
            if self.input_manager.is_just_pressed(pygame.K_ESCAPE):
                self.state = GameState.PAUSED
            
            elif self.input_manager.is_just_pressed(pygame.K_LEFT):
                self.move_piece(-1, 0)
            
            elif self.input_manager.is_just_pressed(pygame.K_RIGHT):
                self.move_piece(1, 0)
            
            elif self.input_manager.is_just_pressed(pygame.K_DOWN):
                if self.move_piece(0, 1):
                    self.score += 1
            
            elif self.input_manager.is_just_pressed(pygame.K_UP):
                self.hard_drop()
            
            elif self.input_manager.is_just_pressed(pygame.K_z):
                self.rotate_piece()
        
        elif self.state == GameState.PAUSED:
            if self.input_manager.is_just_pressed(pygame.K_ESCAPE):
                self.state = GameState.PLAYING
        
        elif self.state == GameState.GAME_OVER:
            if self.input_manager.is_just_pressed(pygame.K_r):
                self.start_new_game()
        
        return True
    
    def start_new_game(self):
        """Start a new game."""
        self.state = GameState.PLAYING
        self.board = TetrisBoard()
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.fall_time = 0
        self.fall_speed = 500
        self.spawn_new_piece()
        self.generate_next_piece()
    
    def render(self):
        """Render the game."""
        self.renderer.clear()
        
        if self.state == GameState.MENU:
            self.renderer.draw_menu()
        
        elif self.state in [GameState.PLAYING, GameState.PAUSED]:
            # Draw game board
            self.renderer.draw_board(self.board)
            
            # Draw current piece
            if self.current_piece:
                self.renderer.draw_piece(self.current_piece)
            
            # Draw UI
            self.renderer.draw_text(f"Score: {self.score}", 400, 100)
            self.renderer.draw_text(f"Lines: {self.lines_cleared}", 400, 130)
            self.renderer.draw_text(f"Level: {self.level}", 400, 160)
            
            # Draw next piece
            if self.next_piece:
                self.renderer.draw_text("Next:", 400, 200)
                next_piece = self.next_piece.copy()
                next_piece.x = 15
                next_piece.y = 8
                self.renderer.draw_piece(next_piece)
            
            if self.state == GameState.PAUSED:
                self.renderer.draw_text("PAUSED", WINDOW_WIDTH // 2 - 50, 300, 
                                      self.renderer.font_large, YELLOW)
        
        elif self.state == GameState.GAME_OVER:
            self.renderer.draw_board(self.board)
            if self.current_piece:
                self.renderer.draw_piece(self.current_piece)
            self.renderer.draw_game_over(self.score)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        print("Tetris Game Started!")
        print("Controls: Arrow keys to move, Z to rotate, Space to start")
        
        running = True
        last_time = pygame.time.get_ticks()
        
        while running:
            current_time = pygame.time.get_ticks()
            dt = current_time - last_time
            last_time = current_time
            
            # Handle input
            if not self.handle_input():
                running = False
            
            # Update game
            self.update_game(dt)
            
            # Render
            self.render()
            
            # Maintain framerate
            self.clock.tick(FPS)
        
        # Cleanup
        self.audio.cleanup()
        print("Game ended. Thanks for playing!")