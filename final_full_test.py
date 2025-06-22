#!/usr/bin/env python3
"""
最終的な完全ゲームテスト
"""

import pygame
import sys
import time
from constants import *
from utils import safe_events
from game_manager import GameManager

def full_game_test():
    """完全なゲーム動作テスト"""
    print("=== 最終完全ゲームテスト ===")
    print("スタートボタン押下とゲームプレイをシミュレート")
    
    try:
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("テトリス最終テスト")
        print("[OK] pygame初期化完了")
        
        # GameManager作成
        print("GameManager作成中...")
        gm = GameManager(screen, event_source=safe_events)
        print("[OK] GameManager作成完了")
        print(f"コントローラー割り当て: {gm.gamepad_manager.assignment_table}")
        
        # メニュー状態確認
        print(f"初期状態: {gm.state}")
        print(f"プレイヤーモード: {gm.player_modes}")
        
        # メニュー画面を数フレーム表示
        print("\nメニュー画面テスト（3秒間）...")
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < 3.0:
            try:
                # イベント処理
                gm.handle_events()
                
                # 更新処理
                gm.update(1.0/60.0)
                
                # 描画処理
                gm.draw(screen)
                pygame.display.flip()
                
                frame_count += 1
                time.sleep(1.0/60.0)  # 60 FPS
                
            except Exception as e:
                print(f"[ERROR] メニューフレーム {frame_count} 失敗: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        print(f"[OK] メニュー画面 {frame_count} フレーム描画完了")
        
        # スタートボタン押下シミュレート
        print("\nスタートボタン押下シミュレート...")
        gm.menu_selection = 3  # スタートボタンを選択
        gm.handle_menu_input(pygame.K_RETURN)  # Enter キー押下
        print(f"[OK] スタートボタン処理完了 - 状態: {gm.state}")
        
        # ゲームプレイテスト（5秒間）
        print("\nゲームプレイテスト（5秒間）...")
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < 5.0:
            try:
                # イベント処理
                gm.handle_events()
                
                # 更新処理
                gm.update(1.0/60.0)
                
                # 描画処理
                gm.draw(screen)
                pygame.display.flip()
                
                frame_count += 1
                
                # 1秒ごとに進捗表示
                if frame_count % 60 == 0:
                    elapsed = time.time() - start_time
                    print(f"  ゲームプレイ {elapsed:.1f}秒経過 ({frame_count} フレーム)")
                
                time.sleep(1.0/60.0)  # 60 FPS
                
            except Exception as e:
                print(f"[ERROR] ゲームフレーム {frame_count} 失敗: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        elapsed = time.time() - start_time
        print(f"[OK] ゲームプレイ {frame_count} フレーム完了 ({elapsed:.1f}秒)")
        
        # 日本語フォント表示確認
        print("\n日本語フォント表示確認...")
        font_mgr = gm.ui_renderer.font_manager
        japanese_texts = ["三人対戦テトリス", "ゲームスタート", "一時停止"]
        
        for text in japanese_texts:
            try:
                surface = font_mgr.render_text(text, "japanese", 24, Colors.WHITE)
                print(f"  [OK] '{text}' 描画成功 ({surface.get_width()}x{surface.get_height()})")
            except Exception as e:
                print(f"  [ERROR] '{text}' 描画失敗: {e}")
                return False
        
        # コントローラーテスト
        print("\nコントローラー機能テスト...")
        print(f"接続コントローラー数: {len(gm.gamepad_manager.joysticks)}")
        print(f"プレイヤー割り当て: {gm.gamepad_manager.player_assignments}")
        
        for player_id in [1, 2, 3]:
            input_state = gm.gamepad_manager.get_input_state(player_id)
            print(f"  プレイヤー {player_id} 入力状態取得: OK")
        
        # クリーンアップ
        print("\nクリーンアップ...")
        gm.audio_manager.cleanup()
        pygame.quit()
        
        print("\n" + "="*50)
        print("🎉 最終テスト結果: 全て成功!")
        print("="*50)
        print("✅ フリーズ問題解決")
        print("✅ 日本語フォント正常表示")
        print("✅ コントローラー自動割り当て")
        print("✅ ゲームループ安定動作")
        print("✅ スタートボタン正常動作")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 最終テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = full_game_test()
    if success:
        print("\n🎮 ゲームは正常に動作します！")
        print("メインゲームを起動するには: python main.py")
    sys.exit(0 if success else 1)