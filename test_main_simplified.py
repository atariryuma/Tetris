#!/usr/bin/env python3
"""Simplified main.py for testing where it hangs."""

import pygame
import sys
import time
import traceback
from constants import *
from utils import safe_events

def main():
    print("=== SIMPLIFIED TETRIS TEST ===")
    print("Step 1: Initialize pygame")
    
    try:
        pygame.init()
        print("[OK] pygame.init() completed")
        
        print("Step 2: Set display mode")
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tetris Test")
        print("[OK] Display mode set")
        
        print("Step 3: Create clock")
        clock = pygame.time.Clock()
        print("[OK] Clock created")
        
        print("Step 4: Test game loop for 100 frames")
        running = True
        frame_count = 0
        
        while running and frame_count < 100:
            print(f"Frame {frame_count + 1}/100", end="\r")
            
            # Handle events
            try:
                events = safe_events()
                for event in events:
                    if event.type == pygame.QUIT:
                        running = False
                        print("\nQuit event received")
            except Exception as e:
                print(f"\nEvent handling error: {e}")
                running = False
            
            # Draw simple test screen
            screen.fill((50, 50, 50))
            pygame.draw.circle(screen, (255, 255, 255), (WINDOW_WIDTH//2, WINDOW_HEIGHT//2), 50)
            
            # Update display
            try:
                pygame.display.flip()
            except Exception as e:
                print(f"\nDisplay flip error: {e}")
                running = False
            
            # Clock tick
            try:
                clock.tick(60)
            except Exception as e:
                print(f"\nClock tick error: {e}")
                running = False
            
            frame_count += 1
        
        print(f"\n[OK] Completed {frame_count} frames successfully")
        
    except Exception as e:
        print(f"Error in main loop: {e}")
        traceback.print_exc()
    finally:
        print("Cleaning up...")
        pygame.quit()
        print("[OK] pygame.quit() completed")

if __name__ == "__main__":
    main()