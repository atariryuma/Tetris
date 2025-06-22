"""
Quick startup test to verify all systems work.
"""

import os
import sys

# Set headless mode
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

def test_startup():
    """Test game startup without running the full game."""
    print("=== Testing Game Startup ===")
    
    try:
        # Test pygame init
        import pygame
        pygame.init()
        print("✓ Pygame initialized")
        
        # Test display
        screen = pygame.display.set_mode((800, 600))
        print("✓ Display created")
        
        # Test GameManager initialization
        from game_manager import GameManager
        game_manager = GameManager(screen)
        print("✓ GameManager created")
        
        # Test event handling
        for _ in range(5):  # Test a few event cycles
            game_manager.handle_events()
        print("✓ Event handling works")
        
        # Cleanup
        pygame.quit()
        print("✓ Cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_startup()
    print(f"Startup test: {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
