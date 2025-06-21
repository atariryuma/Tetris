# CLAUDE\_PYTHON.md

This file provides guidance to **Claude Code** (claude.ai/code) when working with *Python* code in this repository.

---

## 1. Project Overview

This project is a **multiplayer Tetris game** written in **pure Python** using the [**pygame**](https://www.pygame.org/) library.  Up to **three simultaneous players** are supported, each of whom can be set to **Human**, **CPU**, or **OFF**.  A key feature is **universal game‑controller support** that works with Xbox, PlayStation, Nintendo Switch Pro, and other standard gamepads.

---

## 2. Development Commands

> The game is 100 % client‑side and has **no external server**.  A lightweight *virtualenv + pygame* setup is all that is required.

```bash
# 1. Create and activate a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install runtime dependencies (currently just pygame)
pip install -r requirements.txt  # or: pip install pygame

# 3. Run the game
python main.py
```

### Quick Run (no venv)

If you already have pygame installed system‑wide:

```bash
python main.py
```

### Hot‑Reload for Development

Adding the [`watchdog`](https://pypi.org/project/watchdog/) package enables automatic reload on file save:

```bash
pip install watchdog
python dev_server.py  # Lightweight file‑watcher that restarts main.py
```

---

## 3. Code Architecture

### 3.1 Core File Structure

| File           | Purpose                                                                                              |
| -------------- | ---------------------------------------------------------------------------------------------------- |
| `main.py`      | Program entry point; initialises pygame, creates `GameManager`, and starts the main loop             |
| `tetris.py`    | Full Tetris rules implementation *(piece spawning, rotation, gravity, line clearing, scoring, etc.)* |
| `input.py`     | Game‑controller abstraction layer (universal mapping + keyboard fallback)                            |
| `cpu.py`       | Simple AI for CPU players (depth‑1 look‑ahead with heuristic scoring)                                |
| `ui.py`        | Menu, pause screen, and HUD rendering with gamepad navigation                                        |
| `constants.py` | Centralised tweakable constants (board size, colours, input intervals, …)                            |
| `assets/`      | Fonts, sounds, and art (all loaded via `pygame.image` / `pygame.mixer`)                              |

> *There is **no** build pipeline; just edit & run.*

### 3.2 Key System Components

#### 3.2.1 **Gamepad Management System** (`input.py`)

* **`UniversalGamepadMapper`** – Translates raw pygame joystick IDs into a canonical button/axis layout (works across Xbox, DualShock/DualSense, Switch Pro, and generic controllers).
* **`GamepadManager`** – Detects hot‑plug events, assigns controllers to players, and exposes a `get_state(player_idx)` call that returns a debounced input state.
* **`UINavigationManager`** – Provides menu navigation via D‑Pad / left‑stick and face buttons; falls back to arrow keys + Enter/Escape on keyboard.

#### 3.2.2 **Game Architecture** (`tetris.py`)

* **`Tetris` class** – Represents one player’s board:

  * Maintains grid state, active piece, next/hold queues
  * Consumes `InputState` for human players
  * Calls `CPUStrategy` for CPUs (see `cpu.py`)
  * Implements SRS rotation, wall‑kicks, ghost piece, hard/soft drop, and scoring

#### 3.2.3 **Multiplayer Features**

* **Attack System** – Clearing *⩾ 2* lines inserts “garbage” rows into opponents’ boards with adjustable delay animation.
* **Player Modes** – Each of the three playfields can be toggled between *Human*, *CPU*, or *OFF* in the pre‑game menu.
* **Synchronised Loop** – A single `GameManager` tick updates all live players every frame (\~60 FPS) to keep boards in lock‑step.

---

## 4. Gamepad Integration Details

1. **Automatic Detection** – On program start (and whenever a `JOYDEVICEADDED` event fires), the connected controllers are enumerated via `pygame.joystick`.
2. **Universal Mapping** – `UniversalGamepadMapper` normalises axis & button indices so the rest of the game can remain platform‑agnostic.
3. **Debounce & Repeat‑Rate** – The mapper enforces an `INPUT_INTERVAL` (default **180 ms**) to prevent rapid unintended repeats.
4. **Analog Stick Dead‑Zone** – Default dead‑zone is **0.30**; values below are treated as *0*.
5. **Debugging Tools**

   * Print assignments: `print(gamepad_manager.assignment_table())`
   * Force re‑scan: `gamepad_manager.refresh()`
   * Live button chart overlays on screen when `DEBUG_CONTROLLERS = True` in `constants.py`.

---

## 5. Game States

| State       | Description                        | Input Handling                             |
| ----------- | ---------------------------------- | ------------------------------------------ |
| `MENU`      | Pre‑game player configuration      | UI navigation via `UINavigationManager`    |
| `PLAYING`   | Active gameplay                    | `Tetris` consumes player inputs each frame |
| `PAUSED`    | Game paused                        | Resume / quit controls only                |
| `GAME_OVER` | All but one player have topped out | Winner banner + restart prompt             |

State transitions are coordinated by `GameManager.set_state()`.

---

## 6. Key Constants (see `constants.py`)

```python
BLOCK_SIZE        = 32        # px
BOARD_WIDTH       = 10        # blocks
BOARD_HEIGHT      = 20        # blocks
INPUT_INTERVAL_MS = 180       # minimum ms between repeat inputs
ANALOG_DEAD_ZONE  = 0.30      # joystick neutral threshold
CPU_MOVE_MS       = 500       # AI decision interval
```

All values can be tuned at runtime via the "Settings" panel (press **F1**).

---

## 7. Working with Controllers – Cheat‑Sheet

1. Launch the game and plug in a controller (before or after launch).
2. Observe the console: `GamepadManager ── detected "Xbox Wireless Controller" (GUID …)`
3. If the pad is not assigned, press **Start/Options** once to claim Player 1‑3.
4. Use **D‑Pad / Left‑Stick** to navigate the menu.
5. In‑game, default mapping is:

   * **← / →** – Move piece left/right
   * **↓** – Soft drop
   * **A / ×** – Rotate CW
   * **B / ○** – Rotate CCW
   * **Y / △** – Hard drop
   * **X / □** – Hold piece
   * **L / R** – Unused (configurable)

---

## 8. Debugging Common Issues

| Symptom                 | Possible Cause                  | Fix                                                           |
| ----------------------- | ------------------------------- | ------------------------------------------------------------- |
| Controller unresponsive | Pygame joystick not initialised | Ensure `pygame.joystick.init()` is called (done in `main.py`) |
| Wrong button mapping    | Unknown GUID                    | Add GUID → mapping in `UniversalGamepadMapper.MAP_TABLE`      |
| Input repeats too fast  | `INPUT_INTERVAL_MS` too low     | Increase in `constants.py`                                    |
| Cursed framerate        | V‑sync off or heavy print‑spam  | Toggle `VSYNC = True` or disable `DEBUG_PRINT`                |

---

## 9. Folder Layout (TL;DR)

```text
📂 project_root
├── main.py
├── tetris.py
├── input.py
├── cpu.py
├── ui.py
├── constants.py
├── requirements.txt  # = pygame (and optional watchdog)
└── assets/
    ├── fonts/
    ├── sounds/
    └── images/
```

---

## 10. Licence

This project is released under the **MIT Licence**.  See `LICENSE` for details.


