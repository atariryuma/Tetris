#!/usr/bin/env python3
"""
簡単なフリーズ修正テスト
"""

import pygame
import sys
import time
from constants import *

def simple_test():
    """簡単なテスト"""
    print("=== 簡単なフリーズ修正テスト ===")
    
    try:
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        print("[OK] pygame初期化")
        
        from game_manager import GameManager
        from utils import safe_events
        
        print("GameManager作成中...")
        gm = GameManager(screen, event_source=safe_events)
        print("[OK] GameManager作成完了")
        
        print("5フレームテスト...")
        for i in range(5):
            print(f"フレーム {i+1}/5")
            gm.handle_events()
            gm.update(1.0/60.0)
            gm.draw(screen)
            pygame.display.flip()
            time.sleep(0.1)
        
        print("[SUCCESS] 5フレーム完了")
        
        gm.audio_manager.cleanup()
        pygame.quit()
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = simple_test()
    print(f"結果: {'成功' if success else '失敗'}")
    sys.exit(0 if success else 1)