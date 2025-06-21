@echo off
echo === Tetris Game Launcher for Windows ===
echo.

REM Check if we're in the correct directory
if not exist "main.py" (
    echo Error: main.py not found. Please run this script from the Tetris directory.
    pause
    exit /b 1
)

REM Try Windows-specific launcher first
echo Trying Windows-specific launcher...
python run_game_windows.py
if %ERRORLEVEL% EQU 0 goto :success

echo.
echo Windows launcher failed. Trying with uv...
uv run python main.py
if %ERRORLEVEL% EQU 0 goto :success

echo.
echo uv not found or failed. Trying with regular Python...
python main.py
if %ERRORLEVEL% EQU 0 goto :success

echo.
echo Regular Python failed. Trying with py command...
py main.py
if %ERRORLEVEL% EQU 0 goto :success

echo.
echo All attempts failed. Please ensure Python and pygame are installed.
echo You can install dependencies with: pip install pygame numpy
pause
exit /b 1

:success
echo.
echo Game finished successfully!
pause