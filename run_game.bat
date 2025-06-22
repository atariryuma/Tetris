@echo off
echo Starting Tetris Game...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo Game encountered an error.
    pause
) else (
    echo Game completed successfully.
)