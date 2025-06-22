#!/usr/bin/env python3
"""
ゲーム開始後の更新処理テスト
"""

import pygame
import sys
import time
from constants import *
from utils import safe_events
from game_manager import GameManager

def test_game_update():
    """ゲーム開始後の更新処理をテスト"""
    print("=== ゲーム更新処理テスト ===")
    
    try:
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        print("[OK] pygame初期化")
        
        # GameManager作成
        gm = GameManager(screen, event_source=safe_events)
        print("[OK] GameManager作成")
        
        # ゲーム開始
        gm.start_game()
        print("[OK] ゲーム開始")
        print(f"状態: {gm.state}")
        print(f"アクティブプレイヤー: {gm.active_players}")
        
        # 各処理を個別にテスト
        print("\n各処理を個別にテスト...")
        
        # 1. Update処理
        print("1. Update処理テスト...")
        try:
            start_time = time.time()
            gm.update(1.0/60.0)
            elapsed = time.time() - start_time
            print(f"   [OK] Update処理 ({elapsed:.4f}秒)")
        except Exception as e:
            print(f"   [ERROR] Update処理失敗: {e}")
            return False
        
        # 2. Draw処理
        print("2. Draw処理テスト...")
        try:
            start_time = time.time()
            gm.draw(screen)
            elapsed = time.time() - start_time
            print(f"   [OK] Draw処理 ({elapsed:.4f}秒)")
        except Exception as e:
            print(f"   [ERROR] Draw処理失敗: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 3. Display flip
        print("3. Display flip...")
        try:
            start_time = time.time()
            pygame.display.flip()
            elapsed = time.time() - start_time
            print(f"   [OK] Display flip ({elapsed:.4f}秒)")
        except Exception as e:
            print(f"   [ERROR] Display flip失敗: {e}")
            return False
        
        # 連続更新テスト
        print("\n連続更新テスト（10フレーム）...")
        for i in range(10):
            try:
                start_time = time.time()
                
                gm.update(1.0/60.0)
                gm.draw(screen)
                pygame.display.flip()
                
                elapsed = time.time() - start_time
                print(f"   フレーム {i+1}: {elapsed:.4f}秒")
                
                if elapsed > 0.1:  # 100ms以上かかったら警告
                    print(f"   [WARN] フレーム {i+1} が遅い ({elapsed:.4f}秒)")
                
            except Exception as e:
                print(f"   [ERROR] フレーム {i+1} 失敗: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        print("[SUCCESS] 全フレーム処理完了")
        
        gm.audio_manager.cleanup()
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"[ERROR] テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_game_update()
    sys.exit(0 if success else 1)