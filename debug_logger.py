#!/usr/bin/env python3
"""
詳細デバッグログ機能
Bluetoothコントローラーのクラッシュ原因を特定するためのログシステム
"""

import logging
import time
import sys
import traceback
import pygame
from datetime import datetime
from typing import Optional, Dict, Any
import os

class DebugLogger:
    """デバッグログ管理クラス"""
    
    def __init__(self, log_file: str = "tetris_debug.log"):
        self.log_file = log_file
        self.start_time = time.time()
        
        # ログ設定
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S',
            handlers=[
                logging.FileHandler(log_file, mode='w', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('TetrisDebug')
        
        # セッション開始ログ
        self.logger.info("=" * 60)
        self.logger.info("🎮 Tetris Debug Session Started")
        self.logger.info(f"📁 Log file: {log_file}")
        self.logger.info(f"🕐 Session time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 60)
        
        # システム情報をログ
        self.log_system_info()
    
    def log_system_info(self):
        """システム情報をログ出力"""
        try:
            self.logger.info("📊 System Information:")
            self.logger.info(f"   Python: {sys.version}")
            self.logger.info(f"   Platform: {sys.platform}")
            
            # pygame情報
            try:
                pygame.init()
                pygame.joystick.init()
                self.logger.info(f"   Pygame: {pygame.version.ver}")
                self.logger.info(f"   SDL: {pygame.version.SDL}")
                
                # Joystick情報
                joystick_count = pygame.joystick.get_count()
                self.logger.info(f"   Available joysticks: {joystick_count}")
                
                for i in range(joystick_count):
                    try:
                        joy = pygame.joystick.Joystick(i)
                        joy.init()
                        self.logger.info(f"     Joystick {i}: {joy.get_name()}")
                        self.logger.info(f"       GUID: {joy.get_guid()}")
                        self.logger.info(f"       Buttons: {joy.get_numbuttons()}")
                        self.logger.info(f"       Axes: {joy.get_numaxes()}")
                        self.logger.info(f"       Hats: {joy.get_numhats()}")
                        self.logger.info(f"       Power: {joy.get_power_level()}")
                        joy.quit()
                    except Exception as e:
                        self.logger.error(f"     Joystick {i}: Error - {e}")
                
                pygame.joystick.quit()
                pygame.quit()
                
            except Exception as e:
                self.logger.error(f"   Pygame info error: {e}")
                
        except Exception as e:
            self.logger.error(f"System info logging failed: {e}")
    
    def log_controller_event(self, event_type: str, controller_id: Optional[int] = None, 
                           details: Optional[Dict[str, Any]] = None):
        """コントローラー関連イベントをログ"""
        timestamp = time.time() - self.start_time
        msg = f"🎮 [{timestamp:.3f}s] {event_type}"
        
        if controller_id is not None:
            msg += f" (ID: {controller_id})"
        
        if details:
            for key, value in details.items():
                msg += f" {key}={value}"
        
        self.logger.info(msg)
    
    def log_error(self, error: Exception, context: str = ""):
        """エラーをログ出力"""
        timestamp = time.time() - self.start_time
        self.logger.error(f"❌ [{timestamp:.3f}s] ERROR in {context}: {error}")
        self.logger.error(f"   Exception type: {type(error).__name__}")
        
        # スタックトレースをログ
        tb_lines = traceback.format_exc().split('\n')
        for line in tb_lines:
            if line.strip():
                self.logger.error(f"   {line}")
    
    def log_warning(self, message: str, context: str = ""):
        """警告をログ出力"""
        timestamp = time.time() - self.start_time
        self.logger.warning(f"⚠️  [{timestamp:.3f}s] WARNING in {context}: {message}")
    
    def log_info(self, message: str, context: str = ""):
        """情報をログ出力"""
        timestamp = time.time() - self.start_time
        self.logger.info(f"ℹ️  [{timestamp:.3f}s] {context}: {message}")
    
    def log_debug(self, message: str, context: str = ""):
        """デバッグ情報をログ出力"""
        timestamp = time.time() - self.start_time
        self.logger.debug(f"🔍 [{timestamp:.3f}s] DEBUG {context}: {message}")
    
    def log_frame_info(self, frame_count: int, fps: float, state: str):
        """フレーム情報をログ（定期的に）"""
        if frame_count % 300 == 0:  # 5秒ごと（60FPSの場合）
            timestamp = time.time() - self.start_time
            self.logger.debug(f"🎞️  [{timestamp:.3f}s] Frame {frame_count}, FPS: {fps:.1f}, State: {state}")
    
    def log_pygame_event(self, event):
        """pygameイベントをログ"""
        timestamp = time.time() - self.start_time
        event_name = pygame.event.event_name(event.type)
        
        if event.type in [pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED]:
            self.logger.info(f"🔌 [{timestamp:.3f}s] {event_name}: device_index={getattr(event, 'device_index', 'N/A')}")
        elif event.type in [pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP]:
            self.logger.debug(f"🎮 [{timestamp:.3f}s] {event_name}: joy={event.joy}, button={event.button}")
        elif event.type == pygame.JOYAXISMOTION:
            if abs(event.value) > 0.5:  # 大きな軸の変化のみログ
                self.logger.debug(f"🕹️  [{timestamp:.3f}s] {event_name}: joy={event.joy}, axis={event.axis}, value={event.value:.3f}")
        elif event.type == pygame.QUIT:
            self.logger.info(f"🚪 [{timestamp:.3f}s] {event_name}")
        elif event.type in [pygame.KEYDOWN, pygame.KEYUP]:
            key_name = pygame.key.name(event.key)
            self.logger.debug(f"⌨️  [{timestamp:.3f}s] {event_name}: {key_name}")
    
    def close(self):
        """ログセッション終了"""
        timestamp = time.time() - self.start_time
        self.logger.info("=" * 60)
        self.logger.info(f"🎮 Debug Session Ended ({timestamp:.1f}s total)")
        self.logger.info("=" * 60)
        
        # ログファイルの場所を通知
        if os.path.exists(self.log_file):
            file_size = os.path.getsize(self.log_file)
            print(f"\n📁 Debug log saved: {self.log_file} ({file_size} bytes)")


# グローバルデバッガーインスタンス
debug_logger: Optional[DebugLogger] = None

def init_debug_logger(log_file: str = "tetris_debug.log"):
    """デバッグロガーを初期化"""
    global debug_logger
    debug_logger = DebugLogger(log_file)
    return debug_logger

def get_debug_logger() -> Optional[DebugLogger]:
    """デバッグロガーのインスタンスを取得"""
    return debug_logger

def close_debug_logger():
    """デバッグロガーを終了"""
    global debug_logger
    if debug_logger:
        debug_logger.close()
        debug_logger = None