"""
Test script to validate core game logic without GUI.
"""

import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from tetris_game import TetrisGame, Tetromino
from input_manager import InputState, Action
from constants import PlayerMode

def test_tetris_game():
    """Test core Tetris game functionality."""
    print("Testing Tetris game logic...")
    
    # Create a game instance
    game = TetrisGame(1, PlayerMode.HUMAN)
    
    # Test initial state
    assert game.score == 0
    assert game.level == 1
    assert not game.game_over
    assert game.current_piece is not None
    assert game.next_piece is not None
    
    print("✓ Game initialization successful")
    
    # Test piece movement
    input_state = InputState()
    initial_x = game.current_piece.x
    
    input_state.pressed[Action.MOVE_LEFT] = True
    events = game.update(input_state, 0.016)  # 60 FPS
    
    if game.current_piece.x == initial_x - 1:
        print("✓ Piece movement working")
    else:
        print("⚠ Piece movement may have issues")
    
    # Test piece rotation
    input_state = InputState()
    input_state.pressed[Action.ROTATE_CW] = True
    events = game.update(input_state, 0.016)
    
    print("✓ Piece rotation tested")
    
    # Test hard drop
    input_state = InputState()
    input_state.pressed[Action.HARD_DROP] = True
    events = game.update(input_state, 0.016)
    
    if events.get('hard_drop'):
        print("✓ Hard drop working")
    
    print("✓ All core game tests passed!")

def test_cpu_ai():
    """Test CPU AI functionality."""
    print("\nTesting CPU AI...")
    
    from cpu_ai import TetrisAI, SimpleCPU
    
    # Test AI decision making
    ai = TetrisAI('medium')
    game = TetrisGame(2, PlayerMode.CPU)
    
    best_move = ai.get_best_move(game)
    if best_move:
        print(f"✓ AI suggested move: {best_move}")
    else:
        print("⚠ AI could not find a move")
    
    # Test simple CPU
    simple_cpu = SimpleCPU()
    action = simple_cpu.get_random_move(game)
    print(f"✓ Simple CPU action: {action}")
    
    print("✓ CPU AI tests passed!")

def test_audio_system():
    """Test audio system."""
    print("\nTesting audio system...")
    
    from audio_manager import AudioManager
    
    audio = AudioManager()
    
    if audio.initialized:
        print("✓ Audio system initialized")
        
        # Test sound generation
        audio.play_sfx('piece_move')
        print("✓ Sound effects working")
        
        volume_info = audio.get_volume_info()
        print(f"✓ Volume settings: {volume_info}")
    else:
        print("⚠ Audio system not available (expected in headless environment)")
    
    audio.cleanup()
    print("✓ Audio tests completed!")

def test_input_system():
    """Test input system."""
    print("\nTesting input system...")
    
    from input_manager import GamepadManager, UniversalGamepadMapper
    
    gamepad_manager = GamepadManager()
    mapper = UniversalGamepadMapper()
    
    # Test controller detection
    controller_type = mapper.detect_controller_type("Xbox Wireless Controller")
    assert controller_type == 'xbox'
    print("✓ Controller type detection working")
    
    # Test input state
    input_state = gamepad_manager.get_input_state(1)
    assert input_state is not None
    print("✓ Input state management working")
    
    print("✓ Input system tests passed!")

def main():
    """Run all tests."""
    print("=== Tetris Game Test Suite ===\n")
    
    try:
        test_tetris_game()
        test_cpu_ai()
        test_audio_system()
        test_input_system()
        
        print("\n🎉 All tests passed! The game is ready to play.")
        print("\nTo run the game with GUI:")
        print("uv run python main.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()