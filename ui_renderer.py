"""
UI rendering system for menus, HUD, and visual effects.
"""

import pygame
import math
import time
from typing import List, Tuple, Dict, Optional
from constants import *
from tetris_game import TetrisGame, Tetromino
from font_manager import get_font_manager

class Particle:
    """Simple particle for visual effects."""
    
    def __init__(self, x: float, y: float, vx: float, vy: float, color: Tuple[int, int, int], life: float):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = random.randint(2, 4)
    
    def update(self, dt: float):
        """Update particle position and life."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 200 * dt  # Gravity
        self.life -= dt
    
    def draw(self, surface: pygame.Surface):
        """Draw particle."""
        if self.life <= 0:
            return
        
        alpha = int(255 * (self.life / self.max_life))
        color = (*self.color, alpha)
        
        # Create temporary surface for alpha blending
        temp_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surface, color, (self.size, self.size), self.size)
        surface.blit(temp_surface, (int(self.x - self.size), int(self.y - self.size)))

class ParticleSystem:
    """Manages particle effects."""
    
    def __init__(self):
        self.particles: List[Particle] = []
    
    def add_explosion(self, x: float, y: float, color: Tuple[int, int, int], count: int = 10):
        """Add explosion particles."""
        import random
        
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.5, 1.5)
            
            self.particles.append(Particle(x, y, vx, vy, color, life))
    
    def add_line_clear_effect(self, x: float, y: float, width: float):
        """Add line clear particle effect."""
        import random
        
        for i in range(int(width // 10)):
            px = x + i * 10 + random.uniform(-5, 5)
            py = y + random.uniform(-5, 5)
            vx = random.uniform(-30, 30)
            vy = random.uniform(-100, -50)
            color = (255, 255, 255)  # White particles
            life = random.uniform(0.8, 1.2)
            
            self.particles.append(Particle(px, py, vx, vy, color, life))
    
    def update(self, dt: float):
        """Update all particles."""
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update(dt)
    
    def draw(self, surface: pygame.Surface):
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(surface)

class UIRenderer:
    """Handles all UI rendering including menus, game HUD, and effects."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.particle_system = ParticleSystem()
        
        # Initialize font manager
        self.font_manager = get_font_manager()
        
        # Animation states
        self.line_clear_animations = {}  # game_id -> {lines: [], time: float}
        self.flash_effects = {}  # game_id -> {time: float, color: tuple}
        
        # Menu state
        self.menu_background_offset = 0
    
    def update(self, dt: float):
        """Update UI animations."""
        self.particle_system.update(dt)
        self.menu_background_offset += dt * 20  # Slow scrolling background
        
        # Update line clear animations
        current_time = time.time()
        for game_id in list(self.line_clear_animations.keys()):
            anim = self.line_clear_animations[game_id]
            if current_time - anim['time'] > LINE_CLEAR_ANIMATION_MS / 1000:
                del self.line_clear_animations[game_id]
        
        # Update flash effects
        for game_id in list(self.flash_effects.keys()):
            flash = self.flash_effects[game_id]
            if current_time - flash['time'] > 0.2:  # Flash duration
                del self.flash_effects[game_id]
    
    def draw_background(self):
        """Draw animated background."""
        # Gradient background
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            color = (
                int(Colors.BG_PRIMARY[0] * (1 - ratio) + Colors.BG_SECONDARY[0] * ratio),
                int(Colors.BG_PRIMARY[1] * (1 - ratio) + Colors.BG_SECONDARY[1] * ratio),
                int(Colors.BG_PRIMARY[2] * (1 - ratio) + Colors.BG_SECONDARY[2] * ratio)
            )
            pygame.draw.line(self.screen, color, (0, y), (self.screen_width, y))
        
        # Animated grid pattern
        grid_size = 50
        offset_x = int(self.menu_background_offset) % grid_size
        offset_y = int(self.menu_background_offset * 0.7) % grid_size
        
        for x in range(-grid_size, self.screen_width + grid_size, grid_size):
            for y in range(-grid_size, self.screen_height + grid_size, grid_size):
                alpha = 20
                color = (*Colors.UI_HIGHLIGHT[:3], alpha)
                rect = pygame.Rect(x + offset_x, y + offset_y, 2, 2)
                pygame.draw.rect(self.screen, color[:3], rect)
    
    def draw_main_menu(self, selected_index: int, player_modes: List[str]):
        """Draw main menu."""
        self.draw_background()
        
        # Title
        title_text = self.font_manager.render_text("三人対戦テトリス NEO", "title", 48, Colors.UI_HIGHLIGHT)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.font_manager.render_text("Python Edition", "ui", 32, Colors.UI_TEXT)
        subtitle_rect = subtitle_text.get_rect(center=(self.screen_width // 2, 140))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Player setup
        y_start = 200
        player_names = ["PLAYER 1", "PLAYER 2", "PLAYER 3"]
        mode_texts = {"human": "参加する", "cpu": "CPU", "off": "参加しない"}
        
        for i, (name, mode) in enumerate(zip(player_names, player_modes)):
            y = y_start + i * 80
            
            # Player name
            name_text = self.font_manager.render_text(name, "ui", 28, Colors.UI_HIGHLIGHT)
            name_rect = name_text.get_rect(center=(self.screen_width // 2 - 100, y))
            self.screen.blit(name_text, name_rect)
            
            # Mode button
            mode_color = Colors.UI_HIGHLIGHT if selected_index == i else Colors.UI_TEXT
            if selected_index == i:
                # Highlight selected
                highlight_rect = pygame.Rect(self.screen_width // 2 - 50, y - 20, 200, 40)
                pygame.draw.rect(self.screen, Colors.UI_HIGHLIGHT, highlight_rect, 2)
            
            mode_text = self.font_manager.render_text(mode_texts[mode], "japanese", 28, mode_color)
            mode_rect = mode_text.get_rect(center=(self.screen_width // 2 + 50, y))
            self.screen.blit(mode_text, mode_rect)
        
        # Start button
        start_y = y_start + 3 * 80 + 40
        start_color = Colors.UI_HIGHLIGHT if selected_index == 3 else Colors.UI_TEXT
        if selected_index == 3:
            highlight_rect = pygame.Rect(self.screen_width // 2 - 100, start_y - 20, 200, 40)
            pygame.draw.rect(self.screen, Colors.UI_HIGHLIGHT, highlight_rect, 2)
        
        start_text = self.font_manager.render_text("ゲームスタート", "japanese", 28, start_color)
        start_rect = start_text.get_rect(center=(self.screen_width // 2, start_y))
        self.screen.blit(start_text, start_rect)
        
        # Controls info
        controls_y = self.screen_height - 80
        controls = [
            "矢印キー: 移動・選択  Z/X: 回転  Enter: 決定  ESC: 一時停止",
            "ゲームパッド対応: Xbox, PlayStation, Nintendo Switch Pro"
        ]
        
        for i, control_text in enumerate(controls):
            text = self.font_manager.render_text(control_text, "japanese", 18, Colors.UI_TEXT_SECONDARY)
            text_rect = text.get_rect(center=(self.screen_width // 2, controls_y + i * 25))
            self.screen.blit(text, text_rect)
    
    def draw_game_hud(self, games: List[TetrisGame], active_players: List[int]):
        """Draw game HUD for all active players."""
        self.draw_background()
        
        if not active_players:
            return
        
        # Calculate layout
        num_players = len(active_players)
        board_width = BOARD_WIDTH * BLOCK_SIZE
        board_height = BOARD_HEIGHT * BLOCK_SIZE
        
        if num_players == 1:
            positions = [(self.screen_width // 2 - board_width // 2, 50)]
        elif num_players == 2:
            spacing = 50
            total_width = board_width * 2 + spacing
            start_x = (self.screen_width - total_width) // 2
            positions = [
                (start_x, 50),
                (start_x + board_width + spacing, 50)
            ]
        else:  # 3 players
            spacing = 30
            total_width = board_width * 3 + spacing * 2
            start_x = max(10, (self.screen_width - total_width) // 2)
            positions = [
                (start_x, 50),
                (start_x + board_width + spacing, 50),
                (start_x + (board_width + spacing) * 2, 50)
            ]
        
        # Draw each player's area
        for i, player_id in enumerate(active_players):
            if i < len(positions):
                game = games[player_id - 1]
                x, y = positions[i]
                self.draw_player_area(game, x, y, player_id)
        
        # Draw particles
        self.particle_system.draw(self.screen)
    
    def draw_player_area(self, game: TetrisGame, x: int, y: int, player_id: int):
        """Draw individual player area."""
        board_width = BOARD_WIDTH * BLOCK_SIZE
        board_height = BOARD_HEIGHT * BLOCK_SIZE
        
        # Player title
        title = f"PLAYER {player_id}"
        if game.mode == PlayerMode.CPU:
            title += " (CPU)"
        
        title_color = Colors.UI_HIGHLIGHT if not game.game_over else Colors.RED
        title_text = self.font_manager.render_text(title, "ui", 24, title_color)
        title_rect = title_text.get_rect(center=(x + board_width // 2, y - 20))
        self.screen.blit(title_text, title_rect)
        
        # Game board
        self.draw_game_board(game, x, y)
        
        # Side panel
        panel_x = x + board_width + 10
        panel_y = y
        self.draw_side_panel(game, panel_x, panel_y)
        
        # Game over overlay
        if game.game_over:
            self.draw_game_over_overlay(x, y, board_width, board_height)
    
    def draw_game_board(self, game: TetrisGame, x: int, y: int):
        """Draw the Tetris game board."""
        # Board background
        board_rect = pygame.Rect(x, y, BOARD_WIDTH * BLOCK_SIZE, BOARD_HEIGHT * BLOCK_SIZE)
        pygame.draw.rect(self.screen, Colors.BLACK, board_rect)
        pygame.draw.rect(self.screen, Colors.UI_BORDER[:3], board_rect, BOARD_BORDER)
        
        # Grid lines (subtle)
        for i in range(1, BOARD_WIDTH):
            line_x = x + i * BLOCK_SIZE
            pygame.draw.line(self.screen, Colors.DARK_GRAY, 
                           (line_x, y), (line_x, y + BOARD_HEIGHT * BLOCK_SIZE))
        
        for i in range(1, BOARD_HEIGHT):
            line_y = y + i * BLOCK_SIZE
            pygame.draw.line(self.screen, Colors.DARK_GRAY,
                           (x, line_y), (x + BOARD_WIDTH * BLOCK_SIZE, line_y))
        
        # Placed blocks
        board_state = game.get_board_state()
        for row_idx, row in enumerate(board_state):
            for col_idx, color in enumerate(row):
                if color:
                    block_x = x + col_idx * BLOCK_SIZE
                    block_y = y + row_idx * BLOCK_SIZE
                    self.draw_block(block_x, block_y, color)
        
        # Ghost piece
        if game.ghost_piece and DEBUG_SHOW_GHOST:
            self.draw_piece(game.ghost_piece, x, y, alpha=GHOST_ALPHA)
        
        # Current piece
        if game.current_piece:
            self.draw_piece(game.current_piece, x, y)
        
        # Line clear animation
        if game.player_id in self.line_clear_animations:
            self.draw_line_clear_effect(x, y, game.player_id)
        
        # Flash effect
        if game.player_id in self.flash_effects:
            self.draw_flash_effect(x, y, BOARD_WIDTH * BLOCK_SIZE, 
                                 BOARD_HEIGHT * BLOCK_SIZE, game.player_id)
    
    def draw_block(self, x: int, y: int, color: Tuple[int, int, int], alpha: int = 255):
        """Draw a single Tetris block."""
        if alpha < 255:
            # Create surface with alpha
            block_surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
            block_color = (*color, alpha)
            pygame.draw.rect(block_surface, block_color, (0, 0, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(block_surface, Colors.BLACK, (0, 0, BLOCK_SIZE, BLOCK_SIZE), 1)
            self.screen.blit(block_surface, (x, y))
        else:
            # Regular opaque block
            pygame.draw.rect(self.screen, color, (x, y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.screen, Colors.BLACK, (x, y, BLOCK_SIZE, BLOCK_SIZE), 1)
    
    def draw_piece(self, piece: Tetromino, board_x: int, board_y: int, alpha: int = 255):
        """Draw a Tetris piece."""
        blocks = piece.get_blocks()
        for block_x, block_y in blocks:
            if 0 <= block_x < BOARD_WIDTH and 0 <= block_y < BOARD_HEIGHT:
                pixel_x = board_x + block_x * BLOCK_SIZE
                pixel_y = board_y + block_y * BLOCK_SIZE
                self.draw_block(pixel_x, pixel_y, piece.color, alpha)
    
    def draw_side_panel(self, game: TetrisGame, x: int, y: int):
        """Draw side panel with score, next piece, etc."""
        panel_width = 120
        
        # Score
        score_text = self.font_manager.render_text("SCORE", "ui", 16, Colors.UI_HIGHLIGHT)
        self.screen.blit(score_text, (x, y))
        
        score_value = self.font_manager.render_text(str(game.score), "score", 16, Colors.UI_TEXT)
        self.screen.blit(score_value, (x, y + 20))
        
        # Lines
        lines_text = self.font_manager.render_text("LINES", "ui", 16, Colors.UI_HIGHLIGHT)
        self.screen.blit(lines_text, (x, y + 50))
        
        lines_value = self.font_manager.render_text(str(game.lines_cleared), "score", 16, Colors.UI_TEXT)
        self.screen.blit(lines_value, (x, y + 70))
        
        # Level
        level_text = self.font_manager.render_text("LEVEL", "ui", 16, Colors.UI_HIGHLIGHT)
        self.screen.blit(level_text, (x, y + 100))
        
        level_value = self.font_manager.render_text(str(game.level), "score", 16, Colors.UI_TEXT)
        self.screen.blit(level_value, (x, y + 120))
        
        # Next piece
        next_y = y + 160
        next_text = self.font_manager.render_text("NEXT", "ui", 16, Colors.UI_HIGHLIGHT)
        self.screen.blit(next_text, (x, next_y))
        
        if game.next_piece:
            # Draw next piece in small preview
            preview_x = x + 10
            preview_y = next_y + 25
            self.draw_piece_preview(game.next_piece, preview_x, preview_y, scale=0.6)
        
        # Held piece
        if game.held_piece:
            hold_y = next_y + 80
            hold_text = self.font_manager.render_text("HOLD", "ui", 16, Colors.UI_HIGHLIGHT)
            self.screen.blit(hold_text, (x, hold_y))
            
            preview_x = x + 10
            preview_y = hold_y + 25
            alpha = 255 if game.can_hold else 128
            self.draw_piece_preview(game.held_piece, preview_x, preview_y, scale=0.6, alpha=alpha)
    
    def draw_piece_preview(self, piece: Tetromino, x: int, y: int, scale: float = 1.0, alpha: int = 255):
        """Draw piece preview."""
        shape = piece.get_shape()
        block_size = int(BLOCK_SIZE * scale)
        
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell != '.' and cell != ' ':
                    block_x = x + col_idx * block_size
                    block_y = y + row_idx * block_size
                    
                    if alpha < 255:
                        block_surface = pygame.Surface((block_size, block_size), pygame.SRCALPHA)
                        block_color = (*piece.color, alpha)
                        pygame.draw.rect(block_surface, block_color, (0, 0, block_size, block_size))
                        pygame.draw.rect(block_surface, Colors.BLACK, (0, 0, block_size, block_size), 1)
                        self.screen.blit(block_surface, (block_x, block_y))
                    else:
                        pygame.draw.rect(self.screen, piece.color, (block_x, block_y, block_size, block_size))
                        pygame.draw.rect(self.screen, Colors.BLACK, (block_x, block_y, block_size, block_size), 1)
    
    def draw_game_over_overlay(self, x: int, y: int, width: int, height: int):
        """Draw game over overlay."""
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (x, y))
        
        text = self.font_manager.render_text("GAME OVER", "title", 36, Colors.RED)
        text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text, text_rect)
    
    def draw_pause_menu(self):
        """Draw pause menu."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Menu box
        menu_width = 300
        menu_height = 200
        menu_x = (self.screen_width - menu_width) // 2
        menu_y = (self.screen_height - menu_height) // 2
        
        pygame.draw.rect(self.screen, Colors.BG_SECONDARY, (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(self.screen, Colors.UI_BORDER[:3], (menu_x, menu_y, menu_width, menu_height), 2)
        
        # Title
        title_text = self.font_manager.render_text("一時停止", "japanese", 40, Colors.UI_HIGHLIGHT)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, menu_y + 50))
        self.screen.blit(title_text, title_rect)
        
        # Instructions
        instructions = [
            "ESCまたはSTART: 再開",
            "R: リスタート",
            "Q: 終了"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font_manager.render_text(instruction, "japanese", 20, Colors.UI_TEXT)
            text_rect = text.get_rect(center=(self.screen_width // 2, menu_y + 100 + i * 25))
            self.screen.blit(text, text_rect)
    
    def draw_game_over_screen(self, winner: Optional[int], games: List[TetrisGame]):
        """Draw game over screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Winner announcement
        if winner:
            winner_text = f"PLAYER {winner} WINS!"
            color = Colors.UI_HIGHLIGHT
        else:
            winner_text = "DRAW!"
            color = Colors.UI_TEXT
        
        title = self.font_manager.render_text(winner_text, "title", 48, color)
        title_rect = title.get_rect(center=(self.screen_width // 2, 200))
        self.screen.blit(title, title_rect)
        
        # Statistics
        stats_y = 300
        for i, game in enumerate(games):
            if game.mode != PlayerMode.OFF:
                player_text = f"Player {i + 1}: {game.score} points, {game.lines_cleared} lines"
                text = self.font_manager.render_text(player_text, "ui", 24, Colors.UI_TEXT)
                text_rect = text.get_rect(center=(self.screen_width // 2, stats_y + i * 30))
                self.screen.blit(text, text_rect)
        
        # Restart instruction
        restart_text = self.font_manager.render_text("Press R to restart or ESC to menu", "ui", 20, Colors.UI_TEXT_SECONDARY)
        restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height - 100))
        self.screen.blit(restart_text, restart_rect)
    
    def add_line_clear_animation(self, game_id: int, cleared_lines: List[int]):
        """Add line clear animation."""
        self.line_clear_animations[game_id] = {
            'lines': cleared_lines,
            'time': time.time()
        }
        
        # Add particle effects
        for line_y in cleared_lines:
            screen_y = 50 + line_y * BLOCK_SIZE  # Approximate screen position
            self.particle_system.add_line_clear_effect(100, screen_y, BOARD_WIDTH * BLOCK_SIZE)
    
    def add_flash_effect(self, game_id: int, color: Tuple[int, int, int] = Colors.WHITE):
        """Add flash effect."""
        self.flash_effects[game_id] = {
            'color': color,
            'time': time.time()
        }
    
    def draw_line_clear_effect(self, board_x: int, board_y: int, game_id: int):
        """Draw line clear animation effect."""
        if game_id not in self.line_clear_animations:
            return
        
        anim = self.line_clear_animations[game_id]
        elapsed = time.time() - anim['time']
        progress = elapsed / (LINE_CLEAR_ANIMATION_MS / 1000)
        
        if progress > 1.0:
            return
        
        # Flashing white overlay on cleared lines
        alpha = int(255 * (1 - progress) * math.sin(progress * math.pi * 6))
        
        for line_y in anim['lines']:
            overlay = pygame.Surface((BOARD_WIDTH * BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, alpha))
            self.screen.blit(overlay, (board_x, board_y + line_y * BLOCK_SIZE))
    
    def draw_flash_effect(self, x: int, y: int, width: int, height: int, game_id: int):
        """Draw flash effect."""
        if game_id not in self.flash_effects:
            return
        
        flash = self.flash_effects[game_id]
        elapsed = time.time() - flash['time']
        progress = elapsed / 0.2  # Flash duration
        
        if progress > 1.0:
            return
        
        alpha = int(100 * (1 - progress))
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((*flash['color'], alpha))
        self.screen.blit(overlay, (x, y))
