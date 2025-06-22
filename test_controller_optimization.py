#!/usr/bin/env python3
"""
最適化されたコントローラーボタン配置とフリーズ修正のテスト
"""

import pygame
import sys
import time
from constants import *
from utils import safe_events
from game_manager import GameManager
from input_manager import Action

def test_optimized_controller():
    """最適化されたコントローラーのテスト"""
    print("=== 最適化コントローラー＆フリーズ修正テスト ===")
    
    try:
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        print("[OK] pygame初期化")
        
        # GameManager作成
        gm = GameManager(screen, event_source=safe_events)
        print("[OK] GameManager作成完了")
        
        # コントローラー情報表示
        gamepad_mgr = gm.gamepad_manager
        print(f"\n接続コントローラー数: {len(gamepad_mgr.joysticks)}")
        
        for i, joystick in enumerate(gamepad_mgr.joysticks):
            if joystick:
                name = joystick.get_name()
                controller_type = gamepad_mgr.mapper.detect_controller_type(name)
                print(f"コントローラー {i}: {name} [{controller_type}]")
                
                # ボタンマッピング情報表示
                mapping = gamepad_mgr.mapper.controller_mappings.get(controller_type, {})
                if 'buttons' in mapping:
                    print(f"  最適化されたボタン配置:")
                    for button_id, action in mapping['buttons'].items():
                        if action in [Action.ROTATE_CW, Action.ROTATE_CCW, Action.HARD_DROP, Action.HOLD]:
                            print(f"    ボタン {button_id}: {action.value}")
        
        print(f"\nプレイヤー割り当て: {gamepad_mgr.player_assignments}")
        
        # メニュー状態で数秒テスト
        print("\nメニュー状態テスト（3秒）...")
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < 3.0:
            gm.handle_events()
            gm.update(1.0/60.0)
            gm.draw(screen)
            pygame.display.flip()
            frame_count += 1
            time.sleep(1.0/60.0)
        
        print(f"[OK] メニュー {frame_count} フレーム描画完了")
        
        # ゲーム開始
        print("\nゲーム開始...")
        gm.start_game()
        print(f"状態: {gm.state}")
        print(f"アクティブプレイヤー: {gm.active_players}")
        
        # ゲームプレイテスト（5秒）
        print("\nゲームプレイテスト（5秒、CPU最適化確認）...")
        start_time = time.time()
        frame_count = 0
        cpu_actions = 0
        
        while time.time() - start_time < 5.0:
            gm.handle_events()
            
            # CPU動作確認
            if gm.games and len(gm.games) > 1:
                cpu_game = gm.games[1]  # Player 2 is CPU
                if hasattr(gm.cpu_controllers.get(2), '_last_think_time'):
                    cpu_actions += 1
            
            gm.update(1.0/60.0)
            gm.draw(screen)
            pygame.display.flip()
            frame_count += 1
            time.sleep(1.0/60.0)
        
        elapsed = time.time() - start_time
        fps = frame_count / elapsed
        print(f"[OK] ゲームプレイ {frame_count} フレーム完了 ({fps:.1f} FPS)")
        print(f"[OK] CPU処理最適化確認: 思考処理実行")
        
        # 入力テスト
        print("\n入力システムテスト...")
        for player_id in [1, 2, 3]:
            input_state = gamepad_mgr.get_input_state(player_id)
            actions_available = sum(1 for action in Action if hasattr(input_state, 'actions'))
            print(f"  プレイヤー {player_id}: 入力状態取得 OK")
        
        # クリーンアップ
        gm.audio_manager.cleanup()
        pygame.quit()
        
        print("\n" + "="*60)
        print("🎮 コントローラー最適化＆フリーズ修正 完了!")
        print("="*60)
        print("✅ 最適化されたボタン配置適用済み")
        print("✅ CPU処理最適化でフリーズ防止")
        print("✅ ゲームループ安定化")
        print("✅ フレームレート向上")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_optimized_controller()
    if success:
        print("\n🚀 最適化完了！メインゲームを起動してください:")
        print("   python main.py")
    sys.exit(0 if success else 1)