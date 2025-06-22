#!/usr/bin/env python3
"""
デバッグ用：スタートボタン押下時のフリーズ原因を特定
"""

import pygame
import sys
import time
import traceback
from constants import *
from utils import safe_events

def debug_game_start():
    """ゲーム開始時の詳細なデバッグ"""
    print("=== ゲーム開始デバッグ ===")
    
    try:
        # pygame初期化
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("デバッグモード")
        print("[OK] pygame初期化完了")
        
        # GameManager作成
        print("GameManager作成中...")
        from game_manager import GameManager
        gm = GameManager(screen, event_source=safe_events)
        print("[OK] GameManager作成完了")
        
        # 各システムの動作確認
        print("各システムの動作確認...")
        
        # 1. 初期状態確認
        print(f"初期状態: {gm.state}")
        print(f"プレイヤーモード: {gm.player_modes}")
        
        # 2. start_game()メソッドを段階的にテスト
        print("\nstart_game()メソッドのテスト開始...")
        
        # プレイヤー数チェック
        active_count = sum(1 for mode in gm.player_modes if mode != PlayerMode.OFF)
        print(f"アクティブプレイヤー数: {active_count}")
        
        if active_count == 0:
            print("[ERROR] アクティブプレイヤーが0人です")
            return False
        
        # ゲーム配列初期化
        print("ゲーム配列初期化中...")
        gm.games = []
        gm.active_players = []
        gm.cpu_controllers = {}
        print("[OK] 配列初期化完了")
        
        # 各プレイヤーのゲーム作成
        print("プレイヤーゲーム作成中...")
        for i, mode in enumerate(gm.player_modes):
            player_id = i + 1
            print(f"プレイヤー {player_id} (モード: {mode}) 作成中...")
            
            try:
                # TetrisGame作成前のチェック
                print(f"  TetrisGame作成前...")
                from tetris_game import TetrisGame
                print(f"  TetrisGameクラス読み込み完了")
                
                # 実際に作成
                start_time = time.time()
                game = TetrisGame(player_id, mode)
                elapsed = time.time() - start_time
                print(f"  TetrisGame作成完了 ({elapsed:.3f}秒)")
                
                gm.games.append(game)
                
                if mode != PlayerMode.OFF:
                    gm.active_players.append(player_id)
                    print(f"  プレイヤー {player_id} をアクティブリストに追加")
                
                if mode == PlayerMode.CPU:
                    print(f"  CPU作成中...")
                    from cpu_ai import AdaptiveCPU
                    cpu_start = time.time()
                    gm.cpu_controllers[player_id] = AdaptiveCPU('medium')
                    cpu_elapsed = time.time() - cpu_start
                    print(f"  CPU作成完了 ({cpu_elapsed:.3f}秒)")
                    
            except Exception as e:
                print(f"[ERROR] プレイヤー {player_id} 作成失敗: {e}")
                traceback.print_exc()
                return False
        
        # 状態変更
        print("ゲーム状態をPLAYINGに変更...")
        gm.state = GameState.PLAYING
        print("[OK] 状態変更完了")
        
        # BGM開始
        print("BGM開始...")
        try:
            gm.audio_manager.stop_bgm()
            gm.audio_manager.play_bgm('game_music')
            print("[OK] BGM処理完了")
        except Exception as e:
            print(f"[WARN] BGM処理エラー: {e}")
        
        print(f"アクティブプレイヤー: {gm.active_players}")
        
        # 簡単なゲームループテスト
        print("\n簡単なゲームループテスト...")
        test_frames = 60  # 1秒分
        start_time = time.time()
        
        for frame in range(test_frames):
            print(f"\rフレーム {frame+1}/{test_frames}", end="")
            
            # update処理
            gm.update(1.0/60.0)
            
            # draw処理
            gm.draw(screen)
            pygame.display.flip()
            
            # 少し待機
            time.sleep(1.0/60.0)
        
        elapsed = time.time() - start_time
        print(f"\n[OK] {test_frames}フレーム完了 ({elapsed:.2f}秒)")
        
        # クリーンアップ
        gm.audio_manager.cleanup()
        pygame.quit()
        
        print("[SUCCESS] ゲーム開始デバッグ完了")
        return True
        
    except Exception as e:
        print(f"[ERROR] デバッグ中にエラー: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_game_start()
    sys.exit(0 if success else 1)