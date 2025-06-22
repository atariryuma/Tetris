"""
Font management system with support for Google Fonts and Japanese text.
"""

import pygame
import os
from typing import Dict, Optional, Tuple
from constants import DEBUG_PRINT

class FontManager:
    """Manages font loading and rendering with fallback support."""
    
    def __init__(self):
        self.fonts: Dict[str, Dict[int, pygame.font.Font]] = {}
        self.font_paths = {}
        self.fallback_fonts = {}
        
        # Initialize pygame font system
        pygame.font.init()
        
        # Set up font paths
        self._setup_font_paths()
        
        # Load fonts
        self._load_fonts()
    
    def _setup_font_paths(self):
        """Set up paths to font files."""
        font_dir = os.path.join(os.path.dirname(__file__), 'assets', 'fonts')
        
        self.font_paths = {
            'press_start': os.path.join(font_dir, 'PressStart2P-Regular.ttf'),
            'orbitron': os.path.join(font_dir, 'Orbitron-Regular.ttf'),
            'noto_jp': os.path.join(font_dir, 'NotoSansJP-Regular.ttf'),
            'source_code': os.path.join(font_dir, 'SourceCodePro-Regular.ttf'),
        }
        
        # Check which fonts are available
        available_fonts = {}
        for font_name, font_path in self.font_paths.items():
            if os.path.exists(font_path):
                available_fonts[font_name] = font_path
                print(f"✓ Font available: {font_name}")
            else:
                print(f"⚠ Font missing: {font_name} at {font_path}")
        
        self.font_paths = available_fonts
    
    def _load_fonts(self):
        """Load all available fonts in common sizes."""
        common_sizes = [12, 16, 18, 20, 24, 28, 32, 36, 40, 48, 56, 64, 72]
        
        for font_name, font_path in self.font_paths.items():
            self.fonts[font_name] = {}
            
            for size in common_sizes:
                try:
                    font = pygame.font.Font(font_path, size)
                    self.fonts[font_name][size] = font
                    
                except Exception as e:
                    if DEBUG_PRINT:
                        print(f"Failed to load {font_name} size {size}: {e}")
                    
                    # Fall back to system font
                    self.fonts[font_name][size] = pygame.font.Font(None, size)
        
        # Set up fallback fonts for different text types
        self._setup_fallbacks()
    
    def _setup_fallbacks(self):
        """Set up fallback font hierarchy."""
        self.fallback_fonts = {
            'title': ['press_start', 'orbitron', 'noto_jp'],  # Game titles
            'ui': ['orbitron', 'noto_jp', 'source_code'],     # UI elements
            'score': ['source_code', 'orbitron', 'noto_jp'], # Numbers/scores
            'japanese': ['noto_jp', 'orbitron'],              # Japanese text
            'monospace': ['source_code', 'press_start'],      # Monospace text
        }
    
    def get_font(self, font_type: str, size: int) -> pygame.font.Font:
        """
        Get a font of specified type and size.
        
        Args:
            font_type: Type of font ('title', 'ui', 'score', 'japanese', 'monospace')
            size: Font size in pixels
        
        Returns:
            pygame.font.Font object
        """
        # Get fallback hierarchy for this font type
        fallback_hierarchy = self.fallback_fonts.get(font_type, ['noto_jp', 'orbitron'])
        
        # Try each font in the hierarchy
        for font_name in fallback_hierarchy:
            if font_name in self.fonts:
                # Find closest available size
                available_sizes = list(self.fonts[font_name].keys())
                if available_sizes:
                    closest_size = min(available_sizes, key=lambda x: abs(x - size))
                    
                    # If the closest size is too far, create a new font
                    if abs(closest_size - size) > 8:
                        try:
                            font_path = self.font_paths[font_name]
                            new_font = pygame.font.Font(font_path, size)
                            self.fonts[font_name][size] = new_font
                            return new_font
                        except Exception:
                            # Fall through to use closest size
                            pass
                    
                    return self.fonts[font_name][closest_size]
        
        # Ultimate fallback to system font
        return pygame.font.Font(None, size)
    
    def render_text(self, text: str, font_type: str, size: int, color: Tuple[int, int, int], 
                   antialias: bool = True) -> pygame.Surface:
        """
        Render text with automatic font selection.
        
        Args:
            text: Text to render
            font_type: Type of font to use
            size: Font size
            color: Text color (R, G, B)
            antialias: Whether to use antialiasing
        
        Returns:
            pygame.Surface with rendered text
        """
        # Check if text contains Japanese characters
        has_japanese = any(ord(char) > 127 for char in text)
        
        if has_japanese and font_type != 'japanese':
            # Force Japanese font for Japanese text
            font_type = 'japanese'
        
        font = self.get_font(font_type, size)
        
        try:
            return font.render(text, antialias, color)
        except Exception as e:
            if DEBUG_PRINT:
                print(f"Failed to render text '{text}': {e}")
            
            # Fallback: try with system font
            fallback_font = pygame.font.Font(None, size)
            try:
                return fallback_font.render(text, antialias, color)
            except Exception:
                # Last resort: render placeholder
                return fallback_font.render("[TEXT]", antialias, color)
    
    def render_multiline_text(self, text: str, font_type: str, size: int, color: Tuple[int, int, int],
                            max_width: int = None, line_spacing: int = 5) -> pygame.Surface:
        """
        Render multiline text with word wrapping.
        
        Args:
            text: Text to render (can contain \\n)
            font_type: Type of font to use
            size: Font size
            color: Text color
            max_width: Maximum width before wrapping (None for no wrapping)
            line_spacing: Extra spacing between lines
        
        Returns:
            pygame.Surface with rendered text
        """
        font = self.get_font(font_type, size)
        lines = text.split('\n')
        
        if max_width:
            # Word wrap long lines
            wrapped_lines = []
            for line in lines:
                if font.size(line)[0] <= max_width:
                    wrapped_lines.append(line)
                else:
                    # Simple word wrapping
                    words = line.split(' ')
                    current_line = ""
                    
                    for word in words:
                        test_line = current_line + (" " if current_line else "") + word
                        if font.size(test_line)[0] <= max_width:
                            current_line = test_line
                        else:
                            if current_line:
                                wrapped_lines.append(current_line)
                            current_line = word
                    
                    if current_line:
                        wrapped_lines.append(current_line)
            
            lines = wrapped_lines
        
        # Render each line
        line_surfaces = []
        for line in lines:
            if line.strip():  # Skip empty lines
                surface = self.render_text(line, font_type, size, color)
                line_surfaces.append(surface)
            else:
                # Empty line - create a spacer
                empty_surface = pygame.Surface((1, font.get_height()), pygame.SRCALPHA)
                line_surfaces.append(empty_surface)
        
        if not line_surfaces:
            return pygame.Surface((1, 1), pygame.SRCALPHA)
        
        # Calculate total size
        total_width = max(surface.get_width() for surface in line_surfaces)
        total_height = sum(surface.get_height() for surface in line_surfaces) + line_spacing * (len(line_surfaces) - 1)
        
        # Create final surface
        final_surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
        
        # Blit all lines
        y_offset = 0
        for surface in line_surfaces:
            final_surface.blit(surface, (0, y_offset))
            y_offset += surface.get_height() + line_spacing
        
        return final_surface
    
    def get_text_size(self, text: str, font_type: str, size: int) -> Tuple[int, int]:
        """Get the size of rendered text without actually rendering it."""
        font = self.get_font(font_type, size)
        return font.size(text)
    
    def cleanup(self):
        """Clean up font resources."""
        self.fonts.clear()
        if DEBUG_PRINT:
            print("Font manager cleaned up")

# Global font manager instance
font_manager = None

def get_font_manager() -> FontManager:
    """Get the global font manager instance."""
    global font_manager
    if font_manager is None:
        font_manager = FontManager()
    return font_manager

def cleanup_fonts():
    """Clean up global font manager."""
    global font_manager
    if font_manager:
        font_manager.cleanup()
        font_manager = None
