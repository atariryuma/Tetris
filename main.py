"""
Main entry point for the Tetris game.
"""

import sys
import os

try:
    import pygame
except ModuleNotFoundError:
    print("Error: pygame is not installed.")
    print("Please run 'pip install -r requirements.txt' to install dependencies.")
    print("Alternatively, launch the game via 'run_game.sh' or 'run_game.bat'.")
    sys.exit(1)

from constants import *
from game_manager import GameManager
from font_manager import cleanup_fonts

def main():
    """Initialize and run the Tetris game."""
    print("=== 三人対戦テトリス NEO - Python Edition ===")
    print("Initializing game systems...")
    
    # Check if pygame is already initialized
    if not pygame.get_init():
        pygame.init()
    
    # Try to set up display
    try:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("三人対戦テトリス NEO - Python Edition")
    except pygame.error as e:
        print(f"Display initialization failed: {e}")
        print("Falling back to headless mode...")
        try:
            os.environ['SDL_VIDEODRIVER'] = 'dummy'
            pygame.display.quit()
            pygame.display.init()
            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            print("Running in headless mode - no visual output")
        except Exception as fallback_error:
            print(f"Headless mode also failed: {fallback_error}")
            print("Attempting minimal display setup...")
            screen = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # Set icon (if available)
    try:
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'images', 'icon.png')
        if os.path.exists(icon_path):
            icon = pygame.image.load(icon_path)
            pygame.display.set_icon(icon)
    except Exception as e:
        print(f"Could not load icon: {e}")
    
    # Enable VSync if supported
    if VSYNC:
        try:
            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF)
        except Exception:
            print("VSync not supported, continuing without it")
    
    print("Game systems initialized successfully!")
    print("\nControls:")
    print("- Arrow keys: Move pieces")
    print("- Z/X: Rotate pieces")
    print("- C: Hold piece")
    print("- ESC: Pause/Menu")
    print("- F1: Show volume info")
    print("- F2/F3: Adjust master volume")
    print("\nGamepad support:")
    print("- Xbox, PlayStation, Nintendo Switch Pro controllers")
    print("- Plug in controllers before or during play")
    print("- Multiple controllers supported for multiplayer")
    
    try:
        # Create and run game manager
        game_manager = GameManager(screen)
        game_manager.run()
        
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cleanup_fonts()
        pygame.quit()
        print("Game shutdown complete")
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
