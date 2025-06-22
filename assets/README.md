# Assets Directory

This directory contains game assets including fonts, sounds, and images.

## Directory Structure

- `fonts/` - Optional font files for custom UI text
- `sounds/` - Audio files (BGM and sound effects)
- `images/` - Image files (icons, sprites, etc.)

## Recommended Google Fonts

The following high-quality Google Fonts are supported. Download them separately for the best experience:

### Game Fonts
- **Press Start 2P** (`PressStart2P-Regular.ttf`) - 118KB
  - Classic 8-bit arcade game font
  - Used for game titles and retro elements
  - Perfect pixel-perfect rendering

- **Orbitron** (`Orbitron-Regular.ttf`) - 38KB
  - Futuristic, sci-fi inspired font
  - Used for UI elements and menus
  - Clean, modern gaming aesthetic

### Code/Monospace Fonts
- **Source Code Pro** (`SourceCodePro-Regular.ttf`) - 212KB
  - Professional monospace font by Adobe
  - Used for scores, numbers, and technical text
  - Excellent readability for numeric data

### Japanese Support
- **Noto Sans JP** (`NotoSansJP-Regular.ttf`) - 9.6MB
  - Complete Japanese character support
  - Used for all Japanese text rendering
  - Covers Hiragana, Katakana, and Kanji

## Audio Files

The game will automatically generate sound effects if audio files are not present. To use custom audio files, place them in the `sounds/` directory with the following names:

### Sound Effects (.wav format recommended)
- `piece_move.wav` - Piece movement sound
- `piece_rotate.wav` - Piece rotation sound
- `piece_drop.wav` - Hard drop sound
- `line_clear.wav` - Line clear sound
- `tetris.wav` - Tetris (4-line clear) sound
- `game_over.wav` - Game over sound
- `level_up.wav` - Level up sound
- `menu_select.wav` - Menu selection sound
- `menu_navigate.wav` - Menu navigation sound
- `garbage_attack.wav` - Garbage attack sound

### Background Music (.ogg format recommended)
- `menu_music.ogg` - Main menu background music
- `game_music.ogg` - In-game background music

## Images

- `icon.png` - Game window icon (32x32 or 64x64 recommended)

## Font Files

The game uses system fonts by default. Custom fonts can be added to the `fonts/` directory and loaded in the UI renderer.

## Adding Custom Assets

1. Place audio files in the appropriate subdirectory
2. Ensure file names match the expected names listed above
3. Supported audio formats: WAV, OGG, MP3
4. Supported image formats: PNG, JPG, BMP
5. The game will fall back to generated content if files are missing