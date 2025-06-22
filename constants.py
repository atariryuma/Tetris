"""
Game constants and configuration settings.
"""

import pygame

# Window settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60
VSYNC = True

# Game board settings
BLOCK_SIZE = 32
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BOARD_BORDER = 2

# Input settings
INPUT_INTERVAL_MS = 120  # Minimum ms between repeat inputs
ANALOG_DEAD_ZONE = 0.25  # Joystick neutral threshold
MENU_INPUT_DELAY = 200  # Menu navigation delay

# Game timing
DROP_INTERVAL_MS = 800  # Initial drop speed
LEVEL_SPEED_MULTIPLIER = 0.9  # Speed increase per level
MIN_DROP_INTERVAL = 50  # Fastest drop speed
CPU_MOVE_MS = 400  # AI decision interval

# Visual effects
GHOST_ALPHA = 80
LINE_CLEAR_ANIMATION_MS = 300
GARBAGE_ANIMATION_MS = 500
PARTICLE_COUNT = 20

# Audio settings
MASTER_VOLUME = 0.7
MUSIC_VOLUME = 0.5
SFX_VOLUME = 0.8

# Colors (RGB)
class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    LIGHT_GRAY = (192, 192, 192)
    
    # Background colors
    BG_PRIMARY = (26, 26, 46)
    BG_SECONDARY = (15, 52, 96)
    BG_ACCENT = (233, 69, 96)
    
    # UI colors
    UI_BORDER = (255, 255, 255, 51)  # 20% opacity white
    UI_HIGHLIGHT = (252, 163, 17)
    UI_TEXT = (255, 255, 255)
    UI_TEXT_SECONDARY = (170, 170, 170)
    
    # Tetris piece colors
    CYAN = (0, 255, 255)      # I-piece
    BLUE = (0, 0, 255)        # J-piece
    ORANGE = (255, 165, 0)    # L-piece
    YELLOW = (255, 255, 0)    # O-piece
    GREEN = (0, 255, 0)       # S-piece
    PURPLE = (128, 0, 128)    # T-piece
    RED = (255, 0, 0)         # Z-piece
    
    # Special colors
    GARBAGE = (128, 128, 128)
    GHOST = (128, 128, 128, GHOST_ALPHA)

# Tetris pieces (Standard Rotation System - SRS)
TETROMINOS = {
    'I': {
        'shape': [
            ['....', 'IIII', '....', '....'],
            ['..I.', '..I.', '..I.', '..I.'],
            ['....', '....', 'IIII', '....'],
            ['.I..', '.I..', '.I..', '.I..']
        ],
        'color': Colors.CYAN,
        'spawn': (3, 0)
    },
    'O': {
        'shape': [
            ['.OO.', '.OO.', '....', '....'],
            ['.OO.', '.OO.', '....', '....'],
            ['.OO.', '.OO.', '....', '....'],
            ['.OO.', '.OO.', '....', '....']
        ],
        'color': Colors.YELLOW,
        'spawn': (3, 0)
    },
    'T': {
        'shape': [
            ['.T..', '.TT.', '..T.', '....'],
            ['.TT.', '..T.', '.TT.', '....'],
            ['..T.', '..T.', '..T.', '....'],
            ['....', '....', '....', '....']
        ],
        'color': Colors.PURPLE,
        'spawn': (3, 0)
    },
    'S': {
        'shape': [
            ['.SS.', '..S.', '....', '....'],
            ['SS..', '..S.', '.SS.', '....'],
            ['....', '.SS.', 'SS..', '....'],
            ['....', '....', '....', '....']
        ],
        'color': Colors.GREEN,
        'spawn': (3, 0)
    },
    'Z': {
        'shape': [
            ['ZZ..', '..Z.', '....', '....'],
            ['.ZZ.', '.ZZ.', 'ZZ..', '....'],
            ['....', '.Z..', '.ZZ.', '....'],
            ['....', '....', '....', '....']
        ],
        'color': Colors.RED,
        'spawn': (3, 0)
    },
    'J': {
        'shape': [
            ['J...', '.JJ.', '..J.', '....'],
            ['JJJ.', '..J.', 'JJJ.', '....'],
            ['....', '..J.', '...J', '....'],
            ['....', '....', '....', '....']
        ],
        'color': Colors.BLUE,
        'spawn': (3, 0)
    },
    'L': {
        'shape': [
            ['..L.', '.L..', '....', '....'],
            ['LLL.', '.L..', '..L.', '....'],
            ['....', '.LL.', 'LLL.', '....'],
            ['....', '....', '....', '....']
        ],
        'color': Colors.ORANGE,
        'spawn': (3, 0)
    }
}

# Wall kick data for SRS
WALL_KICK_DATA = {
    'JLSTZ': {
        '0->1': [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        '1->0': [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        '1->2': [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        '2->1': [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        '2->3': [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
        '3->2': [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
        '3->0': [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
        '0->3': [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)]
    },
    'I': {
        '0->1': [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        '1->0': [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        '1->2': [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
        '2->1': [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
        '2->3': [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        '3->2': [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        '3->0': [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
        '0->3': [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)]
    }
}

# Scoring system
SCORE_VALUES = {
    'SINGLE': 100,
    'DOUBLE': 300,
    'TRIPLE': 500,
    'TETRIS': 800,
    'SOFT_DROP': 1,
    'HARD_DROP': 2,
    'T_SPIN_SINGLE': 800,
    'T_SPIN_DOUBLE': 1200,
    'T_SPIN_TRIPLE': 1600
}

# Game states
class GameState:
    MENU = 'menu'
    PLAYING = 'playing'
    PAUSED = 'paused'
    GAME_OVER = 'game_over'

# Player modes
class PlayerMode:
    HUMAN = 'human'
    CPU = 'cpu'
    OFF = 'off'

# Debug settings
DEBUG_CONTROLLERS = False
DEBUG_PRINT = False
DEBUG_SHOW_GHOST = True
