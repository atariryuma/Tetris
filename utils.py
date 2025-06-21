"""
Utility functions for the Tetris game.
"""

import pygame

def safe_events():
    """pygame.event.get() を安全に呼び出し、例外発生時は空リストを返す"""
    try:
        return pygame.event.get()
    except Exception as e:
        print(f"[WARN] Event polling error: {e}")
        return []