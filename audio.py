"""
Simple Audio System for Tetris
Lightweight audio manager with fallback support.
"""

import pygame
import math

class SimpleAudio:
    """Simple audio system that works without external files."""
    
    def __init__(self):
        self.enabled = False
        self.sounds = {}
        
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.enabled = True
            self._generate_sounds()
            print("Audio system initialized")
        except Exception as e:
            print(f"Audio disabled: {e}")
    
    def _generate_sounds(self):
        """Generate simple sound effects."""
        try:
            self.sounds['move'] = self._generate_beep(200, 0.1)
            self.sounds['rotate'] = self._generate_beep(300, 0.1) 
            self.sounds['drop'] = self._generate_beep(150, 0.2)
            self.sounds['line'] = self._generate_beep(400, 0.3)
            self.sounds['game_over'] = self._generate_sweep(400, 200, 0.5)
        except Exception:
            self.enabled = False
    
    def _generate_beep(self, frequency: float, duration: float) -> pygame.mixer.Sound:
        """Generate a simple beep sound."""
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = []
        
        for i in range(frames):
            time_point = float(i) / sample_rate
            wave = math.sin(2 * math.pi * frequency * time_point)
            # Apply fade out
            fade = max(0, 1 - (i / frames) * 2)
            wave *= fade * 0.3  # Volume
            
            # Convert to 16-bit integer
            sample = int(wave * 32767)
            arr.extend([sample, sample])  # Stereo
        
        return pygame.sndarray.make_sound(arr)
    
    def _generate_sweep(self, start_freq: float, end_freq: float, duration: float) -> pygame.mixer.Sound:
        """Generate a frequency sweep."""
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = []
        
        for i in range(frames):
            time_point = float(i) / sample_rate
            progress = i / frames
            frequency = start_freq + (end_freq - start_freq) * progress
            wave = math.sin(2 * math.pi * frequency * time_point)
            wave *= (1 - progress) * 0.3  # Fade out
            
            sample = int(wave * 32767)
            arr.extend([sample, sample])
        
        return pygame.sndarray.make_sound(arr)
    
    def play(self, sound_name: str):
        """Play a sound effect."""
        if self.enabled and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except Exception:
                pass  # Ignore audio errors
    
    def cleanup(self):
        """Clean up audio resources."""
        if self.enabled:
            try:
                pygame.mixer.quit()
            except Exception:
                pass