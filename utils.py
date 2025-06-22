"""
Utility functions for the Tetris game.
"""

import pygame

def safe_events():
    """Safely retrieve pending pygame events.

    Some environments occasionally raise errors when calling
    ``pygame.event.get`` directly, which can spam the console and halt
    input processing.  This helper pumps the event queue first and
    gracefully returns an empty list if any exception is raised.
    """

    try:
        # Ensure SDL processes internal actions before fetching events.
        pygame.event.pump()
        return pygame.event.get()
    except Exception as e:
        print(f"[WARN] Event polling error: {e}")
        return []
