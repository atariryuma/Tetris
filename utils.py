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
        events = pygame.event.get()
        return events
    except SystemError as e:
        # Handle Joy-Con controller crashes specifically
        if "exception set" in str(e):
            print("[WARN] Controller crash detected - continuing without events")
            return []
        else:
            raise
    except Exception as e:
        print(f"[WARN] Event polling error: {e}")
        return []
