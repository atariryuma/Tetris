#!/usr/bin/env python3
"""
main.pyの段階的デバッグ
"""

import sys
import os
import pygame
import traceback
import time

def debug_main_step_by_step():
    """main.pyを段階的に実行してハング箇所を特定"""
    print("=== main.py段階的デバッグ ===")
    
    try:
        print("ステップ1: 基本インポート...")
        from constants import WINDOW_WIDTH, WINDOW_HEIGHT, VSYNC
        print("[OK] constants インポート")
        
        from utils import safe_events
        print("[OK] utils インポート")
        
        print("ステップ2: pygame初期化...")
        if not pygame.get_init():
            pygame.init()
        print("[OK] pygame初期化")
        
        print("ステップ3: ディスプレイ作成...")
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("デバッグモード")
        print("[OK] ディスプレイ作成")
        
        print("ステップ4: GameManagerインポート...")
        from game_manager import GameManager
        print("[OK] GameManager インポート")
        
        print("ステップ5: GameManager作成...")
        start_time = time.time()
        gm = GameManager(screen, event_source=safe_events)
        elapsed = time.time() - start_time
        print(f"[OK] GameManager作成完了 ({elapsed:.3f}秒)")
        
        print("ステップ6: 基本機能テスト...")
        gm.update(1.0/60.0)
        print("[OK] update()動作")
        
        gm.draw(screen)
        print("[OK] draw()動作")
        
        pygame.display.flip()
        print("[OK] display.flip()動作")
        
        print("ステップ7: 簡単なループテスト（3秒）...")
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < 3.0:
            gm.handle_events()
            gm.update(1.0/60.0)
            gm.draw(screen)
            pygame.display.flip()
            frame_count += 1
            time.sleep(1.0/60.0)
        
        elapsed = time.time() - start_time
        fps = frame_count / elapsed
        print(f"[OK] 3秒ループテスト完了 ({frame_count}フレーム, {fps:.1f}FPS)")
        
        print("ステップ8: クリーンアップ...")
        gm.audio_manager.cleanup()
        pygame.quit()
        print("[OK] クリーンアップ完了")
        
        print("\n[SUCCESS] 全ステップ完了 - main.pyは正常動作可能")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] エラー発生: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_main_step_by_step()
    print(f"\nデバッグ結果: {'成功' if success else '失敗'}")
    sys.exit(0 if success else 1)