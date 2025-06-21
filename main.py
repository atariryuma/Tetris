"""
Main entry point for the Tetris game.
"""

import pygame
import sys
import os
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, VSYNC
from game_manager import GameManager
from font_manager import cleanup_fonts

def safe_events():
    """Safely retrieve pygame events to avoid platform-specific polling errors."""
    try:
        return pygame.event.get()
    except Exception as e:
        print(f"[WARN] Event polling error: {e}")
        return []

def main():
    """Initialize and run the Tetris game."""
    print("=== 三人対戦テトリス NEO - Python Edition ===")
    print("Initializing game systems...")

    # Initialize pygame if not already
    if not pygame.get_init():
        pygame.init()

    # Attempt to create display
    try:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("三人対戦テトリス NEO - Python Edition")
    except pygame.error as e:
        print(f"[ERROR] Display initialization failed: {e}")
        print("Falling back to headless mode...")
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.display.quit()
        pygame.display.init()
        try:
            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            print("[INFO] Running in headless mode - no visual output")
        except Exception as fallback_error:
            print(f"[ERROR] Headless mode also failed: {fallback_error}")
            screen = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

    # Load window icon if available
    try:
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'images', 'icon.png')
        if os.path.exists(icon_path):
            pygame.display.set_icon(pygame.image.load(icon_path))
    except Exception as e:
        print(f"[WARN] Could not load icon: {e}")

    # Enable VSync if requested
    if VSYNC:
        try:
            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF)
        except pygame.error:
            print("[INFO] VSync not supported, continuing without it")

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

    # Load BGM safely
    bgm_path = os.path.join(os.path.dirname(__file__), 'assets', 'sounds', 'menu_music.ogg')
    if not os.path.exists(bgm_path):
        print(f"[INFO] BGM file not found, continuing without music: {os.path.basename(bgm_path)}")
    else:
        try:
            pygame.mixer.music.load(bgm_path)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"[WARN] Failed to play BGM: {e}")

    try:
        # Pass safe_events into GameManager so all event polling uses the wrapper
        game_manager = GameManager(screen, event_source=safe_events)
        game_manager.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback; traceback.print_exc()
    finally:
        cleanup_fonts()
        pygame.quit()
        print("Game shutdown complete")

    return 0

if __name__ == "__main__":
    sys.exit(main())
