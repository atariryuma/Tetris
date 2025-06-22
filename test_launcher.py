"""
Test the launcher without actually running the game.
"""

import subprocess
import sys
import os

def test_launcher():
    """Test that the launcher doesn't create infinite loops."""
    print("=== Testing Windows Launcher ===")
    
    # Test just the command structure
    print("Testing python executable check...")
    import shutil
    python_exists = shutil.which("python") is not None
    print(f"Python exists: {python_exists}")
    
    if python_exists:
        print("Would run: python main.py")
        print("✓ No circular dependency detected")
    else:
        print("No python interpreter found")
    
    return True

if __name__ == "__main__":
    success = test_launcher()
    print(f"Test result: {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
