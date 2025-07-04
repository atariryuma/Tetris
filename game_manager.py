"""
Main game manager that coordinates all systems.
"""

import pygame
import time
from typing import List, Dict, Optional
from constants import *
from tetris_game import TetrisGame
from input_manager import GamepadManager, UINavigationManager, Action
from audio_manager import AudioManager
from ui_renderer import UIRenderer
from cpu_ai import AdaptiveCPU
from debug_logger import get_debug_logger

# safe_events は main.py 経由でなく utils から直接読み込む
# ただしここでは event_source 経由で呼び出すため、utils をインポート不要

class GameManager:
    """Main game manager that coordinates all game systems."""
    
    def __init__(self, screen: pygame.Surface, event_source=None):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = False  # Will be set to True in run()
        self.state = GameState.MENU
        self.debug = get_debug_logger()
        
        # Use provided event_source or fall back to pygame.event.get
        self.event_source = event_source or pygame.event.get
        
        # Initialize systems
        if self.debug:
            self.debug.log_info("Initializing GameManager systems", "GameManager.__init__")
        
        self.gamepad_manager = GamepadManager()
        self.ui_navigation = UINavigationManager(self.gamepad_manager)
        self.audio_manager = AudioManager()
        self.ui_renderer = UIRenderer(screen)
        
        # Game state
        self.games: List[TetrisGame] = []
        self.active_players: List[int] = []
        self.player_modes = [PlayerMode.HUMAN, PlayerMode.CPU, PlayerMode.OFF]
        self.cpu_controllers: Dict[int, AdaptiveCPU] = {}
        
        # Menu state
        self.menu_selection = 0
        self.menu_items = 4  # 3 players + start button
        
        # Timing
        self.last_time = time.time()
        self.paused_time = 0
        
        # Key states for proper input handling
        self.keys_pressed = {}
        self.keys_just_pressed = {}
        
        # Initialize audio
        self.audio_manager.play_bgm('menu_music')
    
    def run(self):
        """Main game loop using safe event polling."""
        print("Game started! Use controllers or keyboard to play.")
        print("Controls: Arrow keys to move, Z/X to rotate, ESC to pause")
        
        clock = pygame.time.Clock()
        self.running = True
        frame_count = 0
        last_update_time = time.time()
        
        game_start_time = time.time()
        max_hang_time = 5.0  # Maximum time between frames before considering hung
        last_frame_time = time.time()
        
        while self.running:
            current_time = time.time()
            delta_time = current_time - self.last_time
            self.last_time = current_time
            
            # Emergency hang detection (force quit if frames take too long)
            time_since_last_frame = current_time - last_frame_time
            if time_since_last_frame > max_hang_time:
                print(f"[ERROR] Game appears hung (no frame for {time_since_last_frame:.1f}s), force quitting...")
                self.running = False
                break
            
            # Safety check for hung loops (reduced frequency)
            if current_time - last_update_time > 10.0:  # 10 second timeout
                print("[WARN] Game loop may be hanging - continuing...")
                last_update_time = current_time
            
            # Reset just_pressed keys each frame
            self.keys_just_pressed = {}

            try:
                # Process all pending events
                self.handle_events()
                
                # Game update and render calls
                self.update(delta_time)
                self.draw(self.screen)
                
                # Display update
                pygame.display.flip()
                
            except Exception as e:
                print(f"[ERROR] Game loop error: {e}")
                # Continue rather than crash
                
            # Maintain target FPS
            try:
                clock.tick(FPS)
            except Exception:
                time.sleep(1.0 / FPS)  # Fallback timing
            
            frame_count += 1
            last_frame_time = time.time()  # Update frame completion time
            
            # Log frame info to debug
            if self.debug:
                fps = self.clock.get_fps() if hasattr(self, 'clock') else 0
                self.debug.log_frame_info(frame_count, fps, self.state.value if hasattr(self.state, 'value') else str(self.state))
            
            if frame_count % 1800 == 0:  # Every 30 seconds at 60 FPS
                fps = self.clock.get_fps() if hasattr(self, 'clock') else 0
                print(f"Game running: frame {frame_count}, state: {self.state}, FPS: {fps:.1f}")
                if self.debug:
                    controller_count = len(self.gamepad_manager.joysticks)
                    self.debug.log_info(f"Status: frame {frame_count}, state: {self.state}, FPS: {fps:.1f}, controllers: {controller_count}", "periodic_status")
        
        # Cleanup
        print("Game ending, cleaning up...")
        try:
            self.audio_manager.cleanup()
        except Exception as e:
            print(f"Audio cleanup error: {e}")
        
        print("Game ended successfully")

    def handle_events(self):
        """Process all pending pygame events safely."""
        try:
            events = self.event_source()
        except Exception as e:
            if self.debug:
                self.debug.log_error(e, "handle_events.event_source")
            events = []

        for event in events:
            if self.debug:
                self.debug.log_pygame_event(event)
            
            if event.type == pygame.QUIT:
                if self.debug:
                    self.debug.log_info("QUIT event received", "handle_events")
                self.running = False
            else:
                self.handle_event(event)

    def handle_event(self, event):
        """Handle a single pygame event."""
        if event.type == pygame.QUIT:
            self.running = False
        
        elif event.type == pygame.KEYDOWN:
            self.keys_pressed[event.key] = True
            self.keys_just_pressed[event.key] = True
            
            # Global shortcuts
            if event.key == pygame.K_F1:
                print("Volume info:", self.audio_manager.get_volume_info())
            elif event.key == pygame.K_F2:
                current = self.audio_manager.get_volume_info()
                new_volume = min(1.0, current['master'] + 0.1)
                self.audio_manager.set_master_volume(new_volume)
                print(f"Master volume: {new_volume:.1f}")
            elif event.key == pygame.K_F3:
                current = self.audio_manager.get_volume_info()
                new_volume = max(0.0, current['master'] - 0.1)
                self.audio_manager.set_master_volume(new_volume)
                print(f"Master volume: {new_volume:.1f}")
            
            # State-specific shortcuts
            elif self.state == GameState.MENU:
                self.handle_menu_input(event.key)
            elif self.state == GameState.PLAYING:
                if event.key == pygame.K_ESCAPE:
                    self.pause_game()
                elif event.key == pygame.K_r:
                    self.restart_game()
            elif self.state == GameState.PAUSED:
                if event.key == pygame.K_ESCAPE:
                    self.resume_game()
                elif event.key == pygame.K_r:
                    self.restart_game()
                elif event.key == pygame.K_q:
                    self.state = GameState.MENU
            elif self.state == GameState.GAME_OVER:
                if event.key == pygame.K_r:
                    self.restart_game()
                elif event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
        
        elif event.type == pygame.KEYUP:
            self.keys_pressed[event.key] = False
    
    def handle_menu_input(self, key: int):
        """Handle menu input."""
        if key == pygame.K_UP:
            self.menu_selection = (self.menu_selection - 1) % self.menu_items
            self.audio_manager.play_sfx('menu_navigate')
        elif key == pygame.K_DOWN:
            self.menu_selection = (self.menu_selection + 1) % self.menu_items
            self.audio_manager.play_sfx('menu_navigate')
        elif key in [pygame.K_RETURN, pygame.K_SPACE]:
            self.audio_manager.play_sfx('menu_select')
            if self.menu_selection < 3:
                # Toggle player mode
                current_mode = self.player_modes[self.menu_selection]
                if current_mode == PlayerMode.HUMAN:
                    self.player_modes[self.menu_selection] = PlayerMode.CPU
                elif current_mode == PlayerMode.CPU:
                    self.player_modes[self.menu_selection] = PlayerMode.OFF
                else:
                    self.player_modes[self.menu_selection] = PlayerMode.HUMAN
            else:
                # Start game
                self.start_game()
        elif key in [pygame.K_LEFT, pygame.K_RIGHT]:
            if self.menu_selection < 3:
                self.audio_manager.play_sfx('menu_navigate')
                # Toggle player mode
                current_mode = self.player_modes[self.menu_selection]
                if current_mode == PlayerMode.HUMAN:
                    self.player_modes[self.menu_selection] = PlayerMode.CPU
                elif current_mode == PlayerMode.CPU:
                    self.player_modes[self.menu_selection] = PlayerMode.OFF
                else:
                    self.player_modes[self.menu_selection] = PlayerMode.HUMAN
    
    def update(self, delta_time: float):
        """Update game state."""
        # Update input systems
        self.gamepad_manager.update(self.keys_pressed, self.keys_just_pressed)
        
        if self.state == GameState.MENU:
            self.ui_navigation.update(self.keys_pressed)
            
        elif self.state == GameState.PLAYING:
            self.update_gameplay(delta_time)
            
        elif self.state == GameState.PAUSED:
            # Handle pause input via gamepad
            for player_id in range(1, 4):
                input_state = self.gamepad_manager.get_input_state(player_id)
                if input_state.pressed[Action.PAUSE]:
                    self.resume_game()
                    break
        
        # Update UI animations
        self.ui_renderer.update(delta_time)
    
    def update_gameplay(self, delta_time: float):
        """Update gameplay logic."""
        if not self.games:
            return
        
        # Update all active games
        for i, game in enumerate(self.games):
            if game.mode == PlayerMode.OFF or game.game_over:
                continue
            
            player_id = i + 1
            
            if game.mode == PlayerMode.HUMAN:
                # Human player input
                input_state = self.gamepad_manager.get_input_state(player_id)
                
                # Handle pause input
                if input_state.pressed[Action.PAUSE]:
                    self.pause_game()
                    return
                
                # Update game with input
                events = game.update(input_state, delta_time)
                
            elif game.mode == PlayerMode.CPU:
                # CPU player (optimized for performance)
                input_state = self.gamepad_manager.get_input_state(player_id)
                
                if player_id in self.cpu_controllers:
                    cpu = self.cpu_controllers[player_id]
                    current_time = time.time() * 1000
                    
                    # Limit CPU processing frequency to prevent lag
                    if not hasattr(cpu, '_last_think_time'):
                        cpu._last_think_time = 0
                    
                    if current_time - cpu._last_think_time > CPU_MOVE_MS:
                        action = cpu.update(game, current_time)
                        cpu._last_think_time = current_time
                        
                        # Simulate input based on CPU decision
                        if action:
                            self.simulate_cpu_input(input_state, action)
                
                # Update game
                events = game.update(input_state, delta_time)
            
            # Handle game events
            self.handle_game_events(events, player_id)
        
        # Check for game over
        self.check_game_over()
    
    def simulate_cpu_input(self, input_state, action: str):
        """Simulate input for CPU actions."""
        # Reset all actions
        for act in Action:
            input_state.actions[act] = False
            input_state.pressed[act] = False
        
        # Set action based on CPU decision
        if action == 'left':
            input_state.actions[Action.MOVE_LEFT] = True
            input_state.pressed[Action.MOVE_LEFT] = True
        elif action == 'right':
            input_state.actions[Action.MOVE_RIGHT] = True
            input_state.pressed[Action.MOVE_RIGHT] = True
        elif action == 'soft_drop':
            input_state.actions[Action.SOFT_DROP] = True
            input_state.pressed[Action.SOFT_DROP] = True
        elif action == 'hard_drop':
            input_state.actions[Action.HARD_DROP] = True
            input_state.pressed[Action.HARD_DROP] = True
        elif action == 'rotate_cw':
            input_state.actions[Action.ROTATE_CW] = True
            input_state.pressed[Action.ROTATE_CW] = True
        elif action == 'rotate_ccw':
            input_state.actions[Action.ROTATE_CCW] = True
            input_state.pressed[Action.ROTATE_CCW] = True
        elif action == 'hold':
            input_state.actions[Action.HOLD] = True
            input_state.pressed[Action.HOLD] = True
    
    def handle_game_events(self, events: Dict[str, any], player_id: int):
        """Handle events from game updates."""
        if not events:
            return
        
        game = self.games[player_id - 1]
        
        # Sound effects
        if events.get('piece_moved'):
            self.audio_manager.play_sfx('piece_move', 0.5)
        
        if events.get('piece_rotated'):
            self.audio_manager.play_sfx('piece_rotate', 0.6)
        
        if events.get('soft_drop'):
            self.audio_manager.play_sfx('piece_move', 0.3)
        
        if events.get('hard_drop'):
            self.audio_manager.play_sfx('piece_drop', 0.8)
        
        if events.get('piece_locked'):
            self.audio_manager.play_sfx('piece_drop', 0.4)
        
        if events.get('piece_held'):
            self.audio_manager.play_sfx('menu_select', 0.6)
        
        # Line clear effects
        lines_cleared = events.get('lines_cleared', 0)
        if lines_cleared > 0:
            if lines_cleared == 4:
                self.audio_manager.play_sfx('tetris')
                self.ui_renderer.add_flash_effect(player_id, Colors.UI_HIGHLIGHT)
            else:
                self.audio_manager.play_sfx('line_clear')
            
            # Add visual effects
            cleared_line_indices = events.get('cleared_line_indices', [])
            self.ui_renderer.add_line_clear_animation(player_id, cleared_line_indices)
            
            # Send garbage to other players
            attack_power = game.get_attack_power(lines_cleared)
            if attack_power > 0:
                self.send_garbage_attack(player_id, attack_power)
        
        if events.get('level_up'):
            self.audio_manager.play_sfx('level_up')
    
    def send_garbage_attack(self, attacking_player: int, lines: int):
        """Send garbage attack to other players."""
        for i, game in enumerate(self.games):
            target_player = i + 1
            if (target_player != attacking_player and 
                game.mode != PlayerMode.OFF and 
                not game.game_over):
                
                if game.add_garbage(lines):
                    self.audio_manager.play_sfx('garbage_attack', 0.7)
                    self.ui_renderer.add_flash_effect(target_player, Colors.RED)
    
    def check_game_over(self):
        """Check if game is over."""
        active_games = [
            game for game in self.games 
            if game.mode != PlayerMode.OFF and not game.game_over
        ]
        
        if len(active_games) <= 1:
            self.state = GameState.GAME_OVER
            self.audio_manager.stop_bgm()
            self.audio_manager.play_sfx('game_over')
    
    def start_game(self):
        """Start new game."""
        # Validate that at least one player is active
        active_count = sum(1 for mode in self.player_modes if mode != PlayerMode.OFF)
        if active_count == 0:
            return
        
        print(f"Starting game with players: {self.player_modes}")
        
        # Initialize games
        self.games = []
        self.active_players = []
        self.cpu_controllers = {}
        
        for i, mode in enumerate(self.player_modes):
            player_id = i + 1
            try:
                if self.debug:
                    self.debug.log_info(f"Creating TetrisGame for player {player_id}, mode: {mode}", "start_game")
                game = TetrisGame(player_id, mode)
                self.games.append(game)
                if self.debug:
                    self.debug.log_info(f"TetrisGame created successfully for player {player_id}", "start_game")
            except Exception as e:
                if self.debug:
                    self.debug.log_error(e, f"start_game.create_tetris_game_{player_id}")
                print(f"[ERROR] Failed to create game for player {player_id}: {e}")
                # Create a dummy game to maintain list structure
                game = type('DummyGame', (), {
                    'mode': PlayerMode.OFF, 
                    'game_over': True,
                    'pause': lambda: None,
                    'resume': lambda: None
                })()
                self.games.append(game)
            
            if mode != PlayerMode.OFF:
                self.active_players.append(player_id)
            
            if mode == PlayerMode.CPU:
                try:
                    difficulty = 'medium'  # Could be configurable
                    if self.debug:
                        self.debug.log_info(f"Creating CPU controller for player {player_id}, difficulty: {difficulty}", "start_game")
                    self.cpu_controllers[player_id] = AdaptiveCPU(difficulty)
                    if self.debug:
                        self.debug.log_info(f"CPU controller created successfully for player {player_id}", "start_game")
                except Exception as e:
                    if self.debug:
                        self.debug.log_error(e, f"start_game.create_cpu_{player_id}")
                    print(f"[ERROR] Failed to create CPU for player {player_id}: {e}")
                    # Continue without CPU controller
        
        # Change state
        self.state = GameState.PLAYING
        
        # Start game music
        self.audio_manager.stop_bgm()
        self.audio_manager.play_bgm('game_music')
        
        print(f"Active players: {self.active_players}")
    
    def pause_game(self):
        """Pause the game."""
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
            self.paused_time = time.time()
            
            # Pause all games
            for game in self.games:
                game.pause()
            
            self.audio_manager.play_sfx('menu_select')
            print("Game paused")
    
    def resume_game(self):
        """Resume the game."""
        if self.state == GameState.PAUSED:
            self.state = GameState.PLAYING
            
            # Resume all games
            for game in self.games:
                game.resume()
            
            # Adjust timing
            pause_duration = time.time() - self.paused_time
            self.last_time += pause_duration
            
            self.audio_manager.play_sfx('menu_select')
            print("Game resumed")
    
    def restart_game(self):
        """Restart current game."""
        if self.state in [GameState.PLAYING, GameState.PAUSED, GameState.GAME_OVER]:
            self.start_game()
            print("Game restarted")
    
    def draw(self, screen):
        """Draw current state to the screen."""
        screen.fill(Colors.BG_PRIMARY)
        
        if self.state == GameState.MENU:
            self.ui_renderer.draw_main_menu(self.menu_selection, self.player_modes)
            
        elif self.state == GameState.PLAYING:
            self.ui_renderer.draw_game_hud(self.games, self.active_players)
            
        elif self.state == GameState.PAUSED:
            self.ui_renderer.draw_game_hud(self.games, self.active_players)
            self.ui_renderer.draw_pause_menu()
            
        elif self.state == GameState.GAME_OVER:
            self.ui_renderer.draw_game_hud(self.games, self.active_players)
            
            # Determine winner
            winner = None
            if self.games:
                active_games = [
                    (i + 1, game) for i, game in enumerate(self.games)
                    if game.mode != PlayerMode.OFF and not game.game_over
                ]
                if len(active_games) == 1:
                    winner = active_games[0][0]
            
            self.ui_renderer.draw_game_over_screen(winner, self.games)
        
        # Debug info
        if DEBUG_CONTROLLERS:
            self.draw_debug_info(screen)
    
    def draw_debug_info(self, screen):
        """Draw debug information."""
        debug_y = 10
        font = pygame.font.Font(None, 24)
        
        # Controller assignments
        assignments = self.gamepad_manager.assignment_table
        debug_text = f"Controllers: {len(self.gamepad_manager.joysticks)}, Assignments: {assignments}"
        text_surface = font.render(debug_text, True, Colors.WHITE)
        screen.blit(text_surface, (10, debug_y))
        debug_y += 25
        
        # Game state
        state_text = f"State: {self.state}, Active players: {self.active_players}"
        text_surface = font.render(state_text, True, Colors.WHITE)
        screen.blit(text_surface, (10, debug_y))
        debug_y += 25
        
        # FPS - use pygame.time.Clock for FPS calculation
        try:
            fps_text = f"FPS: {self.clock.get_fps():.1f}" if hasattr(self, 'clock') else "FPS: N/A"
            text_surface = font.render(fps_text, True, Colors.WHITE)
            screen.blit(text_surface, (10, debug_y))
        except:
            pass
