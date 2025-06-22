"""
Main entry point for the Tetris game.
"""

import sys
import os
import pygame
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, VSYNC
from game_manager import GameManager
from font_manager import cleanup_fonts
from utils import safe_events  # safe event getter

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
    print("- Works with Xbox, PlayStation, Switch Pro and most generic controllers")
    print("- Plug in controllers before or during play")

    # BGM安全読み込み
    bgm_path = os.path.join(os.path.dirname(__file__), 'assets', 'sounds', 'menu_music.ogg')
    if not os.path.exists(bgm_path):
        print(f"[INFO] BGM not found, skipping: {os.path.basename(bgm_path)}")
    else:
        try:
            pygame.mixer.music.load(bgm_path)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"[WARN] BGM play failed: {e}")

    try:
        # ゲーム開始
        gm = GameManager(screen, event_source=safe_events)
        gm.run()
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
