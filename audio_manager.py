"""
Audio management system for BGM and sound effects.
"""

import pygame
import os
from typing import Dict, Optional
from constants import MASTER_VOLUME, MUSIC_VOLUME, SFX_VOLUME

class AudioManager:
    """Manages all audio playback including BGM and sound effects."""
    
    def __init__(self):
        self.initialized = False
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.current_bgm: Optional[str] = None
        self.master_volume = MASTER_VOLUME
        self.music_volume = MUSIC_VOLUME
        self.sfx_volume = SFX_VOLUME
        
        # Initialize pygame mixer
        self._init_mixer()
        
        # Load default sounds
        self._load_default_sounds()

    def _init_mixer(self):
        """Initialize pygame mixer with optimal settings."""
        try:
            # Initialize with high quality settings
            pygame.mixer.pre_init(
                frequency=44100,
                size=-16,
                channels=2,
                buffer=512
            )
            pygame.mixer.init()
            self.initialized = True
            print("Audio system initialized successfully")
        except pygame.error as e:
            print(f"Failed to initialize audio system: {e}")
            self.initialized = False

    def _load_default_sounds(self):
        """Load default sound effects."""
        if not self.initialized:
            return
            
        # Define default sounds (will be generated if files don't exist)
        default_sounds = {
            'piece_move': self._generate_move_sound(),
            'piece_rotate': self._generate_rotate_sound(),
            'piece_drop': self._generate_drop_sound(),
            'line_clear': self._generate_line_clear_sound(),
            'tetris': self._generate_tetris_sound(),
            'game_over': self._generate_game_over_sound(),
            'level_up': self._generate_level_up_sound(),
            'menu_select': self._generate_menu_select_sound(),
            'menu_navigate': self._generate_menu_navigate_sound(),
            'garbage_attack': self._generate_garbage_sound(),
        }
        
        # Try to load from files first, then use generated sounds
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets', 'sounds')
        
        for sound_name, default_sound in default_sounds.items():
            sound_path = os.path.join(assets_dir, f'{sound_name}.wav')
            
            try:
                if os.path.exists(sound_path):
                    self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                    print(f"Loaded sound: {sound_name}")
                else:
                    self.sounds[sound_name] = default_sound
                    print(f"Using generated sound: {sound_name}")
                    
                # Set initial volume
                self.sounds[sound_name].set_volume(self.sfx_volume * self.master_volume)
                
            except pygame.error as e:
                print(f"Failed to load sound {sound_name}: {e}")
                self.sounds[sound_name] = default_sound

    def _generate_move_sound(self) -> pygame.mixer.Sound:
        """Generate a simple move sound."""
        return self._generate_tone(220, 0.1, 0.3)

    def _generate_rotate_sound(self) -> pygame.mixer.Sound:
        """Generate a simple rotate sound."""
        return self._generate_tone(330, 0.1, 0.3)

    def _generate_drop_sound(self) -> pygame.mixer.Sound:
        """Generate a simple drop sound."""
        return self._generate_tone(110, 0.2, 0.4)

    def _generate_line_clear_sound(self) -> pygame.mixer.Sound:
        """Generate a line clear sound."""
        return self._generate_chord([440, 554, 659], 0.5, 0.6)

    def _generate_tetris_sound(self) -> pygame.mixer.Sound:
        """Generate a tetris (4-line clear) sound."""
        return self._generate_chord([440, 554, 659, 880], 0.8, 0.8)

    def _generate_game_over_sound(self) -> pygame.mixer.Sound:
        """Generate a game over sound."""
        return self._generate_descending_tone(440, 220, 1.0, 0.7)

    def _generate_level_up_sound(self) -> pygame.mixer.Sound:
        """Generate a level up sound."""
        return self._generate_ascending_tone(220, 440, 0.6, 0.6)

    def _generate_menu_select_sound(self) -> pygame.mixer.Sound:
        """Generate a menu select sound."""
        return self._generate_tone(660, 0.1, 0.4)

    def _generate_menu_navigate_sound(self) -> pygame.mixer.Sound:
        """Generate a menu navigate sound."""
        return self._generate_tone(440, 0.05, 0.2)

    def _generate_garbage_sound(self) -> pygame.mixer.Sound:
        """Generate a garbage attack sound."""
        return self._generate_noise(0.3, 0.5)

    def _generate_tone(self, frequency: float, duration: float, volume: float) -> pygame.mixer.Sound:
        """Generate a simple sine wave tone."""
        import math
        import numpy as np
        
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        # Generate mono audio
        mono_data = []
        for i in range(frames):
            t = i / sample_rate
            wave = math.sin(2 * math.pi * frequency * t) * volume
            # Apply fade out
            fade = max(0, 1 - (i / frames) * 2)
            wave *= fade
            # Convert to 16-bit integer
            sample = int(wave * 32767)
            mono_data.append(sample)
        
        # Convert to stereo 2D array: shape (frames, 2)
        stereo_array = np.zeros((frames, 2), dtype=np.int16)
        stereo_array[:, 0] = mono_data  # Left channel
        stereo_array[:, 1] = mono_data  # Right channel
        
        return pygame.sndarray.make_sound(stereo_array)

    def _generate_chord(self, frequencies: list, duration: float, volume: float) -> pygame.mixer.Sound:
        """Generate a chord with multiple frequencies."""
        import math
        import numpy as np
        
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        # Generate mono audio
        mono_data = []
        for i in range(frames):
            t = i / sample_rate
            wave = 0
            for freq in frequencies:
                wave += math.sin(2 * math.pi * freq * t) * volume / len(frequencies)
            
            # Apply fade out
            fade = max(0, 1 - (i / frames) * 1.5)
            wave *= fade
            sample = int(wave * 32767)
            mono_data.append(sample)
        
        # Convert to stereo 2D array
        stereo_array = np.zeros((frames, 2), dtype=np.int16)
        stereo_array[:, 0] = mono_data  # Left channel
        stereo_array[:, 1] = mono_data  # Right channel
        
        return pygame.sndarray.make_sound(stereo_array)

    def _generate_ascending_tone(self, start_freq: float, end_freq: float, duration: float, volume: float) -> pygame.mixer.Sound:
        """Generate an ascending tone sweep."""
        import math
        import numpy as np
        
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        # Generate mono audio
        mono_data = []
        for i in range(frames):
            t = i / sample_rate
            progress = i / frames
            frequency = start_freq + (end_freq - start_freq) * progress
            wave = math.sin(2 * math.pi * frequency * t) * volume
            
            # Apply envelope
            envelope = math.sin(math.pi * progress)
            wave *= envelope
            sample = int(wave * 32767)
            mono_data.append(sample)
        
        # Convert to stereo 2D array
        stereo_array = np.zeros((frames, 2), dtype=np.int16)
        stereo_array[:, 0] = mono_data  # Left channel
        stereo_array[:, 1] = mono_data  # Right channel
        
        return pygame.sndarray.make_sound(stereo_array)

    def _generate_descending_tone(self, start_freq: float, end_freq: float, duration: float, volume: float) -> pygame.mixer.Sound:
        """Generate a descending tone sweep."""
        import math
        import numpy as np
        
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        # Generate mono audio
        mono_data = []
        for i in range(frames):
            t = i / sample_rate
            progress = i / frames
            frequency = start_freq + (end_freq - start_freq) * progress
            wave = math.sin(2 * math.pi * frequency * t) * volume
            
            # Apply envelope
            envelope = 1 - progress * 0.8
            wave *= envelope
            sample = int(wave * 32767)
            mono_data.append(sample)
        
        # Convert to stereo 2D array
        stereo_array = np.zeros((frames, 2), dtype=np.int16)
        stereo_array[:, 0] = mono_data  # Left channel
        stereo_array[:, 1] = mono_data  # Right channel
        
        return pygame.sndarray.make_sound(stereo_array)

    def _generate_noise(self, duration: float, volume: float) -> pygame.mixer.Sound:
        """Generate white noise."""
        import random
        import numpy as np
        
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        # Generate mono audio
        mono_data = []
        for i in range(frames):
            # Generate random noise
            noise = random.uniform(-1, 1) * volume
            
            # Apply fade out
            fade = max(0, 1 - (i / frames) * 3)
            noise *= fade
            
            sample = int(noise * 32767)
            mono_data.append(sample)
        
        # Convert to stereo 2D array
        stereo_array = np.zeros((frames, 2), dtype=np.int16)
        stereo_array[:, 0] = mono_data  # Left channel
        stereo_array[:, 1] = mono_data  # Right channel
        
        return pygame.sndarray.make_sound(stereo_array)

    def play_bgm(self, bgm_name: str, loop: bool = True):
        """Play background music with robust error handling."""
        if not self.initialized:
            return
            
        # Check if mixer is properly initialized
        try:
            if not pygame.mixer.get_init():
                print(f"Audio mixer not initialized, skipping BGM: {bgm_name}")
                return
        except pygame.error:
            print(f"Cannot check mixer status, skipping BGM: {bgm_name}")
            return
            
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets', 'sounds')
        bgm_path = os.path.join(assets_dir, f'{bgm_name}.ogg')
        
        if os.path.exists(bgm_path):
            try:
                pygame.mixer.music.load(bgm_path)
                pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
                pygame.mixer.music.play(-1 if loop else 0)
                self.current_bgm = bgm_name
                print(f"Playing BGM: {bgm_name}")
            except (pygame.error, OSError, IOError) as e:
                print(f"Failed to play BGM {bgm_name}: {e}")
        else:
            # Silent fallback - only warn once per BGM
            if hasattr(self, '_missing_bgm_warned'):
                if bgm_name not in self._missing_bgm_warned:
                    print(f"BGM file not found, continuing without music: {bgm_name}")
                    self._missing_bgm_warned.add(bgm_name)
            else:
                self._missing_bgm_warned = {bgm_name}
                print(f"BGM file not found, continuing without music: {bgm_name}")

    def stop_bgm(self):
        """Stop background music."""
        if not self.initialized:
            return
            
        pygame.mixer.music.stop()
        self.current_bgm = None

    def play_sfx(self, sound_name: str, volume_multiplier: float = 1.0):
        """Play a sound effect."""
        if not self.initialized or sound_name not in self.sounds:
            return
            
        sound = self.sounds[sound_name]
        original_volume = sound.get_volume()
        sound.set_volume(original_volume * volume_multiplier)
        sound.play()

    def set_master_volume(self, volume: float):
        """Set master volume (0.0 to 1.0)."""
        self.master_volume = max(0.0, min(1.0, volume))
        
        # Update all sound volumes
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume * self.master_volume)
        
        # Update music volume
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)

    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)

    def set_sfx_volume(self, volume: float):
        """Set sound effects volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))
        
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume * self.master_volume)

    def get_volume_info(self) -> dict:
        """Get current volume settings."""
        return {
            'master': self.master_volume,
            'music': self.music_volume,
            'sfx': self.sfx_volume
        }

    def is_playing_bgm(self) -> bool:
        """Check if background music is playing."""
        return self.initialized and pygame.mixer.music.get_busy()

    def cleanup(self):
        """Clean up audio resources."""
        if self.initialized:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except pygame.error:
                # Audio might already be cleaned up or not initialized
                pass
            self.initialized = False
            print("Audio system cleaned up")
