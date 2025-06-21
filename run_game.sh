#!/bin/bash

echo "=== Tetris Game Launcher for Linux/WSL ==="
echo

# Check if we're in the correct directory
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found. Please run this script from the Tetris directory."
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect environment
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo "WSL environment detected"
    WSL_ENV=true
else
    echo "Linux environment detected"
    WSL_ENV=false
fi

# Check for display
if [ -z "$DISPLAY" ]; then
    echo "No display detected - will run in headless mode"
    export SDL_VIDEODRIVER=dummy
else
    echo "Display available: $DISPLAY"
fi

# Try to run with uv first
if command_exists uv; then
    echo "Running with uv..."
    uv run python main.py
    exit_code=$?
elif command_exists python3; then
    echo "Running with python3..."
    python3 main.py
    exit_code=$?
elif command_exists python; then
    echo "Running with python..."
    python main.py
    exit_code=$?
else
    echo "Error: No Python interpreter found"
    exit 1
fi

if [ $exit_code -eq 0 ]; then
    echo "Game finished successfully!"
else
    echo "Game exited with error code: $exit_code"
    echo
    echo "If you see pygame errors, try installing dependencies:"
    echo "  pip install pygame numpy"
    echo "  or: apt-get install python3-pygame python3-numpy"
fi

exit $exit_code