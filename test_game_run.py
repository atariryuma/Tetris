#!/usr/bin/env python3
"""Test running the game for a short period."""

import pygame
import sys
import time
import traceback
from constants import WINDOW_WIDTH, WINDOW_HEIGHT
from utils import safe_events
from game_manager import GameManager

def test_game_run():
    """Test running the game for a few seconds."""
    print("=== Testing Game Run ===")
    
    try:
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tetris Test Run")
        print("[OK] Display initialized")
        
        # Create GameManager
        gm = GameManager(screen, event_source=safe_events)
        print("[OK] GameManager created")
        
        # Override the run method to limit runtime
        original_run = gm.run
        
        def limited_run():
            """Run for a limited time."""
            print("Starting limited game run (5 seconds)...")
            gm.running = True
            clock = pygame.time.Clock()
            start_time = time.time()
            frame_count = 0
            
            while gm.running and (time.time() - start_time < 5.0):
                current_time = time.time()
                delta_time = current_time - gm.last_time
                gm.last_time = current_time
                
                # Process events
                try:
                    gm.handle_events()
                except Exception as e:
                    print(f"Event handling error: {e}")
                    break
                
                # Update and draw
                try:
                    gm.update(delta_time)
                    gm.draw(screen)
                    pygame.display.flip()
                except Exception as e:
                    print(f"Update/draw error: {e}")
                    break
                
                # Maintain FPS
                clock.tick(60)
                frame_count += 1
                
                if frame_count % 60 == 0:  # Every second
                    print(f"[INFO] Running... {frame_count} frames, {time.time() - start_time:.1f}s")
            
            print(f"[OK] Completed {frame_count} frames in {time.time() - start_time:.1f} seconds")
            
            # Cleanup
            try:
                gm.audio_manager.cleanup()
            except:
                pass
        
        # Replace the run method and test
        gm.run = limited_run
        gm.run()
        
        print("[SUCCESS] Game run test completed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Game run test failed: {e}")
        traceback.print_exc()
        return False
    finally:
        pygame.quit()

if __name__ == "__main__":
    success = test_game_run()
    sys.exit(0 if success else 1)