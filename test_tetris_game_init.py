#!/usr/bin/env python3
"""
TetrisGameの初期化を段階的にテスト
"""

import sys
import time
import traceback
import pygame
from constants import *
from tetris_game import TetrisGame, PlayerMode

def test_tetris_game_creation():
    """TetrisGameの作成を段階的にテスト"""
    print("=== TetrisGame初期化テスト ===")
    
    try:
        # 基本インポート
        print("基本モジュールインポート中...")
        pygame.init()
        print("[OK] pygame初期化")
        print("[OK] constants読み込み")
        print("[OK] TetrisGame読み込み")
        
        # 実際の作成テスト
        print("\nTetrisGame作成テスト...")
        
        modes_to_test = [PlayerMode.HUMAN, PlayerMode.CPU]
        
        for mode in modes_to_test:
            print(f"\nモード {mode} でテスト...")
            
            try:
                start_time = time.time()
                print(f"  作成開始...")
                
                game = TetrisGame(1, mode)
                
                elapsed = time.time() - start_time
                print(f"  [OK] 作成完了 ({elapsed:.3f}秒)")
                
                # 基本プロパティチェック
                print(f"  プレイヤーID: {game.player_id}")
                print(f"  モード: {game.mode}")
                print(f"  ゲームオーバー: {game.game_over}")
                print(f"  スコア: {game.score}")
                
                # ピース生成チェック
                if game.current_piece:
                    print(f"  現在のピース: {game.current_piece.type}")
                else:
                    print(f"  [WARN] 現在のピースなし")
                
                if game.next_piece:
                    print(f"  次のピース: {game.next_piece.type}")
                else:
                    print(f"  [WARN] 次のピースなし")
                
                print(f"  [SUCCESS] モード {mode} 正常作成")
                
            except Exception as e:
                print(f"  [ERROR] モード {mode} 作成失敗: {e}")
                traceback.print_exc()
                return False
        
        print("\n[SUCCESS] 全モードのTetrisGame作成成功")
        return True
        
    except Exception as e:
        print(f"[ERROR] テスト中にエラー: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tetris_game_creation()
    sys.exit(0 if success else 1)