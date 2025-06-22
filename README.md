# Tetris Game

A complete, professional-grade Tetris implementation with clean architecture and controller support.

## Features

- **Complete Tetris gameplay** with proper rotation system
- **Keyboard and game controller support** (Xbox, PlayStation, Nintendo)
- **Professional game architecture** with clean separation of concerns
- **Built-in audio system** with generated sound effects
- **Clean, maintainable code** following best practices

## Installation

1. Install Python 3.8 or higher
2. Install pygame:
   ```bash
   pip install pygame
   ```

## How to Run

### Windows
Double-click `run_game.bat` or run:
```cmd
python main.py
```

### Linux/Mac
```bash
chmod +x run_game.sh
./run_game.sh
```

Or directly:
```bash
python3 main.py
```

## Controls

### Keyboard
- **Arrow Keys**: Move pieces left/right/down
- **Up Arrow**: Hard drop
- **Z**: Rotate piece
- **Space**: Start game (from menu)
- **ESC**: Pause/Resume
- **R**: Restart (when game over)

### Game Controllers
- **D-Pad/Left Stick**: Move pieces
- **Face buttons**: Rotate and drop
- Automatically detected and configured

## Game Features

- **Line clearing** with score bonuses
- **Level progression** with increasing speed
- **Next piece preview**
- **Score tracking**
- **Sound effects** for all actions
- **Pause functionality**
- **Game over detection** with restart option

## Architecture

The game is built with a clean, modular architecture:

- `main.py` - Entry point and initialization
- `game.py` - Complete game engine with all systems
- `audio.py` - Simple audio system with generated sounds

## Development

The codebase follows professional standards:
- Clean separation of concerns
- Comprehensive error handling
- Modular design for easy extension
- Well-documented code
- Type hints for better maintainability

## System Requirements

- Python 3.8+
- pygame 2.5.0+
- Works on Windows, Linux, and macOS
- Supports both keyboard and game controllers

## Troubleshooting

If you encounter issues:

1. **Audio not working**: The game will run without audio if there are sound system issues
2. **Controller not detected**: Try unplugging and reconnecting the controller
3. **Game won't start**: Ensure pygame is installed correctly

## License

MIT License - Feel free to use and modify as needed.