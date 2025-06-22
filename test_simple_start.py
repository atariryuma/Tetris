#!/usr/bin/env python3
"""
最小限のstart_gameテスト
"""

import pygame
import sys
import time
from constants import *

def test_simple_start():
    """最小限のstart_gameテスト"""
    print("=== 最小限start_gameテスト ===")
    
    try:
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        print("[OK] pygame初期化")
        
        # GameManagerの必要な部分だけをテスト
        from game_manager import GameManager
        from utils import safe_events
        
        print("GameManager作成...")
        gm = GameManager(screen, event_source=safe_events)
        print("[OK] GameManager作成完了")
        
        print("start_game()呼び出し...")
        start_time = time.time()
        
        # start_gameを直接呼び出し
        gm.start_game()
        
        elapsed = time.time() - start_time
        print(f"[OK] start_game()完了 ({elapsed:.3f}秒)")
        
        print(f"状態: {gm.state}")
        print(f"ゲーム数: {len(gm.games)}")
        print(f"アクティブプレイヤー: {gm.active_players}")
        
        gm.audio_manager.cleanup()
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_start()
    sys.exit(0 if success else 1)