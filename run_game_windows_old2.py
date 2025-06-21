"""
Windows-specific launcher for Tetris game with immediate success termination.
"""

import subprocess
import sys
import shutil
import os

def try_command(cmd, description):
    """コマンドを実行し、成功したら True を返す"""
    print(description)
    try:
        subprocess.run(cmd, check=True, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def setup_windows_environment():
    """Set up Windows-specific environment variables."""
    # Set up optimal Windows environment
    if 'SDL_VIDEODRIVER' not in os.environ:
        os.environ['SDL_VIDEODRIVER'] = 'windib'  # Most compatible
    
    if 'SDL_AUDIODRIVER' not in os.environ:
        os.environ['SDL_AUDIODRIVER'] = 'directsound'
    
    # Reduce event polling issues
    os.environ['SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS'] = '1'

def main():
    """Main launcher with immediate success termination."""
    print("=== Tetris Game Launcher for Windows ===")
    print("Starting game with the first available method...")
    print()
    
    # Set up Windows environment
    setup_windows_environment()
    
    # 実行可能をチェックするヘルパー
    def exists(exe):
        return shutil.which(exe) is not None

    # 1. Python モジュールから直接実行（最優先）
    if exists("python"):
        if try_command("python main.py", "▶ python main.py を実行"):
            print("\n🎉 ゲームが正常に起動しました！")
            sys.exit(0)

    # 2. 'py' コマンド（Windows Python Launcher）
    if exists("py"):
        if try_command("py main.py", "▶ py main.py を実行"):
            print("\n🎉 ゲームが正常に起動しました！")
            sys.exit(0)

    # 3. uv コマンド（開発者向け）
    if exists("uv"):
        if try_command("uv run python main.py", "▶ uv run python main.py を実行"):
            print("\n🎉 ゲームが正常に起動しました！")
            sys.exit(0)

    # 4. Windows バッチファイル（最終手段）
    if os.path.exists("run_game.bat"):
        if try_command("run_game.bat", "▶ run_game.bat を実行"):
            print("\n🎉 ゲームが正常に起動しました！")
            sys.exit(0)

    # どれもダメならエラーメッセージ
    print("\n❌ すべての起動方法に失敗しました。")
    print("\nトラブルシューティング:")
    print("1. Python がインストールされているか確認してください")
    print("2. 依存関係をインストール: pip install pygame numpy")
    print("3. 管理者として実行してみてください")
    print("4. ウイルス対策ソフトを一時的に無効にしてみてください")
    
    input("\nEnter キーを押して終了...")
    sys.exit(1)

if __name__ == "__main__":
    main()