#!/usr/bin/env python3
"""
フォント読み込みテスト
"""

import pygame
import sys
import os

def test_font_loading():
    """フォント読み込みをテスト"""
    print("=== フォント読み込みテスト ===")
    
    try:
        pygame.init()
        print("[OK] pygame初期化")
        
        # フォントファイル存在確認
        font_dir = os.path.join(os.path.dirname(__file__), 'assets', 'fonts')
        noto_path = os.path.join(font_dir, 'NotoSansJP-Regular.ttf')
        
        print(f"フォントディレクトリ: {font_dir}")
        print(f"NotoSansJPパス: {noto_path}")
        print(f"ファイル存在: {os.path.exists(noto_path)}")
        
        if os.path.exists(noto_path):
            file_size = os.path.getsize(noto_path)
            print(f"ファイルサイズ: {file_size} bytes")
        
        # FontManager テスト
        print("\nFontManager作成...")
        from font_manager import get_font_manager
        
        font_mgr = get_font_manager()
        print("[OK] FontManager作成完了")
        
        # 日本語テキスト描画テスト
        print("\n日本語テキスト描画テスト...")
        japanese_texts = [
            "三人対戦テトリス",
            "ゲームスタート", 
            "参加する",
            "参加しない",
            "一時停止"
        ]
        
        for text in japanese_texts:
            try:
                print(f"  テスト: '{text}'")
                surface = font_mgr.render_text(text, "japanese", 24, (255, 255, 255))
                print(f"    [OK] 描画完了 ({surface.get_width()}x{surface.get_height()})")
            except Exception as e:
                print(f"    [ERROR] 描画失敗: {e}")
                return False
        
        # 英語テキストテスト
        print("\n英語テキストテスト...")
        english_texts = [
            "TETRIS",
            "PLAYER 1",
            "SCORE",
            "LINES"
        ]
        
        for text in english_texts:
            try:
                print(f"  テスト: '{text}'")
                surface = font_mgr.render_text(text, "ui", 24, (255, 255, 255))
                print(f"    [OK] 描画完了 ({surface.get_width()}x{surface.get_height()})")
            except Exception as e:
                print(f"    [ERROR] 描画失敗: {e}")
                return False
        
        print("\n[SUCCESS] 全フォントテスト完了")
        return True
        
    except Exception as e:
        print(f"[ERROR] テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        pygame.quit()

if __name__ == "__main__":
    success = test_font_loading()
    sys.exit(0 if success else 1)