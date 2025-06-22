"""
Test script for font rendering system.
"""

import os
import pygame
from font_manager import FontManager

def test_fonts():
    """Test font loading and rendering."""
    print("Testing font system...")
    
    # Initialize pygame
    pygame.init()
    
    # Create a small display for testing
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Font Test")
    
    # Initialize font manager
    font_manager = FontManager()
    
    print("\n=== Font Availability Test ===")
    
    # Test different font types
    font_types = ['title', 'ui', 'score', 'japanese', 'monospace']
    test_texts = {
        'title': 'TETRIS NEO',
        'ui': 'Game Menu',
        'score': '123456',
        'japanese': '三人対戦テトリス',
        'monospace': 'Code Text 123'
    }
    
    y_offset = 50
    for font_type in font_types:
        text = test_texts[font_type]
        print(f"Testing {font_type}: '{text}'")
        
        try:
            # Test rendering
            surface = font_manager.render_text(text, font_type, 32, (255, 255, 255))
            screen.blit(surface, (50, y_offset))
            y_offset += 60
            print(f"  ✓ {font_type} rendered successfully")
        except Exception as e:
            print(f"  ✗ {font_type} failed: {e}")
    
    # Test Japanese text specifically
    print("\n=== Japanese Text Test ===")
    japanese_texts = [
        "三人対戦テトリス NEO",
        "ゲームスタート",
        "参加する",
        "一時停止",
        "コントローラー対応"
    ]
    
    y_offset = 50
    for text in japanese_texts:
        try:
            surface = font_manager.render_text(text, 'japanese', 24, (255, 255, 0))
            screen.blit(surface, (400, y_offset))
            y_offset += 40
            print(f"  ✓ Rendered: '{text}'")
        except Exception as e:
            print(f"  ✗ Failed: '{text}' - {e}")
    
    # Update display
    pygame.display.flip()
    
    print("\n=== Font Size Test ===")
    sizes = [12, 16, 24, 32, 48, 64]
    for size in sizes:
        try:
            font = font_manager.get_font('ui', size)
            print(f"  ✓ Size {size}: {font}")
        except Exception as e:
            print(f"  ✗ Size {size} failed: {e}")
    
    print("\n=== Font Files Check ===")
    font_files = [
        'PressStart2P-Regular.ttf',
        'Orbitron-Regular.ttf', 
        'NotoSansJP-Regular.ttf',
        'SourceCodePro-Regular.ttf'
    ]
    
    fonts_dir = os.path.join(os.path.dirname(__file__), 'assets', 'fonts')
    for font_file in font_files:
        font_path = os.path.join(fonts_dir, font_file)
        if os.path.exists(font_path):
            file_size = os.path.getsize(font_path)
            print(f"  ✓ {font_file}: {file_size} bytes")
        else:
            print(f"  ✗ {font_file}: Missing")
    
    print("\nFont test complete. Closing automatically...")

    # Short delay so CI environments don't hang waiting for input
    running = True
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    timeout = 2000  # ms

    while running and pygame.time.get_ticks() - start_time < timeout:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                running = False
        clock.tick(60)
    
    # Cleanup
    font_manager.cleanup()
    pygame.quit()

if __name__ == "__main__":
    test_fonts()
