"""
Test that there are no circular dependencies in the launcher structure.
"""

import subprocess
import sys
import os

def test_structure():
    """Test the launcher structure for circular dependencies."""
    print("=== Testing Launcher Structure ===")
    
    # Check run_game.bat content
    if os.path.exists("run_game.bat"):
        with open("run_game.bat", "r", encoding="utf-8") as f:
            bat_content = f.read()
        print("run_game.bat content:")
        print(bat_content)
        
        # Check if it contains circular calls
        if "run_game_windows.py" in bat_content:
            print("❌ Circular dependency detected: bat -> windows.py")
            return False
        else:
            print("✅ run_game.bat is clean (no circular calls)")
    
    # Check run_game_windows.py structure
    if os.path.exists("run_game_windows.py"):
        with open("run_game_windows.py", "r", encoding="utf-8") as f:
            py_content = f.read()
        
        # Check the flow
        if "run_game.bat" in py_content:
            print("❌ Circular dependency detected: windows.py -> bat")
            return False
        else:
            print("✅ run_game_windows.py is clean (no circular calls)")
    
    print("✅ No circular dependencies detected")
    return True

if __name__ == "__main__":
    success = test_structure()
    print(f"Test result: {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)