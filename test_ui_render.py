#!/usr/bin/env python3
"""
UI描画処理のテスト
"""

import pygame
import sys
import time
from constants import *
from utils import safe_events
from game_manager import GameManager

def test_ui_rendering():
    """UI描画処理の個別テスト"""
    print("=== UI描画処理テスト ===")
    
    try:
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        print("[OK] pygame初期化")
        
        # GameManager作成（ゲーム開始まで）
        gm = GameManager(screen, event_source=safe_events)
        gm.start_game()
        print("[OK] ゲーム開始完了")
        
        # 各描画処理を個別にテスト
        print("\n各描画処理テスト...")
        
        # 1. 背景描画
        print("1. 背景描画...")
        try:
            start_time = time.time()
            screen.fill(Colors.BG_PRIMARY)
            elapsed = time.time() - start_time
            print(f"   [OK] 背景描画 ({elapsed:.4f}秒)")
        except Exception as e:
            print(f"   [ERROR] 背景描画失敗: {e}")
            return False
        
        # 2. UIRenderer.draw_game_hud
        print("2. draw_game_hud...")
        try:
            start_time = time.time()
            gm.ui_renderer.draw_game_hud(gm.games, gm.active_players)
            elapsed = time.time() - start_time
            print(f"   [OK] draw_game_hud ({elapsed:.4f}秒)")
        except Exception as e:
            print(f"   [ERROR] draw_game_hud失敗: {e}")
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
        
        # 4. 完全な描画処理テスト
        print("\n完全描画処理テスト（5フレーム）...")
        for i in range(5):
            try:
                start_time = time.time()
                
                # gm.draw()を直接使用
                gm.draw(screen)
                pygame.display.flip()
                
                elapsed = time.time() - start_time
                print(f"   フレーム {i+1}: {elapsed:.4f}秒")
                
                if elapsed > 0.1:
                    print(f"   [WARN] フレーム {i+1} が遅い")
                
            except Exception as e:
                print(f"   [ERROR] フレーム {i+1} 失敗: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        print("\n[SUCCESS] UI描画テスト完了")
        
        gm.audio_manager.cleanup()
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"[ERROR] テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ui_rendering()
    sys.exit(0 if success else 1)