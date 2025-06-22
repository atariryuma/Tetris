#!/usr/bin/env python3
"""
Bluetoothコントローラー接続デバッグテスト
クラッシュの原因を特定するための詳細ログ付きテスト
"""

import pygame
import sys
import time
from debug_logger import init_debug_logger, close_debug_logger

def test_bluetooth_controller_debug():
    """Bluetoothコントローラーのデバッグテスト"""
    print("🔍 Bluetoothコントローラー・デバッグテスト開始")
    print("=" * 60)
    
    # デバッグロガー初期化
    debug = init_debug_logger("bluetooth_debug.log")
    debug.log_info("Bluetooth controller debug test started", "test_main")
    
    try:
        # Pygame初期化
        debug.log_info("Initializing pygame", "test_main")
        pygame.init()
        
        debug.log_info("Initializing joystick subsystem", "test_main")
        pygame.joystick.init()
        
        # 初期コントローラー状態
        controller_count = pygame.joystick.get_count()
        debug.log_info(f"Initial controller count: {controller_count}", "test_main")
        print(f"接続されているコントローラー数: {controller_count}")
        
        if controller_count == 0:
            print("\n⚠️  コントローラーが接続されていません")
            print("   1. Bluetoothコントローラーをペアリングして接続してください")
            print("   2. 接続後、再度このテストを実行してください")
            return False
        
        # 各コントローラーの詳細情報取得
        controllers = {}
        for i in range(controller_count):
            try:
                debug.log_info(f"Initializing controller {i}", "controller_init")
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                
                # コントローラー情報収集
                info = {
                    'name': joystick.get_name(),
                    'guid': joystick.get_guid(),
                    'buttons': joystick.get_numbuttons(),
                    'axes': joystick.get_numaxes(),
                    'hats': joystick.get_numhats(),
                    'power': joystick.get_power_level()
                }
                
                controllers[i] = {'joystick': joystick, 'info': info}
                
                debug.log_controller_event("BLUETOOTH_CONTROLLER_INIT", i, info)
                
                print(f"\nコントローラー {i}:")
                print(f"  名前: {info['name']}")
                print(f"  GUID: {info['guid']}")
                print(f"  ボタン数: {info['buttons']}")
                print(f"  軸数: {info['axes']}")
                print(f"  ハット数: {info['hats']}")
                print(f"  バッテリー: {info['power']}")
                
            except Exception as e:
                debug.log_error(e, f"controller_{i}_init")
                print(f"❌ コントローラー {i} の初期化に失敗: {e}")
                continue
        
        if not controllers:
            debug.log_warning("No controllers successfully initialized", "test_main")
            print("❌ 全てのコントローラーの初期化に失敗しました")
            return False
        
        # Bluetooth特有の問題をテスト
        print(f"\n🔍 {len(controllers)}個のコントローラーで詳細テスト開始...")
        debug.log_info(f"Starting detailed test with {len(controllers)} controllers", "test_main")
        
        # テスト1: 基本的な状態読み取り
        print("\n📋 テスト1: 基本状態読み取り")
        for controller_id, controller_data in controllers.items():
            joystick = controller_data['joystick']
            try:
                debug.log_debug(f"Testing basic state reading for controller {controller_id}", "test1")
                
                # ボタン状態読み取り
                for button_id in range(joystick.get_numbuttons()):
                    pressed = joystick.get_button(button_id)
                    if pressed:
                        debug.log_debug(f"Button {button_id} pressed", f"controller_{controller_id}")
                
                # 軸状態読み取り
                for axis_id in range(joystick.get_numaxes()):
                    value = joystick.get_axis(axis_id)
                    if abs(value) > 0.1:  # 小さな変化は無視
                        debug.log_debug(f"Axis {axis_id} value: {value:.3f}", f"controller_{controller_id}")
                
                print(f"  ✅ コントローラー {controller_id}: 基本読み取り成功")
                
            except Exception as e:
                debug.log_error(e, f"test1_controller_{controller_id}")
                print(f"  ❌ コントローラー {controller_id}: 基本読み取り失敗 - {e}")
        
        # テスト2: 継続的な入力監視（10秒間）
        print(f"\n🕐 テスト2: 10秒間の継続監視")
        debug.log_info("Starting 10-second continuous monitoring", "test2")
        
        start_time = time.time()
        event_count = 0
        error_count = 0
        
        print("   コントローラーのボタンや軸を動かしてください...")
        
        while time.time() - start_time < 10.0:
            try:
                # イベント処理
                for event in pygame.event.get():
                    event_count += 1
                    debug.log_pygame_event(event)
                    
                    if event.type == pygame.JOYDEVICEADDED:
                        debug.log_info(f"Controller hot-plugged: {event.device_index}", "test2")
                        print(f"    🔌 コントローラー {event.device_index} が接続されました")
                    
                    elif event.type == pygame.JOYDEVICEREMOVED:
                        debug.log_info(f"Controller disconnected: {event.device_index}", "test2")
                        print(f"    🔌 コントローラー {event.device_index} が切断されました")
                    
                    elif event.type == pygame.JOYBUTTONDOWN:
                        debug.log_info(f"Button pressed: joy={event.joy}, button={event.button}", "test2")
                        print(f"    🎮 ボタン {event.button} 押下 (コントローラー {event.joy})")
                    
                    elif event.type == pygame.JOYAXISMOTION:
                        if abs(event.value) > 0.5:
                            debug.log_info(f"Axis moved: joy={event.joy}, axis={event.axis}, value={event.value:.3f}", "test2")
                            print(f"    🕹️  軸 {event.axis} 移動: {event.value:.3f} (コントローラー {event.joy})")
                
                # 安全な状態ポーリング
                for controller_id, controller_data in controllers.items():
                    joystick = controller_data['joystick']
                    try:
                        # 電力レベルチェック（Bluetooth特有）
                        power = joystick.get_power_level()
                        if power != controller_data['info']['power']:
                            debug.log_info(f"Power level changed: {controller_data['info']['power']} -> {power}", 
                                         f"controller_{controller_id}")
                            controller_data['info']['power'] = power
                    except Exception as e:
                        error_count += 1
                        debug.log_warning(f"State polling error: {e}", f"controller_{controller_id}")
                
                time.sleep(0.016)  # ~60 FPS
                
            except Exception as e:
                error_count += 1
                debug.log_error(e, "test2_main_loop")
                print(f"    ❌ ループエラー: {e}")
                
                # 致命的エラーの場合は停止
                if error_count > 10:
                    debug.log_warning("Too many errors, stopping test", "test2")
                    print("    🛑 エラーが多すぎます。テストを停止します。")
                    break
        
        elapsed = time.time() - start_time
        debug.log_info(f"Monitoring completed: {elapsed:.1f}s, {event_count} events, {error_count} errors", "test2")
        print(f"  ✅ 監視完了: {elapsed:.1f}秒, {event_count}イベント, {error_count}エラー")
        
        # テスト3: クリーンアップテスト
        print(f"\n🧹 テスト3: クリーンアップテスト")
        debug.log_info("Starting cleanup test", "test3")
        
        for controller_id, controller_data in controllers.items():
            joystick = controller_data['joystick']
            try:
                debug.log_debug(f"Quitting controller {controller_id}", "test3")
                joystick.quit()
                print(f"  ✅ コントローラー {controller_id}: クリーンアップ成功")
            except Exception as e:
                debug.log_error(e, f"test3_controller_{controller_id}")
                print(f"  ❌ コントローラー {controller_id}: クリーンアップ失敗 - {e}")
        
        pygame.joystick.quit()
        pygame.quit()
        
        debug.log_info("Bluetooth controller test completed successfully", "test_main")
        
        print("\n" + "=" * 60)
        print("✅ Bluetoothコントローラーテスト完了!")
        print("=" * 60)
        
        if error_count == 0:
            print("🎉 エラーなし - Bluetoothコントローラーは正常に動作しています")
        else:
            print(f"⚠️  {error_count}個のエラーが発生しました - ログを確認してください")
        
        return error_count == 0
        
    except Exception as e:
        debug.log_error(e, "test_main_exception")
        print(f"\n❌ テスト中に致命的エラー: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        close_debug_logger()


if __name__ == "__main__":
    print("🔍 Bluetoothコントローラー・デバッグテスト")
    print("\n注意事項:")
    print("1. Bluetoothコントローラーを事前にペアリング・接続してください")
    print("2. テスト中はコントローラーのボタンや軸を動かしてください")
    print("3. エラーが発生した場合は bluetooth_debug.log を確認してください")
    print("\n開始しますか? (Enter キーを押してください)")
    input()
    
    success = test_bluetooth_controller_debug()
    
    if success:
        print("\n🚀 テスト成功！メインゲームを安全に起動できます:")
        print("   uv run python main.py")
    else:
        print("\n📁 詳細なログを確認してください:")
        print("   bluetooth_debug.log")
    
    sys.exit(0 if success else 1)