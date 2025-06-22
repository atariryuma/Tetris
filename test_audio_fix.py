#!/usr/bin/env python3
"""Test script to check if audio system fixes work."""

import sys
import pygame

def test_audio_system():
    """Test the audio system without running the full game."""
    print("Testing audio system fixes...")
    
    try:
        # Initialize pygame
        pygame.init()
        print("✓ Pygame initialized successfully")
        
        # Import our audio manager
        from audio_manager import AudioManager
        print("✓ AudioManager imported successfully")
        
        # Create audio manager instance
        audio_manager = AudioManager()
        print("✓ AudioManager created successfully")
        
        # Test playing a sound effect
        audio_manager.play_sfx('menu_select')
        print("✓ Sound effect played successfully")
        
        # Test volume controls
        volume_info = audio_manager.get_volume_info()
        print(f"✓ Volume info: {volume_info}")
        
        # Cleanup
        audio_manager.cleanup()
        pygame.quit()
        print("✓ Audio system cleaned up successfully")
        
        print("\n🎉 All audio system tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Audio system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_audio_system()
    sys.exit(0 if success else 1)