#!/usr/bin/env python3
"""Test startup sequence step by step."""

import sys
import traceback

def test_imports():
    """Test each import individually."""
    print("Testing imports...")
    
    try:
        import pygame
        print("[OK] pygame imported")
        
        import os
        print("[OK] os imported")
        
        import time
        print("[OK] time imported")
        
        from utils import safe_events
        print("[OK] utils.safe_events imported")
        
        from game_manager import GameManager
        print("[OK] GameManager imported")
        
        return True
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        traceback.print_exc()
        return False

def test_pygame_init():
    """Test pygame initialization."""
    print("\nTesting pygame initialization...")
    
    try:
        import pygame
        pygame.init()
        print("[OK] pygame.init() successful")
        
        screen = pygame.display.set_mode((800, 600))
        print("[OK] Display mode set")
        
        pygame.quit()
        print("[OK] pygame.quit() successful")
        
        return True
    except Exception as e:
        print(f"[ERROR] Pygame init failed: {e}")
        traceback.print_exc()
        return False

def test_audio():
    """Test audio system."""
    print("\nTesting audio system...")
    
    try:
        import pygame
        pygame.init()
        
        from audio_manager import AudioManager
        audio = AudioManager()
        print("[OK] AudioManager created")
        
        audio.cleanup()
        pygame.quit()
        print("[OK] Audio cleanup successful")
        
        return True
    except Exception as e:
        print(f"[ERROR] Audio test failed: {e}")
        traceback.print_exc()
        return False

def test_fonts():
    """Test font system."""
    print("\nTesting font system...")
    
    try:
        import pygame
        pygame.init()
        
        from font_manager import get_font_manager
        font_mgr = get_font_manager()
        print("[OK] FontManager created")
        
        pygame.quit()
        print("[OK] Font test successful")
        
        return True
    except Exception as e:
        print(f"[ERROR] Font test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    tests = [
        test_imports,
        test_pygame_init,
        test_audio,
        test_fonts
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
            break
    
    if all_passed:
        print("\n[SUCCESS] All tests passed! The game should work.")
    else:
        print("\n[FAILED] Some tests failed.")
    
    sys.exit(0 if all_passed else 1)