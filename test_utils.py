"""
Test utils.py safe_events function.
"""

import os
import sys

# Set safe environment
os.environ['SDL_VIDEODRIVER'] = 'dummy'

def test_safe_events():
    """Test safe_events function works correctly."""
    print("=== Testing utils.safe_events ===")
    
    try:
        import pygame
        pygame.init()
        
        from utils import safe_events
        
        print("✓ utils.safe_events imported successfully")
        
        # Test normal operation
        events = safe_events()
        print(f"✓ safe_events() returned: {type(events)} with {len(events)} events")
        
        # Test it's actually a list
        assert isinstance(events, list), "safe_events() should return a list"
        print("✓ Return type is correct (list)")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    finally:
        try:
            pygame.quit()
        except:
            pass

if __name__ == "__main__":
    success = test_safe_events()
    print(f"Test result: {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
