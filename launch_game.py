"""
Game launcher that handles different environments (Windows/WSL/headless).
"""

import os
import sys
import platform
import pygame

def detect_environment():
    """Detect the current environment and set up display accordingly."""
    system = platform.system()
    
    # Check if we're in WSL
    is_wsl = False
    try:
        with open('/proc/version', 'r') as f:
            if 'microsoft' in f.read().lower():
                is_wsl = True
    except:
        pass
    
    # Check if display is available
    has_display = os.environ.get('DISPLAY') is not None
    
    print(f"System: {system}")
    print(f"WSL: {is_wsl}")
    print(f"Display available: {has_display}")
    
    return system, is_wsl, has_display

def setup_display_environment():
    """Set up the display environment based on what's available."""
    system, is_wsl, has_display = detect_environment()
    
    if is_wsl and not has_display:
        print("WSL environment detected without display.")
        print("Setting up virtual display...")
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        return 'headless'
    
    elif system == 'Windows':
        print("Windows environment detected.")
        return 'windows'
    
    elif has_display:
        print("Linux environment with display detected.")
        return 'linux_gui'
    
    else:
        print("Headless environment detected.")
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        return 'headless'

def launch_game():
    """Launch the game with appropriate environment settings."""
    print("=== Tetris Game Launcher ===")
    
    # Detect and setup environment
    env_type = setup_display_environment()
    
    # Try to initialize pygame
    try:
        pygame.init()
        print("✓ Pygame initialized successfully")
    except Exception as e:
        print(f"✗ Pygame initialization failed: {e}")
        return False
    
    # Import and run the game
    try:
        from main import main
        print("✓ Game modules imported successfully")
        
        if env_type == 'headless':
            print("\n=== Running in Headless Mode ===")
            print("Note: This is a demonstration mode without visual output.")
            print("To play with graphics, run on Windows or Linux with display.")
            
            # Run a simplified game loop for demonstration
            run_demo_mode()
        else:
            print("\n=== Starting Full Game ===")
            main()
            
    except Exception as e:
        print(f"✗ Game failed to start: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def run_demo_mode():
    """Run a simplified demo without graphics."""
    print("\n🎮 Starting Tetris Demo Mode...")
    
    try:
        # Test core game systems
        from tetris_game import TetrisGame
        from constants import PlayerMode
        from audio_manager import AudioManager
        from font_manager import get_font_manager
        
        print("✓ Core systems loaded")
        
        # Create a test game
        game = TetrisGame(1, PlayerMode.HUMAN)
        print(f"✓ Game created - Score: {game.score}, Level: {game.level}")
        
        # Test font system
        font_manager = get_font_manager()
        print("✓ Font system ready")
        
        # Test audio system
        audio = AudioManager()
        print(f"✓ Audio system - Initialized: {audio.initialized}")
        
        print("\n=== Demo Complete ===")
        print("All systems working! Game is ready for GUI environment.")
        print("\nTo play with graphics:")
        print("1. Run on Windows")
        print("2. Or set up X11 forwarding in WSL")
        print("3. Or use a Linux desktop environment")
        
    except Exception as e:
        print(f"✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    success = launch_game()
    sys.exit(0 if success else 1)
