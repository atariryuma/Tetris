"""
Windows-specific launcher for Tetris game with comprehensive error handling.
"""

import sys
import os
import subprocess
import time

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"Warning: Python {version.major}.{version.minor} detected")
        print("Recommended: Python 3.8 or higher")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import pygame
        print(f"✓ Pygame {pygame.version.ver}")
        return True
    except ImportError:
        print("✗ Pygame not found")
        print("Installing pygame...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame", "numpy"])
            print("✓ Dependencies installed")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install dependencies")
            return False

def setup_windows_environment():
    """Set up Windows-specific environment variables."""
    # Prevent pygame from trying to use DirectX which can cause issues
    os.environ['SDL_VIDEODRIVER'] = 'windib'
    # Ensure audio works properly
    os.environ['SDL_AUDIODRIVER'] = 'directsound'
    print("✓ Windows environment configured")

def run_game():
    """Run the Tetris game with error handling."""
    print("=== Tetris Game Launcher for Windows ===")
    print()
    
    # Check Python version
    if not check_python_version():
        print("Consider upgrading Python for best compatibility")
        input("Press Enter to continue anyway...")
    
    # Check dependencies
    if not check_dependencies():
        print("Cannot run game without dependencies")
        input("Press Enter to exit...")
        return False
    
    # Set up environment
    setup_windows_environment()
    
    # Try to run the game
    print("\nStarting Tetris game...")
    print("If the game window doesn't appear, check the console for error messages.")
    print()
    
    try:
        # Import and run the game
        from main import main
        return main() == 0
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Make sure all game files are in the same directory")
        return False
    except Exception as e:
        print(f"✗ Game error: {e}")
        print("\nTroubleshooting:")
        print("1. Try running as administrator")
        print("2. Check Windows graphics drivers")
        print("3. Disable antivirus temporarily")
        print("4. Try running: python main.py")
        return False

def main():
    """Main launcher function."""
    success = run_game()
    
    if success:
        print("\n🎉 Game finished successfully!")
    else:
        print("\n⚠️  Game encountered issues")
        print("\nAlternative ways to run:")
        print("1. Double-click main.py")
        print("2. Run: python main.py")
        print("3. Run: python safe_launcher.py")
    
    print("\nPress Enter to exit...")
    input()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())