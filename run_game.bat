@echo off
rem run_game.bat

rem 1. ゲームを起動
python main.py

rem 2. ゲームが閉じたらこのバッチも終了
exit /B %ERRORLEVEL%

