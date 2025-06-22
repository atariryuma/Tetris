# 三人対戦テトリス NEO - Python Edition

A modern, feature-rich multiplayer Tetris game built with Python and Pygame, supporting up to 3 simultaneous players with universal gamepad support.

## Features

### 🎮 Universal Controller Support
- **Xbox Controllers**: Xbox One, Xbox Series X/S
- **PlayStation Controllers**: DualShock 4, DualSense (PS5)
- **Nintendo Switch Pro Controller**
- **Generic USB Gamepads**: Automatic mapping fallback
- **Hot-plug Support**: Connect controllers during gameplay
- **Keyboard Fallback**: Full game playable with keyboard

### 🎯 Advanced Tetris Mechanics
- **Standard Rotation System (SRS)** with proper wall kicks
- **Ghost piece** preview showing drop position
- **Hold piece** functionality
- **Hard drop** and **soft drop**
- **Line clear animations** with particle effects
- **T-spin detection** (framework ready)
- **Garbage attack system** for multiplayer combat

### 🤖 Smart AI Players
- **Multiple difficulty levels**: Easy, Medium, Hard, Expert
- **Advanced evaluation**: Height, holes, bumpiness, wells analysis
- **Adaptive strategy**: Changes tactics based on game state
- **Natural movement**: Realistic timing and decision making

### 🎵 Rich Audio Experience
- **Procedural audio generation**: No external files required
- **Dynamic sound effects**: Movement, rotation, line clears, attacks
- **Background music support**: Menu and gameplay tracks
- **Volume controls**: Master, music, and SFX independently adjustable

### 🎨 Beautiful Visuals
- **Retro-modern aesthetic**: Clean lines with visual flair
- **Particle effects**: Line clear celebrations and attack indicators
- **Smooth animations**: Piece movement and UI transitions
- **Responsive design**: Adapts to different player counts
- **Visual feedback**: Flash effects for attacks and achievements

## Installation

### Prerequisites
- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Quick Setup with uv (Recommended)

```bash
# Clone or download the project
cd tetris

# Install dependencies
uv sync

# Run the game
uv run python main.py
```

### Alternative Setup with pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

## Controls

### Keyboard Controls

#### Player 1 (Default)
- **Arrow Keys**: Move pieces left/right/down
- **Z**: Rotate clockwise
- **X**: Rotate counter-clockwise
- **C**: Hold piece
- **Up Arrow**: Hard drop

#### Player 2
- **A/D**: Move left/right
- **S**: Soft drop
- **Q**: Rotate clockwise
- **E**: Rotate counter-clockwise
- **R**: Hold piece
- **W**: Hard drop

#### Player 3
- **J/L**: Move left/right
- **K**: Soft drop
- **U**: Rotate clockwise
- **O**: Rotate counter-clockwise
- **P**: Hold piece
- **I**: Hard drop

#### Global Controls
- **ESC**: Pause/Resume/Menu
- **R**: Restart game (during play or game over)
- **F1**: Show volume information
- **F2/F3**: Increase/Decrease master volume

### Gamepad Controls

#### Universal Mapping (Works with Xbox, PlayStation, Nintendo)
- **D-Pad/Left Stick**: Move pieces and navigate menus
- **A Button (Xbox) / X Button (PlayStation)**: Rotate clockwise
- **B Button (Xbox) / Circle Button (PlayStation)**: Rotate counter-clockwise
- **Y Button (Xbox) / Triangle Button (PlayStation)**: Hard drop
- **X Button (Xbox) / Square Button (PlayStation)**: Hold piece
- **Start/Options Button**: Pause/Resume
- **Left/Right Bumpers**: Alternative rotation controls

## Game Modes

### Player Setup
Before starting a game, configure each of the three player slots:

- **参加する (Human)**: Human player with controller or keyboard
- **CPU**: Computer-controlled player with adjustable AI
- **参加しない (Off)**: Slot disabled

### Multiplayer Combat
When multiple players are active:
- Clearing **2+ lines** sends garbage blocks to opponents
- **Double**: 1 garbage line
- **Triple**: 2 garbage lines  
- **Tetris (4 lines)**: 4 garbage lines
- Garbage blocks have random holes for counterplay

### Scoring System
- **Line Clears**: 100-800 points based on lines cleared
- **Soft Drop**: 1 point per cell
- **Hard Drop**: 2 points per cell
- **Level Multiplier**: All scores increase with level
- **T-Spins**: Bonus points (framework implemented)

## Audio Assets

The game generates all audio procedurally, but supports custom audio files:

### Sound Effects (`.wav` format)
Place in `assets/sounds/`:
- `piece_move.wav` - Piece movement
- `piece_rotate.wav` - Piece rotation
- `piece_drop.wav` - Hard drop
- `line_clear.wav` - Line clear
- `tetris.wav` - 4-line clear
- `game_over.wav` - Game over
- `level_up.wav` - Level advancement
- `menu_select.wav` - Menu selection
- `menu_navigate.wav` - Menu navigation
- `garbage_attack.wav` - Attack sound

### Background Music (`.ogg` format)
- `menu_music.ogg` - Main menu
- `game_music.ogg` - Gameplay

## Architecture

### Core Systems
- **`tetris_game.py`**: Complete Tetris rules implementation
- **`input_manager.py`**: Universal gamepad and keyboard input
- **`cpu_ai.py`**: AI players with multiple difficulty levels
- **`audio_manager.py`**: Procedural audio generation and playback
- **`ui_renderer.py`**: All visual rendering and effects
- **`game_manager.py`**: Coordinates all systems and game states

### Key Features
- **Modular Design**: Each system is independently testable
- **Event-Driven Architecture**: Loose coupling between components
- **Universal Input**: Same code path for all input devices
- **Scalable Rendering**: Efficient for 1-3 simultaneous players
- **Resource Management**: Automatic cleanup and memory management

## Development

### Testing
```bash
# Run core game logic tests
uv run python test_game.py

# Run with debug output
DEBUG_CONTROLLERS=true uv run python main.py
```

### Configuration
Modify `constants.py` for game tuning:
- **Timing**: Drop speeds, input intervals
- **Visual**: Colors, block sizes, animation speeds  
- **Audio**: Volume levels, sound generation parameters
- **Gameplay**: Scoring values, AI difficulty weights

### Adding Custom Audio
1. Place audio files in `assets/sounds/`
2. Use supported formats: WAV, OGG, MP3
3. Follow naming convention in `assets/README.md`
4. Game falls back to generated audio if files missing

## Troubleshooting

### Common Issues

#### "No audio device" error
- **Linux**: Install `pulseaudio` or `alsa`
- **Windows**: Usually indicates driver issues
- **Workaround**: Game continues without audio

#### Controllers not detected
- **Check**: Controllers are properly connected
- **Try**: Press any button to activate controller
- **Debug**: Set `DEBUG_CONTROLLERS=true` for detailed logs

#### Performance issues
- **Check**: Disable VSync with `VSYNC=false` in constants.py
- **Monitor**: Use F1 to check FPS in debug mode
- **Reduce**: Particle count in `PARTICLE_COUNT` setting

#### Import errors
- **Ensure**: Python 3.11+ installed
- **Install**: All dependencies with `uv sync` or `pip install -r requirements.txt`
- **Check**: Virtual environment activation

## License

This project is released under the MIT License. See `LICENSE` file for details.

## Contributing

Contributions welcome! Areas for enhancement:
- Additional piece types or game modes
- Enhanced visual effects and shaders
- Online multiplayer support
- Tournament/ranking system
- Custom key bindings interface
- Mobile/touch controls

---

**Enjoy playing! 🎮✨**
