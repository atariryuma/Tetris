"""
Utility functions for the Tetris game.
"""

import pygame

def safe_events():
    """Safely call ``pygame.event.get()`` and return an empty list on failure."""
    try:
        return pygame.event.get()
    except Exception as e:
        print(f"[WARN] Event polling error: {e}")
        return []
