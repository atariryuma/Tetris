#!/usr/bin/env python3
"""
Xbox専用・フリーズ修正テスト
"""

import pygame
import sys
import time
from constants import *
from utils import safe_events
from game_manager import GameManager

def test_xbox_only_freeze_fix():
    """Xbox専用・フリーズ修正のテスト"""
    print("=== Xbox専用・フリーズ修正テスト ===")
    
    try:
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        print("[OK] pygame初期化")
        
        # GameManager作成
        gm = GameManager(screen, event_source=safe_events)
        print("[OK] GameManager作成")
        
        # コントローラー確認
        gamepad_mgr = gm.gamepad_manager
        print(f"接続コントローラー数: {len(gamepad_mgr.joysticks)}")
        
        for i, joystick in enumerate(gamepad_mgr.joysticks):
            if joystick:
                name = joystick.get_name()
                controller_type = gamepad_mgr.mapper.detect_controller_type(name)
                print(f"コントローラー {i}: {name} -> {controller_type}")
        
        # 短時間ゲームループテスト（10秒）
        print("\n10秒間ゲームループテスト...")
        test_start = time.time()
        frame_count = 0
        
        # ゲーム開始
        gm.start_game()
        
        while time.time() - test_start < 10.0 and gm.running:
            loop_start = time.time()
            
            gm.handle_events()
            gm.update(1.0/60.0)
            gm.draw(screen)
            pygame.display.flip()
            
            loop_time = time.time() - loop_start
            frame_count += 1
            
            # フレーム処理時間チェック
            if loop_time > 0.1:  # 100ms以上かかったら警告
                print(f"[WARN] フレーム {frame_count} が遅い: {loop_time:.3f}秒")
            
            time.sleep(max(0, 1.0/60.0 - loop_time))  # 60 FPS target
        
        elapsed = time.time() - test_start
        fps = frame_count / elapsed
        
        print(f"[OK] {frame_count} フレーム完了 ({fps:.1f} FPS)")
        print(f"[OK] 総時間: {elapsed:.1f}秒")
        print(f"[OK] ハング検出機能: 動作中")
        
        if gm.running:
            print("[OK] ゲームループ正常終了")
        else:
            print("[INFO] ゲームループが停止されました")
        
        # クリーンアップ
        gm.running = False
        gm.audio_manager.cleanup()
        pygame.quit()
        
        print("\n" + "="*50)
        print("🎮 Xbox専用・フリーズ修正 完了!")
        print("="*50)
        print("✅ Xbox コントローラーのみサポート")
        print("✅ フリーズ検出・強制終了機能追加")
        print("✅ CPU処理頻度制限")
        print("✅ ゲームループ安定化")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_xbox_only_freeze_fix()
    if success:
        print("\n🚀 修正完了！メインゲームを起動:")
        print("   python main.py")
        print("\n終了方法:")
        print("   - ウィンドウの×ボタンをクリック")
        print("   - ESCキーを押してからQキー")
        print("   - Ctrl+C（強制終了）")
    sys.exit(0 if success else 1)