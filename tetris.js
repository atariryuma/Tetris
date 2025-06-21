// ゲームの設定と定数
const blockSize = 32;
const boardWidth = 10;
const boardHeight = 20;
const INPUT_INTERVAL = 180; // 入力の最小間隔(ms)

// ブロックカラー定義
const COLORS = {
    OBSTACLE: '#808080'
};

// 汎用コントローラー用ボタンマッピングシステム
class UniversalGamepadMapper {
    constructor() {
        // 標準的なゲームパッドボタンマッピング（Standard Gamepad Layout）
        this.standardMapping = {
            // Face buttons
            'A': [0],           // A/Cross
            'B': [1],           // B/Circle  
            'X': [2],           // X/Square
            'Y': [3],           // Y/Triangle
            
            // Shoulder buttons
            'LB': [4],          // Left Bumper
            'RB': [5],          // Right Bumper
            'LT': [6],          // Left Trigger
            'RT': [7],          // Right Trigger
            
            // Menu buttons
            'SELECT': [8],      // Select/Share
            'START': [9],       // Start/Options
            'LS': [10],         // Left Stick Click
            'RS': [11],         // Right Stick Click
            
            // D-pad (multiple possible mappings)
            'DPAD_UP': [12, 16],
            'DPAD_DOWN': [13, 17], 
            'DPAD_LEFT': [14, 18],
            'DPAD_RIGHT': [15, 19],
            
            // Additional mappings for various controllers
            'EXTRA1': [16], 'EXTRA2': [17], 'EXTRA3': [18], 'EXTRA4': [19],
            'EXTRA5': [20], 'EXTRA6': [21], 'EXTRA7': [22], 'EXTRA8': [23]
        };
        
        // Xbox One specific optimizations
        this.xboxMapping = {
            'A': [0], 'B': [1], 'X': [2], 'Y': [3],
            'LB': [4], 'RB': [5], 'LT': [6], 'RT': [7],
            'SELECT': [8], 'START': [9], 'LS': [10], 'RS': [11],
            'DPAD_UP': [12], 'DPAD_DOWN': [13], 'DPAD_LEFT': [14], 'DPAD_RIGHT': [15]
        };
    }
    
    detectControllerType(gamepad) {
        const id = gamepad.id.toLowerCase();
        if (id.includes('xbox') || id.includes('045e')) {
            return 'xbox';
        } else if (id.includes('playstation') || id.includes('sony') || id.includes('054c')) {
            return 'playstation';
        } else if (id.includes('nintendo') || id.includes('057e')) {
            return 'nintendo';
        }
        return 'generic';
    }
    
    getMapping(gamepad) {
        const type = this.detectControllerType(gamepad);
        switch (type) {
            case 'xbox':
                return this.xboxMapping;
            default:
                return this.standardMapping;
        }
    }
    
    isButtonPressed(gamepad, action) {
        const mapping = this.getMapping(gamepad);
        const buttonIndices = mapping[action] || [];
        
        return buttonIndices.some(buttonIndex => {
            const button = gamepad.buttons[buttonIndex];
            return button && button.pressed;
        });
    }
    
    getAxisValue(gamepad, axisIndex, deadzone = 0.1) {
        if (!gamepad.axes[axisIndex]) return 0;
        const value = gamepad.axes[axisIndex];
        return Math.abs(value) > deadzone ? value : 0;
    }
    
    detectPressedButtons(gamepad) {
        const pressed = [];
        for (let i = 0; i < gamepad.buttons.length; i++) {
            if (gamepad.buttons[i] && gamepad.buttons[i].pressed) {
                pressed.push(i);
            }
        }
        return pressed;
    }
}

// グローバルGamepad管理システム
class GamepadManager {
    constructor() {
        this.assignments = new Map(); // gamepadIndex -> playerId
        this.playerAssignments = new Map(); // playerId -> gamepadIndex
        this.availableGamepads = [];
        this.updateInterval = null;
    }
    
    startMonitoring() {
        this.updateAvailableGamepads();
        this.updateInterval = setInterval(() => {
            this.updateAvailableGamepads();
        }, 1000);
    }
    
    stopMonitoring() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
    
    updateAvailableGamepads() {
        try {
            // Gamepad API サポート確認
            if (!navigator.getGamepads) {
                console.error('ERROR: Gamepad API is not supported in this browser');
                return;
            }

            const gamepads = navigator.getGamepads();
            this.availableGamepads = [];
            
            console.log('=== Gamepad Detection Debug ===');
            console.log('Total gamepad slots found:', gamepads.length);
            console.log('Raw gamepads array:', gamepads);
            
            for (let i = 0; i < gamepads.length; i++) {
                console.log(`Slot ${i}:`, gamepads[i] ? 'OCCUPIED' : 'EMPTY');
                if (gamepads[i]) {
                    const gamepad = gamepads[i];
                    console.log(`  - ID: ${gamepad.id}`);
                    console.log(`  - Connected: ${gamepad.connected}`);
                    console.log(`  - Buttons: ${gamepad.buttons.length}`);
                    console.log(`  - Axes: ${gamepad.axes.length}`);
                    console.log(`  - Timestamp: ${gamepad.timestamp}`);
                    
                    if (gamepad.connected) {
                        this.availableGamepads.push({
                            index: i,
                            id: gamepad.id,
                            gamepad: gamepad
                        });
                        console.log(`  ✓ Added to available list`);
                    } else {
                        console.log(`  ✗ Not connected, skipping`);
                    }
                }
            }
            
            console.log(`Available gamepads after update: ${this.availableGamepads.length}`);
            if (this.availableGamepads.length === 0) {
                console.warn('WARNING: No gamepads detected! Make sure controllers are:');
                console.warn('1. Properly connected');
                console.warn('2. Recognized by the system');
                console.warn('3. Press any button to activate');
            }
            
        } catch (error) {
            console.error('ERROR in updateAvailableGamepads:', error);
        }
        
        // 切断されたゲームパッドの割り当てを削除
        for (let [gamepadIndex, playerId] of this.assignments.entries()) {
            if (!this.availableGamepads.find(gp => gp.index === gamepadIndex)) {
                console.log(`Gamepad ${gamepadIndex} disconnected, removing assignment from Player ${playerId}`);
                this.assignments.delete(gamepadIndex);
                this.playerAssignments.delete(playerId);
            }
        }
    }
    
    forceRefreshGamepads() {
        try {
            console.log('=== Force Refresh Gamepads ===');
            // Force a fresh check of gamepads by accessing the API multiple times
            for (let i = 0; i < 5; i++) {
                const gamepads = navigator.getGamepads();
                console.log(`Refresh attempt ${i + 1}: Found ${gamepads ? gamepads.length : 0} slots`);
            }
            this.updateAvailableGamepads();
        } catch (error) {
            console.error('ERROR in forceRefreshGamepads:', error);
        }
    }
    
    assignGamepadToPlayer(playerId) {
        try {
            console.log(`=== Assigning Gamepad to Player ${playerId} ===`);
            
            // 既に割り当てられている場合はスキップ
            if (this.playerAssignments.has(playerId)) {
                const existingIndex = this.playerAssignments.get(playerId);
                console.log(`Player ${playerId} already has gamepad ${existingIndex}`);
                return existingIndex;
            }
            
            // 最新のゲームパッド情報を取得
            console.log('Updating gamepad list before assignment...');
            this.updateAvailableGamepads();
            
            console.log(`Available gamepads: ${this.availableGamepads.length}`);
            console.log('Current assignments:', Object.fromEntries(this.assignments));
            
            // 利用可能な未割り当てのゲームパッドを検索
            for (let gamepadInfo of this.availableGamepads) {
                console.log(`Checking gamepad ${gamepadInfo.index}: ${this.assignments.has(gamepadInfo.index) ? 'ASSIGNED' : 'FREE'}`);
                if (!this.assignments.has(gamepadInfo.index)) {
                    this.assignments.set(gamepadInfo.index, playerId);
                    this.playerAssignments.set(playerId, gamepadInfo.index);
                    console.log(`✓ Successfully assigned gamepad ${gamepadInfo.index} (${gamepadInfo.id}) to Player ${playerId}`);
                    return gamepadInfo.index;
                }
            }
            
            console.error(`✗ FAILED: No available gamepad for Player ${playerId}`);
            console.error(`Available gamepads: ${this.availableGamepads.length}`);
            console.error(`Current assignments:`, Object.fromEntries(this.assignments));
            return null;
            
        } catch (error) {
            console.error(`ERROR in assignGamepadToPlayer for Player ${playerId}:`, error);
            return null;
        }
    }
    
    unassignPlayer(playerId) {
        const gamepadIndex = this.playerAssignments.get(playerId);
        if (gamepadIndex !== undefined) {
            this.assignments.delete(gamepadIndex);
            this.playerAssignments.delete(playerId);
            console.log(`Unassigned gamepad ${gamepadIndex} from Player ${playerId}`);
        }
    }
    
    getGamepadForPlayer(playerId) {
        const gamepadIndex = this.playerAssignments.get(playerId);
        if (gamepadIndex === undefined) return null;
        
        const gamepads = navigator.getGamepads();
        return gamepads[gamepadIndex] || null;
    }
    
    isGamepadAssigned(gamepadIndex) {
        return this.assignments.has(gamepadIndex);
    }
    
    getAssignmentInfo() {
        const info = {};
        for (let [gamepadIndex, playerId] of this.assignments.entries()) {
            const gamepadInfo = this.availableGamepads.find(gp => gp.index === gamepadIndex);
            info[playerId] = {
                gamepadIndex,
                gamepadId: gamepadInfo ? gamepadInfo.id : 'Unknown'
            };
        }
        return info;
    }
}

// UI ナビゲーション管理クラス
class UINavigationManager {
    constructor() {
        this.currentFocus = 0;
        this.focusableElements = [];
        this.isActive = false;
        this.lastInputTime = {};
        this.inputDelay = 300; // ms
    }
    
    setFocusableElements(elements) {
        this.focusableElements = elements;
        this.currentFocus = 0;
        this.updateVisualFocus();
    }
    
    enable() {
        this.isActive = true;
        console.log('UI Navigation activated');
    }
    
    disable() {
        this.isActive = false;
        this.clearVisualFocus();
        console.log('UI Navigation deactivated');
    }
    
    updateVisualFocus() {
        this.focusableElements.forEach((element, index) => {
            if (index === this.currentFocus) {
                element.style.outline = '3px solid #fca311';
                element.style.transform = 'scale(1.05)';
                element.style.transition = 'all 0.2s ease';
            } else {
                element.style.outline = 'none';
                element.style.transform = 'scale(1.0)';
            }
        });
    }
    
    clearVisualFocus() {
        this.focusableElements.forEach(element => {
            element.style.outline = 'none';
            element.style.transform = 'scale(1.0)';
        });
    }
    
    navigateUp() {
        if (!this.isActive || this.focusableElements.length === 0) return;
        this.currentFocus = (this.currentFocus - 1 + this.focusableElements.length) % this.focusableElements.length;
        this.updateVisualFocus();
        console.log(`Navigation: Focus moved to element ${this.currentFocus}`);
    }
    
    navigateDown() {
        if (!this.isActive || this.focusableElements.length === 0) return;
        this.currentFocus = (this.currentFocus + 1) % this.focusableElements.length;
        this.updateVisualFocus();
        console.log(`Navigation: Focus moved to element ${this.currentFocus}`);
    }
    
    navigateLeft() {
        if (!this.isActive || this.focusableElements.length === 0) return;
        this.currentFocus = (this.currentFocus - 1 + this.focusableElements.length) % this.focusableElements.length;
        this.updateVisualFocus();
        console.log(`Navigation: Focus moved to element ${this.currentFocus}`);
    }
    
    navigateRight() {
        if (!this.isActive || this.focusableElements.length === 0) return;
        this.currentFocus = (this.currentFocus + 1) % this.focusableElements.length;
        this.updateVisualFocus();
        console.log(`Navigation: Focus moved to element ${this.currentFocus}`);
    }
    
    activate() {
        if (!this.isActive || this.focusableElements.length === 0) return;
        const currentElement = this.focusableElements[this.currentFocus];
        console.log('Navigation: Activating element', currentElement);
        currentElement.click();
    }
    
    handleGamepadInput() {
        if (!this.isActive) return;
        
        const gamepads = navigator.getGamepads();
        for (let i = 0; i < gamepads.length; i++) {
            if (gamepads[i]) {
                const gamepad = gamepads[i];
                const now = Date.now();
                
                // D-pad navigation
                if (gamepadMapper.isButtonPressed(gamepad, 'DPAD_UP')) {
                    if (!this.lastInputTime.up || now - this.lastInputTime.up > this.inputDelay) {
                        this.navigateUp();
                        this.lastInputTime.up = now;
                    }
                } else if (gamepadMapper.isButtonPressed(gamepad, 'DPAD_DOWN')) {
                    if (!this.lastInputTime.down || now - this.lastInputTime.down > this.inputDelay) {
                        this.navigateDown();
                        this.lastInputTime.down = now;
                    }
                } else if (gamepadMapper.isButtonPressed(gamepad, 'DPAD_LEFT')) {
                    if (!this.lastInputTime.left || now - this.lastInputTime.left > this.inputDelay) {
                        this.navigateLeft();
                        this.lastInputTime.left = now;
                    }
                } else if (gamepadMapper.isButtonPressed(gamepad, 'DPAD_RIGHT')) {
                    if (!this.lastInputTime.right || now - this.lastInputTime.right > this.inputDelay) {
                        this.navigateRight();
                        this.lastInputTime.right = now;
                    }
                }
                
                // Analog stick navigation
                const leftStickX = gamepadMapper.getAxisValue(gamepad, 0, 0.5);
                const leftStickY = gamepadMapper.getAxisValue(gamepad, 1, 0.5);
                
                if (Math.abs(leftStickX) > 0.5) {
                    if (leftStickX > 0.5 && (!this.lastInputTime.stickRight || now - this.lastInputTime.stickRight > this.inputDelay)) {
                        this.navigateRight();
                        this.lastInputTime.stickRight = now;
                    } else if (leftStickX < -0.5 && (!this.lastInputTime.stickLeft || now - this.lastInputTime.stickLeft > this.inputDelay)) {
                        this.navigateLeft();
                        this.lastInputTime.stickLeft = now;
                    }
                }
                
                if (Math.abs(leftStickY) > 0.5) {
                    if (leftStickY > 0.5 && (!this.lastInputTime.stickDown || now - this.lastInputTime.stickDown > this.inputDelay)) {
                        this.navigateDown();
                        this.lastInputTime.stickDown = now;
                    } else if (leftStickY < -0.5 && (!this.lastInputTime.stickUp || now - this.lastInputTime.stickUp > this.inputDelay)) {
                        this.navigateUp();
                        this.lastInputTime.stickUp = now;
                    }
                }
                
                // Activation buttons
                if (gamepadMapper.isButtonPressed(gamepad, 'A') || 
                    gamepadMapper.isButtonPressed(gamepad, 'START')) {
                    if (!this.lastInputTime.activate || now - this.lastInputTime.activate > this.inputDelay) {
                        this.activate();
                        this.lastInputTime.activate = now;
                    }
                }
            }
        }
    }
}

// グローバルインスタンス
const gamepadManager = new GamepadManager();
const gamepadMapper = new UniversalGamepadMapper();
const uiNavigation = new UINavigationManager();

const shapes = [
    { shape: [[1, 1, 1, 1]], color: "#00FFFF" }, // Iテトリミノ
    { shape: [[1, 1, 1], [0, 1, 0]], color: "#FFA500" }, // Tテトリミノ
    { shape: [[1, 1], [1, 1]], color: "#FFFF00" }, // Oテトリミノ
    { shape: [[1, 1, 0], [0, 1, 1]], color: "#00FF00" }, // Sテトリミノ
    { shape: [[0, 1, 1], [1, 1, 0]], color: "#FF0000" }, // Zテトリミノ
    { shape: [[1, 1, 1], [1, 0, 0]], color: "#0000FF" }, // Jテトリミノ
    { shape: [[1, 1, 1], [0, 0, 1]], color: "#FF00FF" }  // Lテトリミノ
];

function getRandomShape() {
    const randomIndex = Math.floor(Math.random() * shapes.length);
    return deepCopyShape(shapes[randomIndex]);
}

function deepCopyShape(shape) {
    return {
        shape: shape.shape.map(row => [...row]),
        color: shape.color,
        type: shape.type || null
    };
}

// Tetrisクラスの定義
class Tetris {
    constructor(playerId, mode) {
        this.playerId = playerId;
        this.mode = mode; // 'ON' (human), 'CPU', or 'OFF'
        this.canvas = document.getElementById(`player${playerId}Canvas`);
        this.ctx = this.canvas.getContext('2d');
        this.nextCanvas = document.getElementById(`player${playerId}Next`);
        this.nextCtx = this.nextCanvas.getContext('2d');
        this.scoreElement = document.getElementById(`player${playerId}Score`);
        
        this.canvas.width = boardWidth * blockSize;
        this.canvas.height = boardHeight * blockSize;
        this.nextCanvas.width = 4 * (blockSize / 4);
        this.nextCanvas.height = 4 * (blockSize / 4);
        
        this.board = Array.from({ length: boardHeight }, () => Array(boardWidth).fill(0));
        this.currentShape = null;
        this.nextShape = null;
        this.currentPosition = { x: Math.floor(boardWidth / 2) - 1, y: 0 };
        this.ghostPosition = { x: 0, y: 0 };
        this.dropInterval = 700;
        this.lastDropTime = 0;
        this.gameOver = false;
        this.score = 0;
        
        this.lastInputTime = {
            left: 0,
            right: 0,
            down: 0,
            rotate: 0,
            hardDrop: 0
        };
        
        // CPUのAI設定
        this.cpuMoveInterval = 500;
        this.lastCPUMoveTime = 0;
        
        // Gamepad設定
        this.gamepadButtonStates = {};
        
        // Animation設定
        this.animatingObstacles = [];
        this.obstacleAnimationSpeed = 8; // pixels per frame
    }

    assignGamepad() {
        console.log(`Player ${this.playerId} (${this.mode}) requesting gamepad assignment...`);
        const result = gamepadManager.assignGamepadToPlayer(this.playerId);
        if (result !== null) {
            console.log(`Player ${this.playerId} successfully got gamepad ${result}`);
        } else {
            console.error(`Player ${this.playerId} FAILED to get gamepad`);
        }
        return result;
    }
    
    hasGamepadInput() {
        const gamepad = gamepadManager.getGamepadForPlayer(this.playerId);
        if (!gamepad) {
            return false;
        }
        
        return gamepad.buttons.some(button => button.pressed) || 
               Math.abs(gamepad.axes[0]) > 0.1 || Math.abs(gamepad.axes[1]) > 0.1;
    }
    
    getAssignedGamepad() {
        return gamepadManager.getGamepadForPlayer(this.playerId);
    }

    start() {
        this.currentShape = getRandomShape();
        this.nextShape = getRandomShape();
        this.updateGhostPosition();
        this.lastDropTime = performance.now();
        this.lastCPUMoveTime = performance.now();
        
        // ゲームパッドの割り当てを試行
        this.assignGamepad();
        
        this.draw();
        this.drawNext();
    }

    update(time) {
        if (this.gameOver) return 0;
        
        // Handle gamepad input if connected
        if (this.mode === 'ON') {
            this.handleGamepadInput(time);
        }
        
        if (this.mode === 'CPU') {
            if (time - this.lastCPUMoveTime > this.cpuMoveInterval) {
                this.makeCPUMove();
                this.lastCPUMoveTime = time;
            }
        }
        
        if (time - this.lastDropTime > this.dropInterval) {
            this.lastDropTime = time;
            if (!this.moveDown()) {
                const clearedLines = this.placeShape();
                this.setNextShape();
                if (this.checkGameOver()) {
                    this.gameOver = true;
                }
                this.draw();
                this.drawNext();
                return clearedLines;
            }
        }
        
        this.draw();
        this.drawNext();
        return 0;
    }
    
    handleGamepadInput(time) {
        const gamepad = this.getAssignedGamepad();
        if (!gamepad) return;
        
        const inputInterval = INPUT_INTERVAL;
        
        // デバッグ: コントローラータイプとボタン状態をログ出力
        if (Math.random() < 0.005) { // 0.5%の確率でログ出力
            const controllerType = gamepadMapper.detectControllerType(gamepad);
            const pressedButtons = gamepadMapper.detectPressedButtons(gamepad);
            console.log(`Player ${this.playerId} [${controllerType}] pressed buttons:`, pressedButtons);
        }
        
        // 汎用ボタンチェック関数
        const checkAction = (action, gameAction, inputType) => {
            if (gamepadMapper.isButtonPressed(gamepad, action)) {
                const actionKey = `${action}_${this.playerId}`;
                const wasPressed = this.gamepadButtonStates[actionKey] || false;
                this.gamepadButtonStates[actionKey] = true;
                
                // 新しく押された場合のみ実行
                if (!wasPressed && time - this.lastInputTime[inputType] > inputInterval) {
                    gameAction();
                    this.lastInputTime[inputType] = time;
                    return true;
                }
            } else {
                this.gamepadButtonStates[`${action}_${this.playerId}`] = false;
            }
            return false;
        };
        
        // アナログスティック対応（Xbox Oneコントローラー最適化）
        const leftStickX = gamepadMapper.getAxisValue(gamepad, 0, 0.3); // デッドゾーン拡大
        const leftStickY = gamepadMapper.getAxisValue(gamepad, 1, 0.3);
        
        // アナログスティック左右移動
        if (Math.abs(leftStickX) > 0.3) {
            const now = time;
            if (leftStickX < -0.3 && now - this.lastInputTime.left > inputInterval) {
                this.move(-1);
                this.lastInputTime.left = now;
            } else if (leftStickX > 0.3 && now - this.lastInputTime.right > inputInterval) {
                this.move(1);
                this.lastInputTime.right = now;
            }
        }
        
        // アナログスティック下移動
        if (leftStickY > 0.3 && time - this.lastInputTime.down > inputInterval) {
            this.drop();
            this.lastInputTime.down = time;
        }
        
        // D-pad操作（汎用マッピング使用）
        checkAction('DPAD_LEFT', () => this.move(-1), 'left');
        checkAction('DPAD_RIGHT', () => this.move(1), 'right');
        checkAction('DPAD_DOWN', () => this.drop(), 'down');
        checkAction('DPAD_UP', () => this.hardDrop(), 'hardDrop');
        
        // ボタン操作（フェイスボタンで回転）
        checkAction('A', () => this.rotate(), 'rotate') ||
        checkAction('B', () => this.rotate(), 'rotate') ||
        checkAction('X', () => this.rotate(), 'rotate') ||
        checkAction('Y', () => this.rotate(), 'rotate');
        
        // 追加操作（肩ボタンでも回転可能）
        checkAction('RB', () => this.rotate(), 'rotate') ||
        checkAction('LB', () => this.hardDrop(), 'hardDrop');
    }

    makeCPUMove() {
        // シンプルなCPUロジック
        if (Math.random() < 0.3) {
            if (this.canMove(-1, 0)) {
                this.move(-1);
            } else if (this.canMove(1, 0)) {
                this.move(1);
            }
        }
        
        if (Math.random() < 0.1) {
            this.rotate();
        }
        
        if (Math.random() < 0.5) {
            this.drop();
        }
    }

    move(dx) {
        if (this.canMove(dx, 0)) {
            this.currentPosition.x += dx;
            this.updateGhostPosition();
        }
    }

    drop() {
        if (this.canMove(0, 1)) {
            this.currentPosition.y += 1;
            this.updateGhostPosition();
        }
    }

    rotate() {
        const rotatedShape = this.rotateMatrix(this.currentShape.shape);
        if (this.isValidMove(rotatedShape, this.currentPosition.x, this.currentPosition.y)) {
            this.currentShape.shape = rotatedShape;
            this.updateGhostPosition();
        } else {
            // Wall kick
            const offsets = [-1, 1, -2, 2];
            for (let offset of offsets) {
                if (this.isValidMove(rotatedShape, this.currentPosition.x + offset, this.currentPosition.y)) {
                    this.currentShape.shape = rotatedShape;
                    this.currentPosition.x += offset;
                    this.updateGhostPosition();
                    break;
                }
            }
        }
    }

    flip() {
        if (this.gameOver || !this.currentShape) return;

        const flippedShape = this.currentShape.shape.map(row => row.slice().reverse());
        if (this.isValidMove(flippedShape, this.currentPosition.x, this.currentPosition.y)) {
            this.currentShape.shape = flippedShape;
            this.updateGhostPosition();
        }
    }

    hardDrop() {
        let clearedLines = 0;
        while (this.canMove(0, 1)) {
            this.currentPosition.y += 1;
        }
        clearedLines = this.placeShape();
        this.setNextShape();
        if (this.checkGameOver()) {
            this.gameOver = true;
        }
        this.draw();
        this.drawNext();
        return clearedLines;
    }

    canMove(dx, dy) {
        return this.isValidMove(this.currentShape.shape, this.currentPosition.x + dx, this.currentPosition.y + dy);
    }

    moveDown() {
        if (this.canMove(0, 1)) {
            this.currentPosition.y += 1;
            return true;
        }
        return false;
    }

    isValidMove(shape, x, y) {
        return shape.every((row, dy) => {
            return row.every((cell, dx) => {
                let newX = x + dx;
                let newY = y + dy;
                return !cell || (newX >= 0 && newX < boardWidth && newY < boardHeight && !this.board[newY][newX]);
            });
        });
    }

    placeShape() {
        this.currentShape.shape.forEach((row, dy) => {
            row.forEach((cell, dx) => {
                if (cell) {
                    this.board[this.currentPosition.y + dy][this.currentPosition.x + dx] = this.currentShape.color;
                }
            });
        });
        
        let clearedLines = 0;
        for (let y = this.board.length - 1; y >= 0; y--) {
            if (this.board[y].every(cell => cell)) {
                this.board.splice(y, 1);
                this.board.unshift(Array(boardWidth).fill(0));
                clearedLines++;
                y++;
            }
        }
        
        this.score += this.calculateScore(clearedLines);
        this.updateScore();
        return clearedLines;
    }

    calculateScore(clearedLines) {
        const scores = [0, 100, 300, 500, 800];
        return scores[clearedLines] || 0;
    }

    setNextShape() {
        this.currentShape = deepCopyShape(this.nextShape);
        this.nextShape = getRandomShape();
        this.currentPosition = { x: Math.floor(boardWidth / 2) - 1, y: 0 };
        this.updateGhostPosition();
    }

    checkGameOver() {
        return !this.isValidMove(this.currentShape.shape, this.currentPosition.x, this.currentPosition.y);
    }

    updateGhostPosition() {
        let ghostY = this.currentPosition.y;
        while (this.isValidMove(this.currentShape.shape, this.currentPosition.x, ghostY + 1)) {
            ghostY++;
        }
        this.ghostPosition = { x: this.currentPosition.x, y: ghostY };
    }

    rotateMatrix(matrix) {
        const result = [];
        for (let col = 0; col < matrix[0].length; col++) {
            const newRow = [];
            for (let row = matrix.length - 1; row >= 0; row--) {
                newRow.push(matrix[row][col]);
            }
            result.push(newRow);
        }
        return result;
    }

    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Update and draw animating obstacles
        this.updateObstacleAnimations();
        
        // Draw board
        this.board.forEach((row, y) => {
            row.forEach((color, x) => {
                if (color) {
                    this.drawBlock(x, y, color);
                }
            });
        });
        
        // Draw animating obstacles
        this.drawAnimatingObstacles();
        
        // Draw ghost shape
        if (this.currentShape) {
            this.drawGhostShape();
            this.drawShape(this.currentShape.shape, this.currentPosition.x, this.currentPosition.y, this.currentShape.color);
        }
    }

    drawNext() {
        if (!this.nextShape) return;
        
        this.nextCtx.clearRect(0, 0, this.nextCanvas.width, this.nextCanvas.height);
        
        const nextBlockSize = blockSize / 4; // Next キャンバス用のより小さいブロックサイズ
        const startX = Math.floor((4 - this.nextShape.shape[0].length) / 2);
        const startY = Math.floor((4 - this.nextShape.shape.length) / 2);
        
        this.nextShape.shape.forEach((row, dy) => {
            row.forEach((cell, dx) => {
                if (cell) {
                    this.nextCtx.fillStyle = this.nextShape.color;
                    this.nextCtx.fillRect((startX + dx) * nextBlockSize, (startY + dy) * nextBlockSize, nextBlockSize, nextBlockSize);
                    this.nextCtx.strokeStyle = '#000';
                    this.nextCtx.strokeRect((startX + dx) * nextBlockSize, (startY + dy) * nextBlockSize, nextBlockSize, nextBlockSize);
                }
            });
        });
    }

    drawBlock(x, y, color) {
        this.ctx.fillStyle = color;
        this.ctx.fillRect(x * blockSize, y * blockSize, blockSize, blockSize);
        this.ctx.strokeStyle = '#000';
        this.ctx.strokeRect(x * blockSize, y * blockSize, blockSize, blockSize);
    }

    drawShape(shape, x, y, color) {
        shape.forEach((row, dy) => {
            row.forEach((cell, dx) => {
                if (cell) {
                    this.drawBlock(x + dx, y + dy, color);
                }
            });
        });
    }

    drawGhostShape() {
        this.ctx.globalAlpha = 0.3;
        this.drawShape(this.currentShape.shape, this.ghostPosition.x, this.ghostPosition.y, this.currentShape.color);
        this.ctx.globalAlpha = 1;
    }

    updateScore() {
        if (this.scoreElement) {
            this.scoreElement.textContent = this.score;
        }
    }

    addObstacle(lines) {
        if (this.gameOver || lines <= 0) return;
        
        // アニメーション付きでお邪魔ブロックを追加
        for (let i = 0; i < lines; i++) {
            const obstacleRow = Array(boardWidth).fill(COLORS.OBSTACLE);
            obstacleRow[Math.floor(Math.random() * boardWidth)] = 0; // ランダムな位置に穴を開ける
            
            // アニメーション情報を追加
            this.animatingObstacles.push({
                row: obstacleRow,
                targetY: boardHeight - 1 - i,
                currentY: boardHeight + i, // 画面下から開始
                animationProgress: 0
            });
        }
        
        // ボードから上の行を削除
        for (let i = 0; i < lines; i++) {
            this.board.splice(0, 1);
        }

        // 現在のピースが衝突する場合はゲームオーバー
        if (this.currentShape && !this.isValidMove(this.currentShape.shape, this.currentPosition.x, this.currentPosition.y)) {
            this.gameOver = true;
        }
    }
    
    updateObstacleAnimations() {
        this.animatingObstacles = this.animatingObstacles.filter(obstacle => {
            obstacle.animationProgress += this.obstacleAnimationSpeed;
            obstacle.currentY = obstacle.targetY + (boardHeight - obstacle.targetY) * (1 - obstacle.animationProgress / 100);
            
            // アニメーション完了
            if (obstacle.animationProgress >= 100) {
                this.board.push(obstacle.row);
                return false;
            }
            return true;
        });
    }
    
    drawAnimatingObstacles() {
        this.animatingObstacles.forEach(obstacle => {
            obstacle.row.forEach((color, x) => {
                if (color) {
                    this.ctx.fillStyle = color;
                    this.ctx.fillRect(x * blockSize, obstacle.currentY * blockSize, blockSize, blockSize);
                    this.ctx.strokeStyle = '#000';
                    this.ctx.strokeRect(x * blockSize, obstacle.currentY * blockSize, blockSize, blockSize);
                }
            });
        });
    }
}