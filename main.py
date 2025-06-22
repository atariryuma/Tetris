#!/usr/bin/env python3
"""
Tetris Game - Main Entry Point
A complete, multiplayer Tetris implementation with controller support.
"""

import sys
import pygame
from game import TetrisGame

def main():
    """Initialize and run the Tetris game."""
    try:
        # Initialize pygame
        pygame.init()
        
        # Create and run the game
        game = TetrisGame()
        game.run()
        
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        pygame.quit()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())