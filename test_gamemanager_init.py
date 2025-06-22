#!/usr/bin/env python3
"""Test GameManager initialization step by step."""

import pygame
import sys
import traceback
from constants import WINDOW_WIDTH, WINDOW_HEIGHT
from utils import safe_events

def test_gamemanager_init():
    """Test GameManager initialization step by step."""
    print("=== Testing GameManager Initialization ===")
    
    try:
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        print("[OK] Pygame and screen initialized")
        
        # Import GameManager
        from game_manager import GameManager
        print("[OK] GameManager imported")
        
        # Test individual system initialization
        print("\nTesting individual systems...")
        
        # Test 1: Can we create a basic GameManager?
        print("Creating GameManager instance...")
        try:
            gm = GameManager(screen, event_source=safe_events)
            print("[OK] GameManager created successfully!")
            
            # Test basic methods
            print("Testing basic methods...")
            gm.update(0.016)  # 60 FPS frame
            print("[OK] update() works")
            
            gm.draw(screen)
            print("[OK] draw() works")
            
            pygame.display.flip()
            print("[OK] display flip works")
            
            # Cleanup
            try:
                gm.audio_manager.cleanup()
            except:
                pass
            
            print("[SUCCESS] GameManager fully functional!")
            return True
            
        except Exception as e:
            print(f"[ERROR] GameManager creation failed: {e}")
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"[ERROR] Test setup failed: {e}")
        traceback.print_exc()
        return False
    finally:
        pygame.quit()

if __name__ == "__main__":
    success = test_gamemanager_init()
    sys.exit(0 if success else 1)