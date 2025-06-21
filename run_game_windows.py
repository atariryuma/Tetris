#!/usr/bin/env python
"""
Tetris Game Launcher for Windows (Improved)
"""
import subprocess
import sys
import shutil


def try_command(cmd, description):
    """Execute a shell command, print description. Return True on success."""
    print(description)
    try:
        result = subprocess.run(cmd, check=True, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    print("=== Tetris Game Launcher for Windows ===")
    print("Starting game with the first available method...")

    # Helper to check if an executable exists
    def exists(exe):
        return shutil.which(exe) is not None

    # 1. Try python interpreter (direct)
    if exists("python"):
        if try_command("python main.py", "▶ python main.py を実行"):
            sys.exit(0)

    # 2. Try py launcher
    if exists("py"):
        if try_command("py main.py", "▶ py main.py を実行"):
            sys.exit(0)

    # All attempts failed
    print("❌ すべての起動に失敗しました。依存関係が正しくインストールされているか確認してください。")
    print("  pip install pygame")
    sys.exit(1)


if __name__ == "__main__":
    main()