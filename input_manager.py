"""
Universal gamepad and keyboard input manager.
"""

import pygame
import time
from enum import Enum
from typing import Dict, List, Optional, Tuple
from constants import INPUT_INTERVAL_MS, ANALOG_DEAD_ZONE, DEBUG_CONTROLLERS
from debug_logger import get_debug_logger

class Action(Enum):
    """Game actions that can be mapped to inputs."""
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    SOFT_DROP = "soft_drop"
    HARD_DROP = "hard_drop"
    ROTATE_CW = "rotate_cw"
    ROTATE_CCW = "rotate_ccw"
    HOLD = "hold"
    PAUSE = "pause"
    MENU_UP = "menu_up"
    MENU_DOWN = "menu_down"
    MENU_LEFT = "menu_left"
    MENU_RIGHT = "menu_right"
    MENU_SELECT = "menu_select"
    MENU_BACK = "menu_back"

class InputState:
    """Current input state for a player."""
    def __init__(self):
        self.actions: Dict[Action, bool] = {action: False for action in Action}
        self.pressed: Dict[Action, bool] = {action: False for action in Action}
        self.released: Dict[Action, bool] = {action: False for action in Action}
        self.last_press_time: Dict[Action, float] = {action: 0 for action in Action}

class UniversalGamepadMapper:
    """Maps different controller types to a universal button layout."""
    
    def __init__(self):
        # Xbox Controller mapping only (simplified for stability)
        self.xbox_mapping = {
            'buttons': {
                0: Action.ROTATE_CW,      # A - 右回転
                1: Action.HOLD,           # B - ホールド
                2: Action.ROTATE_CCW,     # X - 左回転
                3: Action.HARD_DROP,      # Y - ハードドロップ
                4: Action.HARD_DROP,      # LB - ハードドロップ（代替）
                5: Action.ROTATE_CW,      # RB - 右回転（代替）
                6: Action.MENU_BACK,      # Back/Select
                7: Action.PAUSE,          # Start
                11: Action.MENU_UP,       # D-pad Up
                12: Action.MENU_DOWN,     # D-pad Down  
                13: Action.MENU_LEFT,     # D-pad Left
                14: Action.MENU_RIGHT,    # D-pad Right
            },
            'axes': {
                0: (Action.MOVE_LEFT, Action.MOVE_RIGHT),  # Left stick X
                1: (Action.MENU_UP, Action.SOFT_DROP),     # Left stick Y
            }
        }
        
        # Keyboard mapping
        self.keyboard_mapping = {
            pygame.K_LEFT: Action.MOVE_LEFT,
            pygame.K_RIGHT: Action.MOVE_RIGHT,
            pygame.K_DOWN: Action.SOFT_DROP,
            pygame.K_UP: Action.HARD_DROP,
            pygame.K_z: Action.ROTATE_CW,
            pygame.K_x: Action.ROTATE_CCW,
            pygame.K_c: Action.HOLD,
            pygame.K_ESCAPE: Action.PAUSE,
            pygame.K_RETURN: Action.MENU_SELECT,
            pygame.K_SPACE: Action.MENU_SELECT,
            
            # Player 2 controls
            pygame.K_a: Action.MOVE_LEFT,
            pygame.K_d: Action.MOVE_RIGHT,
            pygame.K_s: Action.SOFT_DROP,
            pygame.K_w: Action.HARD_DROP,
            pygame.K_q: Action.ROTATE_CW,
            pygame.K_e: Action.ROTATE_CCW,
            pygame.K_r: Action.HOLD,
            
            # Player 3 controls
            pygame.K_j: Action.MOVE_LEFT,
            pygame.K_l: Action.MOVE_RIGHT,
            pygame.K_k: Action.SOFT_DROP,
            pygame.K_i: Action.HARD_DROP,
            pygame.K_u: Action.ROTATE_CW,
            pygame.K_o: Action.ROTATE_CCW,
            pygame.K_p: Action.HOLD,
        }

    def detect_controller_type(self, joystick_name: str) -> str:
        """Detect if controller is Xbox (only Xbox supported)."""
        name_lower = joystick_name.lower()
        if any(keyword in name_lower for keyword in ['xbox', '045e', 'microsoft']):
            return 'xbox'
        else:
            return 'xbox'  # Force Xbox mapping for all controllers

    def get_mapping(self) -> Dict:
        """Get Xbox button/axis mapping."""
        return self.xbox_mapping

class GamepadManager:
    """Manages gamepad detection, assignment, and input processing."""
    
    def __init__(self):
        self.mapper = UniversalGamepadMapper()
        self.joysticks: Dict[int, pygame.joystick.Joystick] = {}
        self.player_assignments: Dict[int, int] = {}  # player_id -> joystick_id
        self.assignment_table: Dict[int, int] = {}    # joystick_id -> player_id
        self.input_states: Dict[int, InputState] = {}
        self.last_scan_time = 0
        self.scan_interval = 1.0  # Scan for new controllers every second
        self.debug = get_debug_logger()
        
        # Initialize pygame joystick module
        try:
            if self.debug:
                self.debug.log_info("Initializing joystick subsystem", "GamepadManager.__init__")
            pygame.joystick.init()
            
            if self.debug:
                self.debug.log_info("Scanning for controllers", "GamepadManager.__init__")
            self.scan_controllers()
            
        except (pygame.error, SystemError, OSError) as e:
            if self.debug:
                self.debug.log_error(e, "GamepadManager.__init__")
            elif DEBUG_CONTROLLERS:
                print(f"Joystick initialization failed: {e}")
            # Continue without gamepad support

    def scan_controllers(self):
        """Scan for connected controllers."""
        # Pump the event queue to keep SDL responsive
        try:
            pygame.event.pump()
        except Exception as e:
            if self.debug:
                self.debug.log_warning(f"pygame.event.pump() failed: {e}", "scan_controllers")

        current_time = time.time()
        if current_time - self.last_scan_time < self.scan_interval:
            return
            
        self.last_scan_time = current_time
        
        try:
            # Check current controller count
            controller_count = pygame.joystick.get_count()
            if self.debug:
                self.debug.log_debug(f"Scanning controllers: {controller_count} detected", "scan_controllers")
            
            # Remove disconnected joysticks
            connected_ids = set(range(controller_count))
            for joystick_id in list(self.joysticks.keys()):
                if joystick_id not in connected_ids:
                    joystick = self.joysticks[joystick_id]
                    if self.debug:
                        self.debug.log_controller_event("DISCONNECTED", joystick_id, 
                                                      {"name": joystick.get_name()})
                    
                    # Safely quit joystick
                    try:
                        joystick.quit()
                    except Exception as e:
                        if self.debug:
                            self.debug.log_warning(f"Failed to quit joystick {joystick_id}: {e}", "scan_controllers")
                    
                    del self.joysticks[joystick_id]
                    if joystick_id in self.assignment_table:
                        player_id = self.assignment_table[joystick_id]
                        del self.player_assignments[player_id]
                        del self.assignment_table[joystick_id]
            
            # Add new joysticks
            for i in range(controller_count):
                if i not in self.joysticks:
                    try:
                        if self.debug:
                            self.debug.log_debug(f"Attempting to initialize controller {i}", "scan_controllers")
                        
                        joystick = pygame.joystick.Joystick(i)
                        joystick.init()
                        
                        # Get controller info
                        name = joystick.get_name()
                        guid = joystick.get_guid()
                        buttons = joystick.get_numbuttons()
                        axes = joystick.get_numaxes()
                        hats = joystick.get_numhats()
                        
                        ctype = self.mapper.detect_controller_type(name)
                        self.joysticks[i] = joystick
                        
                        if self.debug:
                            self.debug.log_controller_event("CONNECTED", i, {
                                "name": name,
                                "guid": guid,
                                "type": ctype,
                                "buttons": buttons,
                                "axes": axes,
                                "hats": hats
                            })
                        elif DEBUG_CONTROLLERS:
                            print(f"Controller {i} connected: {name} [{ctype}]")
                            
                    except (pygame.error, SystemError, OSError) as e:
                        if self.debug:
                            self.debug.log_error(e, f"scan_controllers.init_controller_{i}")
                        elif DEBUG_CONTROLLERS:
                            print(f"Failed to initialize controller {i}: {e}")
                        
        except (pygame.error, SystemError, OSError) as e:
            if self.debug:
                self.debug.log_error(e, "scan_controllers.get_count")
            elif DEBUG_CONTROLLERS:
                print(f"Failed to get controller count: {e}")

    def assign_controller(self, player_id: int, joystick_id: int) -> bool:
        """Assign a controller to a player."""
        if joystick_id not in self.joysticks:
            return False
            
        # Remove previous assignment
        if player_id in self.player_assignments:
            old_joystick_id = self.player_assignments[player_id]
            if old_joystick_id in self.assignment_table:
                del self.assignment_table[old_joystick_id]
        
        # Remove joystick from other players
        if joystick_id in self.assignment_table:
            old_player_id = self.assignment_table[joystick_id]
            if old_player_id in self.player_assignments:
                del self.player_assignments[old_player_id]
        
        # Make new assignment
        self.player_assignments[player_id] = joystick_id
        self.assignment_table[joystick_id] = player_id
        
        if DEBUG_CONTROLLERS:
            print(f"Assigned controller {joystick_id} to player {player_id}")
        
        return True

    def auto_assign_controllers(self):
        """Automatically assign controllers to players."""
        unassigned_controllers = [
            jid for jid in self.joysticks.keys() 
            if jid not in self.assignment_table
        ]
        
        for player_id in range(1, 4):  # Players 1, 2, 3
            if player_id not in self.player_assignments and unassigned_controllers:
                controller_id = unassigned_controllers.pop(0)
                self.assign_controller(player_id, controller_id)

    def get_input_state(self, player_id: int) -> InputState:
        """Get current input state for a player."""
        if player_id not in self.input_states:
            self.input_states[player_id] = InputState()
        return self.input_states[player_id]

    def update(self, keys_pressed: Dict[int, bool], keys_just_pressed: Dict[int, bool]):
        """Update input states for all players."""
        self.scan_controllers()
        self.auto_assign_controllers()
        
        current_time = time.time() * 1000  # Convert to milliseconds
        
        # Update gamepad inputs
        for player_id, joystick_id in self.player_assignments.items():
            if joystick_id in self.joysticks:
                joystick = self.joysticks[joystick_id]
                input_state = self.get_input_state(player_id)
                
                controller_type = self.mapper.detect_controller_type(joystick.get_name())
                mapping = self.mapper.get_mapping()  # Xbox only
                
                try:
                    # Process buttons
                    for button_id, action in mapping['buttons'].items():
                        try:
                            if button_id < joystick.get_numbuttons():
                                pressed = joystick.get_button(button_id)
                                self._update_action_state(input_state, action, pressed, current_time)
                        except (pygame.error, SystemError, OSError) as e:
                            if self.debug:
                                self.debug.log_warning(f"Button {button_id} read failed: {e}", 
                                                     f"controller_{joystick_id}")
                            continue
                    
                    # Process axes
                    for axis_id, (neg_action, pos_action) in mapping['axes'].items():
                        try:
                            if axis_id < joystick.get_numaxes():
                                axis_value = joystick.get_axis(axis_id)
                                
                                # Apply deadzone
                                if abs(axis_value) < ANALOG_DEAD_ZONE:
                                    axis_value = 0
                                
                                # Process negative direction
                                pressed = axis_value < -ANALOG_DEAD_ZONE
                                self._update_action_state(input_state, neg_action, pressed, current_time)
                                
                                # Process positive direction
                                pressed = axis_value > ANALOG_DEAD_ZONE
                                self._update_action_state(input_state, pos_action, pressed, current_time)
                        except (pygame.error, SystemError, OSError) as e:
                            if self.debug:
                                self.debug.log_warning(f"Axis {axis_id} read failed: {e}", 
                                                     f"controller_{joystick_id}")
                            continue
                except (pygame.error, SystemError, OSError) as e:
                    if self.debug:
                        self.debug.log_error(e, f"controller_{joystick_id}_processing")
                        self.debug.log_info(f"Removing problematic controller {joystick_id}", 
                                          "controller_cleanup")
                    elif DEBUG_CONTROLLERS:
                        print(f"Error processing controller {joystick_id}: {e}")
                    
                    # Remove this controller from active list
                    try:
                        if joystick_id in self.joysticks:
                            self.joysticks[joystick_id].quit()
                            del self.joysticks[joystick_id]
                        if joystick_id in self.assignment_table:
                            player_id = self.assignment_table[joystick_id]
                            del self.player_assignments[player_id]
                            del self.assignment_table[joystick_id]
                    except Exception as cleanup_error:
                        if self.debug:
                            self.debug.log_error(cleanup_error, f"controller_{joystick_id}_cleanup")
        
        # Update keyboard inputs for players without controllers
        for player_id in range(1, 4):
            if player_id not in self.player_assignments:
                input_state = self.get_input_state(player_id)
                
                # Map keyboard keys to this player
                key_mapping = self._get_keyboard_mapping_for_player(player_id)
                
                for key, action in key_mapping.items():
                    pressed = keys_pressed.get(key, False)
                    self._update_action_state(input_state, action, pressed, current_time)

    def _get_keyboard_mapping_for_player(self, player_id: int) -> Dict[int, Action]:
        """Get keyboard mapping for a specific player."""
        if player_id == 1:
            return {
                pygame.K_LEFT: Action.MOVE_LEFT,
                pygame.K_RIGHT: Action.MOVE_RIGHT,
                pygame.K_DOWN: Action.SOFT_DROP,
                pygame.K_UP: Action.HARD_DROP,
                pygame.K_z: Action.ROTATE_CW,
                pygame.K_x: Action.ROTATE_CCW,
                pygame.K_c: Action.HOLD,
                pygame.K_ESCAPE: Action.PAUSE,
            }
        elif player_id == 2:
            return {
                pygame.K_a: Action.MOVE_LEFT,
                pygame.K_d: Action.MOVE_RIGHT,
                pygame.K_s: Action.SOFT_DROP,
                pygame.K_w: Action.HARD_DROP,
                pygame.K_q: Action.ROTATE_CW,
                pygame.K_e: Action.ROTATE_CCW,
                pygame.K_r: Action.HOLD,
            }
        elif player_id == 3:
            return {
                pygame.K_j: Action.MOVE_LEFT,
                pygame.K_l: Action.MOVE_RIGHT,
                pygame.K_k: Action.SOFT_DROP,
                pygame.K_i: Action.HARD_DROP,
                pygame.K_u: Action.ROTATE_CW,
                pygame.K_o: Action.ROTATE_CCW,
                pygame.K_p: Action.HOLD,
            }
        return {}

    def _update_action_state(self, input_state: InputState, action: Action, pressed: bool, current_time: float):
        """Update action state with timing and repeat logic."""
        was_pressed = input_state.actions[action]
        
        # Update pressed/released states
        input_state.pressed[action] = pressed and not was_pressed
        input_state.released[action] = not pressed and was_pressed
        
        # Handle repeat timing
        if pressed:
            if not was_pressed:
                # First press
                input_state.actions[action] = True
                input_state.last_press_time[action] = current_time
            elif current_time - input_state.last_press_time[action] >= INPUT_INTERVAL_MS:
                # Repeat press
                input_state.actions[action] = True
                input_state.last_press_time[action] = current_time
            else:
                # Too soon for repeat
                input_state.actions[action] = False
        else:
            input_state.actions[action] = False

class UINavigationManager:
    """Manages UI navigation with gamepad and keyboard support."""
    
    def __init__(self, gamepad_manager: GamepadManager):
        self.gamepad_manager = gamepad_manager
        self.current_focus = 0
        self.focusable_elements = []
        self.last_nav_time = 0
        self.nav_delay = 200  # ms between navigation moves

    def set_focusable_elements(self, elements: List):
        """Set the list of focusable UI elements."""
        self.focusable_elements = elements
        self.current_focus = 0

    def update(self, keys_pressed: Dict[int, bool]):
        """Update navigation state."""
        current_time = time.time() * 1000
        
        if current_time - self.last_nav_time < self.nav_delay:
            return
        
        # Check all players for navigation input
        for player_id in range(1, 4):
            input_state = self.gamepad_manager.get_input_state(player_id)
            
            if input_state.pressed[Action.MENU_UP]:
                self.navigate_up()
                self.last_nav_time = current_time
                break
            elif input_state.pressed[Action.MENU_DOWN]:
                self.navigate_down()
                self.last_nav_time = current_time
                break
            elif input_state.pressed[Action.MENU_LEFT]:
                self.navigate_left()
                self.last_nav_time = current_time
                break
            elif input_state.pressed[Action.MENU_RIGHT]:
                self.navigate_right()
                self.last_nav_time = current_time
                break
        
        # Keyboard fallback
        if keys_pressed.get(pygame.K_UP, False):
            self.navigate_up()
            self.last_nav_time = current_time
        elif keys_pressed.get(pygame.K_DOWN, False):
            self.navigate_down()
            self.last_nav_time = current_time
        elif keys_pressed.get(pygame.K_LEFT, False):
            self.navigate_left()
            self.last_nav_time = current_time
        elif keys_pressed.get(pygame.K_RIGHT, False):
            self.navigate_right()
            self.last_nav_time = current_time

    def navigate_up(self):
        """Navigate up in the menu."""
        if self.focusable_elements:
            self.current_focus = (self.current_focus - 1) % len(self.focusable_elements)

    def navigate_down(self):
        """Navigate down in the menu."""
        if self.focusable_elements:
            self.current_focus = (self.current_focus + 1) % len(self.focusable_elements)

    def navigate_left(self):
        """Navigate left in the menu."""
        if self.focusable_elements:
            self.current_focus = (self.current_focus - 1) % len(self.focusable_elements)

    def navigate_right(self):
        """Navigate right in the menu."""
        if self.focusable_elements:
            self.current_focus = (self.current_focus + 1) % len(self.focusable_elements)

    def get_current_focus(self) -> int:
        """Get the currently focused element index."""
        return self.current_focus

    def is_select_pressed(self) -> bool:
        """Check if select/confirm is pressed."""
        # Check all players
        for player_id in range(1, 4):
            input_state = self.gamepad_manager.get_input_state(player_id)
            if input_state.pressed[Action.MENU_SELECT]:
                return True
        return False

    def is_back_pressed(self) -> bool:
        """Check if back/cancel is pressed."""
        # Check all players
        for player_id in range(1, 4):
            input_state = self.gamepad_manager.get_input_state(player_id)
            if input_state.pressed[Action.MENU_BACK]:
                return True
        return False
