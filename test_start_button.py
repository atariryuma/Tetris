#!/usr/bin/env python3
"""
スタートボタン押下のシミュレーションテスト
"""

import pygame
import sys
import time
import traceback
from constants import *
from utils import safe_events
from game_manager import GameManager

def test_start_button_press():
    """スタートボタン押下をシミュレート"""
    print("=== スタートボタン押下テスト ===")
    
    try:
        # pygame初期化
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        print("[OK] pygame初期化完了")
        
        # GameManager作成
        print("GameManager作成中...")
        gm = GameManager(screen, event_source=safe_events)
        print("[OK] GameManager作成完了")
        
        # 初期状態確認
        print(f"初期状態: {gm.state}")
        print(f"メニュー選択: {gm.menu_selection}")
        print(f"プレイヤーモード: {gm.player_modes}")
        
        # メニューでスタートボタンを選択（menu_selection = 3）
        print("\nスタートボタンを選択...")
        gm.menu_selection = 3
        print(f"メニュー選択: {gm.menu_selection}")
        
        # キーボード入力をシミュレート（Enterキー押下）
        print("Enterキー押下をシミュレート...")
        
        # Enterキーイベントを作成
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        
        print("handle_menu_input呼び出し...")
        try:
            # メニュー入力処理を直接呼び出し
            gm.handle_menu_input(pygame.K_RETURN)
            print("[OK] handle_menu_input完了")
        except Exception as e:
            print(f"[ERROR] handle_menu_input失敗: {e}")
            traceback.print_exc()
            return False
        
        # 状態確認
        print(f"処理後の状態: {gm.state}")
        print(f"ゲーム数: {len(gm.games)}")
        print(f"アクティブプレイヤー: {gm.active_players}")
        
        # 少し更新してみる
        print("\nゲーム更新テスト...")
        for i in range(10):
            print(f"フレーム {i+1}/10", end="\r")
            try:
                gm.update(1.0/60.0)
                gm.draw(screen)
                pygame.display.flip()
                time.sleep(0.01)  # 10ms待機
            except Exception as e:
                print(f"\n[ERROR] フレーム {i+1} で失敗: {e}")
                traceback.print_exc()
                return False
        
        print(f"\n[OK] 10フレーム更新完了")
        
        # クリーンアップ
        gm.audio_manager.cleanup()
        pygame.quit()
        
        print("[SUCCESS] スタートボタンテスト完了")
        return True
        
    except Exception as e:
        print(f"[ERROR] テスト中にエラー: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_start_button_press()
    sys.exit(0 if success else 1)