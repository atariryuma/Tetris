#!/usr/bin/env python3
"""
短時間の最終テスト
"""

import pygame
import sys
import time
from constants import *
from utils import safe_events
from game_manager import GameManager

def quick_test():
    """短時間の最終テスト"""
    print("=== 短時間最終テスト ===")
    
    try:
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        print("[OK] pygame初期化")
        
        # GameManager作成
        gm = GameManager(screen, event_source=safe_events)
        print("[OK] GameManager作成")
        
        # スタートボタン押下
        print("スタートボタン押下...")
        gm.menu_selection = 3
        gm.handle_menu_input(pygame.K_RETURN)
        print(f"[OK] ゲーム開始 - 状態: {gm.state}")
        
        # 短時間テスト（10フレーム）
        print("10フレームテスト...")
        for i in range(10):
            start_frame = time.time()
            
            gm.handle_events()
            gm.update(1.0/60.0)
            gm.draw(screen)
            pygame.display.flip()
            
            frame_time = time.time() - start_frame
            print(f"  フレーム {i+1}: {frame_time:.4f}秒")
            
            if frame_time > 0.1:
                print(f"  [WARN] フレーム {i+1} が遅い")
        
        print("[OK] 10フレーム完了")
        
        # 日本語フォントテスト
        print("日本語フォントテスト...")
        font_mgr = gm.ui_renderer.font_manager
        surface = font_mgr.render_text("三人対戦テトリス", "japanese", 24, Colors.WHITE)
        print(f"[OK] 日本語描画 ({surface.get_width()}x{surface.get_height()})")
        
        gm.audio_manager.cleanup()
        pygame.quit()
        
        print("\n[SUCCESS] 短時間テスト完了")
        return True
        
    except Exception as e:
        print(f"[ERROR] テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)