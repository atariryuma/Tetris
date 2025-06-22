#!/usr/bin/env python3
"""
コントローラーボタン配置情報表示
"""

import pygame
from input_manager import UniversalGamepadMapper, Action

def show_controller_mappings():
    """最適化されたコントローラーボタン配置を表示"""
    print("=== 最適化されたコントローラーボタン配置 ===")
    
    mapper = UniversalGamepadMapper()
    
    for controller_type, mapping in mapper.controller_mappings.items():
        print(f"\n【{controller_type.upper()} コントローラー】")
        
        if 'buttons' in mapping:
            print("  ボタン配置:")
            button_names = {
                'xbox': {0: 'A', 1: 'B', 2: 'X', 3: 'Y', 4: 'LB', 5: 'RB'},
                'playstation': {0: 'Square', 1: 'Cross', 2: 'Circle', 3: 'Triangle', 4: 'L1', 5: 'R1', 6: 'L2', 7: 'R2'},
                'switch': {0: 'B', 1: 'A', 2: 'Y', 3: 'X', 4: 'L', 5: 'R', 6: 'ZL', 7: 'ZR'}
            }
            
            names = button_names.get(controller_type, {})
            
            # 主要なゲームボタンのみ表示
            important_actions = [Action.ROTATE_CW, Action.ROTATE_CCW, Action.HARD_DROP, Action.HOLD]
            
            for button_id, action in mapping['buttons'].items():
                if action in important_actions:
                    button_name = names.get(button_id, f"Button{button_id}")
                    action_name = {
                        Action.ROTATE_CW: "右回転",
                        Action.ROTATE_CCW: "左回転", 
                        Action.HARD_DROP: "ハードドロップ",
                        Action.HOLD: "ホールド"
                    }.get(action, action.value)
                    print(f"    {button_name}: {action_name}")
        
        print("  軸操作:")
        print("    左スティック X軸: 左右移動")
        print("    左スティック Y軸: ソフトドロップ")
        print("    D-Pad: メニュー操作")

    print("\n" + "="*50)
    print("🎮 最適化のポイント:")
    print("="*50)
    print("✅ 右回転を最もアクセスしやすい位置に配置")
    print("✅ ハードドロップを複数ボタンに割り当て")
    print("✅ 左右回転を対称的に配置")
    print("✅ ホールドを押しやすい位置に配置")
    print("✅ 現代テトリス（Tetris Effect）スタイル準拠")
    print("="*50)
    
    print("\n参考:")
    print("- この配置はTetris Effect: Connectedなどの")
    print("  現代テトリスゲームで使用される最適配置です")
    print("- 競技プレイヤーの推奨設定を基に調整されています")
    print("- 複数のボタンに同じ機能を割り当て、快適性を向上")

if __name__ == "__main__":
    show_controller_mappings()