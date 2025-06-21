// ゲームの設定と定数
const canvas1 = document.getElementById("player1Canvas");
const ctx1 = canvas1.getContext("2d");
const canvas2 = document.getElementById("player2Canvas");
const ctx2 = canvas2.getContext("2d");
const canvas3 = document.getElementById("player3Canvas");
const ctx3 = canvas3.getContext("2d");
const blockSize = 32;
const boardWidth = 10;
const boardHeight = 20;
const INPUT_INTERVAL = 180; // 入力の最小間隔(ms)

const keyBindings = [
    { left: 'ArrowLeft', right: 'ArrowRight', down: 'ArrowDown', rotate: 'z', hardDrop: 'ArrowUp', flip: 'x' },
    { left: 'a', right: 'd', down: 's', rotate: 'w', hardDrop: 'q', flip: 'e' },
    { left: 'j', right: 'l', down: 'k', rotate: 'i', hardDrop: 'u', flip: 'o' }
];
canvas1.width = canvas2.width = canvas3.width = boardWidth * blockSize;
canvas1.height = canvas2.height = canvas3.height = boardHeight * blockSize;

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


let players = [];
let activePlayers = [true, true, true]; // 1P, 2P, 3P のオンオフ状態を管理
let gameActive = false;  // ゲームのアクティブ状態を管理

document.getElementById('startButton').addEventListener('click', () => {
    gameActive = true;
    initializePlayers();
    assignGamepadsToPlayers();
    requestFullScreen();
    resetGame();
    gameLoop();
});

document.getElementById('togglePlayer1').addEventListener('click', () => {
    activePlayers[0] = !activePlayers[0];
    toggleCanvasVisibility(canvas1, activePlayers[0]);
});

document.getElementById('togglePlayer2').addEventListener('click', () => {
    activePlayers[1] = !activePlayers[1];
    toggleCanvasVisibility(canvas2, activePlayers[1]);
});

document.getElementById('togglePlayer3').addEventListener('click', () => {
    activePlayers[2] = !activePlayers[2];
    toggleCanvasVisibility(canvas3, activePlayers[2]);
});

// キーボード入力イベントを登録
document.addEventListener('keydown', handleKeyboardInput);
window.addEventListener('gamepadconnected', assignGamepadsToPlayers);
window.addEventListener('gamepaddisconnected', assignGamepadsToPlayers);

function toggleCanvasVisibility(canvas, isVisible) {
    canvas.style.display = isVisible ? 'block' : 'none';
}

function requestFullScreen() {
    const elem = document.documentElement;
    if (elem.requestFullscreen) {
        elem.requestFullscreen();
    } else if (elem.mozRequestFullScreen) { // Firefox
        elem.mozRequestFullScreen();
    } else if (elem.webkitRequestFullscreen) { // Chrome, Safari and Opera
        elem.webkitRequestFullscreen();
    } else if (elem.msRequestFullscreen) { // IE/Edge
        elem.msRequestFullscreen();
    }
}

function initializePlayers() {
    players = [
        new Player('Player 1', ctx1, '#00FFFF', null),
        new Player('Player 2', ctx2, '#FF00FF', null),
        new Player('Player 3', ctx3, '#00FF00', null)
    ];
    assignGamepadsToPlayers();
}

function assignGamepadsToPlayers() {
    const connected = [];
    const pads = navigator.getGamepads ? navigator.getGamepads() : [];
    for (let i = 0; i < pads.length; i++) {
        if (pads[i]) connected.push(i);
    }
    players.forEach((player, index) => {
        player.gamepadIndex = connected[index] !== undefined ? connected[index] : null;
    });
}

function resetGame() {
    players.forEach(player => {
        player.reset();
    });
}

function gameLoop() {
    if (!gameActive) {
        return;  // ゲームが非アクティブの場合はループを終了
    }
    handleControllerInput();
    players.forEach((player, index) => {
        if (activePlayers[index] && Date.now() - player.lastDropTime > player.dropInterval) {
            player.lastDropTime = Date.now();
            if (!moveDown(player)) {
                const clearedLines = placeShape(player);
                addObstacleBlocks(player, clearedLines);
                if (resetPlayer(player)) {
                    if (checkGameOver()) {
                        endGame();
                        return;
                    }
                }
            }
        }
        if (activePlayers[index]) {
            draw(player);
        }
    });
    requestAnimationFrame(gameLoop);
}

function endGame() {
    gameActive = false;  // ゲームを非アクティブに設定
    const activePlayersList = players.filter((player, index) => activePlayers[index]);
    if (activePlayersList.length === 1) {
        alert(activePlayersList[0].name + " wins!");
    }
}

function resetPlayer(player) {
    player.setNextShape();  // 次のブロックに切り替える
    if (player.gameOver) {
        activePlayers[players.indexOf(player)] = false;
        toggleCanvasVisibility(player.ctx.canvas, false);
        return true;  // ゲームオーバーを示す
    }
    return false;
}

function checkGameOver() {
    return activePlayers.filter(isActive => isActive).length === 1;
}

// コントローラー入力を処理
function handleControllerInput() {
    const gamepads = navigator.getGamepads();
    players.forEach(player => {
        if (player.gamepadIndex !== null) {
            const gamepad = gamepads[player.gamepadIndex];
            if (gamepad) {
                player.handleControllerInput(gamepad);
            }
        }
    });
}

// キーボード入力を処理
function handleKeyboardInput(event) {
    if (!gameActive) return;
    players.forEach((player, index) => {
        if (!activePlayers[index]) return;
        const binding = keyBindings[index];
        const last = player.lastInputTime;
        const key = event.key;

        if (key === binding.hardDrop && Date.now() - last.hardDrop > INPUT_INTERVAL) {
            player.hardDrop();
            last.hardDrop = Date.now();
        } else if (key === binding.left && Date.now() - last.left > INPUT_INTERVAL) {
            if (isValidMove(player.currentShape.shape, player.currentPosition.x - 1, player.currentPosition.y, player)) {
                player.currentPosition.x -= 1;
                last.left = Date.now();
                player.updateGhostPosition();
            }
        } else if (key === binding.right && Date.now() - last.right > INPUT_INTERVAL) {
            if (isValidMove(player.currentShape.shape, player.currentPosition.x + 1, player.currentPosition.y, player)) {
                player.currentPosition.x += 1;
                last.right = Date.now();
                player.updateGhostPosition();
            }
        } else if (key === binding.down && Date.now() - last.down > INPUT_INTERVAL) {
            if (isValidMove(player.currentShape.shape, player.currentPosition.x, player.currentPosition.y + 1, player)) {
                player.currentPosition.y += 1;
                last.down = Date.now();
                player.updateGhostPosition();
            }
        } else if (key === binding.rotate && Date.now() - last.rotate > INPUT_INTERVAL) {
            const rotatedShape = rotate(player.currentShape.shape);
            if (isValidMove(rotatedShape, player.currentPosition.x, player.currentPosition.y, player)) {
                player.currentShape.shape = rotatedShape;
                last.rotate = Date.now();
                player.updateGhostPosition();
            } else {
                const leftPos = { x: player.currentPosition.x - 1, y: player.currentPosition.y };
                const rightPos = { x: player.currentPosition.x + 1, y: player.currentPosition.y };
                if (isValidMove(rotatedShape, leftPos.x, leftPos.y, player)) {
                    player.currentShape.shape = rotatedShape;
                    player.currentPosition = leftPos;
                    last.rotate = Date.now();
                    player.updateGhostPosition();
                } else if (isValidMove(rotatedShape, rightPos.x, rightPos.y, player)) {
                    player.currentShape.shape = rotatedShape;
                    player.currentPosition = rightPos;
                    last.rotate = Date.now();
                    player.updateGhostPosition();
                }
            }
        } else if (key === binding.flip && Date.now() - last.flip > INPUT_INTERVAL) {
            const flippedShape = flip(player.currentShape.shape);
            if (isValidMove(flippedShape, player.currentPosition.x, player.currentPosition.y, player)) {
                player.currentShape.shape = flippedShape;
                last.flip = Date.now();
                player.updateGhostPosition();
            }
        }
    });
}

function drawBlock(ctx, x, y, color) {
    ctx.fillStyle = color;
    ctx.fillRect(x * blockSize, y * blockSize, blockSize, blockSize);
    ctx.strokeStyle = '#000';
    ctx.strokeRect(x * blockSize, y * blockSize, blockSize, blockSize);
}

function draw(player) {
    const ctx = player.ctx;
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    player.board.forEach((row, y) => {
        row.forEach((color, x) => {
            if (color) {
                drawBlock(ctx, x, y, color);
            }
        });
    });
    drawShape(ctx, player.currentShape.shape, player.currentPosition.x, player.currentPosition.y, player.currentShape.color);
    drawGhostShape(ctx, player.currentShape.shape, player.ghostPosition.x, player.ghostPosition.y, player.currentShape.color);
    drawScore(player);  // スコアを描画
}

function drawScore(player) {
    const ctx = player.ctx;
    ctx.font = '20px Arial';
    ctx.fillStyle = 'white';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillText(`${player.name} Score: ${player.score}`, 10, 10);
}

function drawShape(ctx, shape, x, y, color) {
    shape.forEach((row, dy) => {
        row.forEach((cell, dx) => {
            if (cell) {
                drawBlock(ctx, x + dx, y + dy, color);
            }
        });
    });
}

function drawGhostShape(ctx, shape, x, y, color) {
    ctx.globalAlpha = 0.5;
    drawShape(ctx, shape, x, y, color);
    ctx.globalAlpha = 1;
}

function Player(name, ctx, color, gamepadIndex) {
    this.name = name;
    this.ctx = ctx;
    this.board = Array.from({ length: boardHeight }, () => Array(boardWidth).fill(0));
    this.currentPosition = { x: Math.floor(boardWidth / 2) - 1, y: 0 };
    this.currentShape = getRandomShape();  // 修正: 初期値をランダムなブロックに設定
    this.nextShape = getRandomShape();
    this.dropInterval = 700;
    this.lastDropTime = Date.now();
    this.gameOver = false;
    this.color = color;
    this.gamepadIndex = gamepadIndex;
    this.ghostPosition = { x: 0, y: 0 };
    this.score = 0;
    this.shielded = false;

    // 追加: コントローラー入力の最後の時間を管理するオブジェクト
    this.lastInputTime = {
        left: 0,
        right: 0,
        down: 0,
        rotate: 0,
        hardDrop: 0,
        flip: 0
    };

    // コントローラー入力を処理するメソッド
    this.handleControllerInput = function(gamepad) {
        const inputInterval = INPUT_INTERVAL; // ボタン入力の最小時間間隔

        // ハードドロップ (十字キーの上)
        if (gamepad.buttons[12].pressed && Date.now() - this.lastInputTime.hardDrop > inputInterval) {
            this.hardDrop();
            this.lastInputTime.hardDrop = Date.now();
        }

        // 左移動
        if (gamepad.buttons[14].pressed && Date.now() - this.lastInputTime.left > inputInterval) {
            if (isValidMove(this.currentShape.shape, this.currentPosition.x - 1, this.currentPosition.y, this)) {
                this.currentPosition.x -= 1;
                this.lastInputTime.left = Date.now();
                this.updateGhostPosition();
            }
        }

        // 右移動
        if (gamepad.buttons[15].pressed && Date.now() - this.lastInputTime.right > inputInterval) {
            if (isValidMove(this.currentShape.shape, this.currentPosition.x + 1, this.currentPosition.y, this)) {
                this.currentPosition.x += 1;
                this.lastInputTime.right = Date.now();
                this.updateGhostPosition();
            }
        }

        // 下移動
        if (gamepad.buttons[13].pressed && Date.now() - this.lastInputTime.down > inputInterval) {
            if (isValidMove(this.currentShape.shape, this.currentPosition.x, this.currentPosition.y + 1, this)) {
                this.currentPosition.y += 1;
                this.lastInputTime.down = Date.now();
                this.updateGhostPosition();
            }
        }

        // 回転
        if (gamepad.buttons[0].pressed && Date.now() - this.lastInputTime.rotate > inputInterval) {
            const rotatedShape = rotate(this.currentShape.shape);
            if (isValidMove(rotatedShape, this.currentPosition.x, this.currentPosition.y, this)) {
                this.currentShape.shape = rotatedShape;
                this.lastInputTime.rotate = Date.now();
                this.updateGhostPosition();
            } else {
                // 回転できない場合は、左右に1ブロック移動して回転を試みる
                const leftPosition = { x: this.currentPosition.x - 1, y: this.currentPosition.y };
                const rightPosition = { x: this.currentPosition.x + 1, y: this.currentPosition.y };
                if (isValidMove(rotatedShape, leftPosition.x, leftPosition.y, this)) {
                    this.currentShape.shape = rotatedShape;
                    this.currentPosition = leftPosition;
                    this.lastInputTime.rotate = Date.now();
                    this.updateGhostPosition();
                } else if (isValidMove(rotatedShape, rightPosition.x, rightPosition.y, this)) {
                    this.currentShape.shape = rotatedShape;
                    this.currentPosition = rightPosition;
                    this.lastInputTime.rotate = Date.now();
                    this.updateGhostPosition();
                }
            }
        }

        // 反転 (フリップ)
        if (gamepad.buttons[1].pressed && Date.now() - this.lastInputTime.flip > inputInterval) {
            const flippedShape = flip(this.currentShape.shape);
            if (isValidMove(flippedShape, this.currentPosition.x, this.currentPosition.y, this)) {
                this.currentShape.shape = flippedShape;
                this.lastInputTime.flip = Date.now();
                this.updateGhostPosition();
            }
        }
    };

    // ゴーストピースの位置を更新するメソッド
    this.updateGhostPosition = function() {
        let ghostY = this.currentPosition.y;
        while (isValidMove(this.currentShape.shape, this.currentPosition.x, ghostY + 1, this)) {
            ghostY++;
        }
        this.ghostPosition = { x: this.currentPosition.x, y: ghostY };
    };

    // ハードドロップを実行するメソッド
    this.hardDrop = function() {
        while (moveDown(this)) {
            // ピースを可能な限り下へ移動
        }
        const clearedLines = placeShape(this);  // 最終位置にピースを固定し、消去ライン数を取得
        addObstacleBlocks(this, clearedLines);  // 相手プレイヤーに邪魔ブロックを追加
        if (resetPlayer(this)) {
            if (checkGameOver()) {
                endGame();
                return;
            }
        }
    };

    // 追加: 次のブロックに切り替えるメソッド    
    this.setNextShape = function() {
        this.currentShape = deepCopyShape(this.nextShape);
        this.nextShape = getRandomShape();
        this.currentPosition = { x: Math.floor(boardWidth / 2) - 1, y: 0 };
        if (!isValidMove(this.currentShape.shape, this.currentPosition.x, this.currentPosition.y, this)) {
            this.gameOver = true;
        }
        this.updateGhostPosition();
    };

    this.reset = function() {
        this.board = Array.from({ length: boardHeight }, () => Array(boardWidth).fill(0));
        this.currentPosition = { x: Math.floor(boardWidth / 2) - 1, y: 0 };
        this.currentShape = getRandomShape();
        this.nextShape = getRandomShape();
        this.dropInterval = 700;
        this.lastDropTime = Date.now();
        this.gameOver = false;
        this.score = 0;
        this.updateGhostPosition();
    }
}

function rotate(matrix) {
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

function flip(matrix) {
    return matrix.map(row => row.reverse());
}

function isValidMove(shape, x, y, player) {
    return shape.every((row, dy) => {
        return row.every((cell, dx) => {
            let newX = x + dx;
            let newY = y + dy;
            return !cell || (newX >= 0 && newX < boardWidth && newY < boardHeight && !player.board[newY][newX]);
        });
    });
}

function moveDown(player) {
    if (isValidMove(player.currentShape.shape, player.currentPosition.x, player.currentPosition.y + 1, player)) {
        player.currentPosition.y++;
        return true;
    }
    return false;
}

function placeShape(player) {
    const specialBlocks = [];
    player.currentShape.shape.forEach((row, dy) => {
        row.forEach((cell, dx) => {
            if (cell) {
                player.board[player.currentPosition.y + dy][player.currentPosition.x + dx] = player.currentShape.color;
                if (player.currentShape.type) {
                    specialBlocks.push({ x: player.currentPosition.x + dx, y: player.currentPosition.y + dy, type: player.currentShape.type });
                }
            }
        });
    });
    applySpecialBlockEffects(player, specialBlocks); // 常にエフェクトを表示するように変更
    return clearLines(player, specialBlocks);
}

function clearLines(player, specialBlocks = []) {
    let clearedLines = 0;
    for (let y = player.board.length - 1; y >= 0; y--) {
        if (player.board[y].every(cell => cell)) {
            player.board.splice(y, 1);
            player.board.unshift(Array(boardWidth).fill(0));
            clearedLines++;
            y++; // since the line is removed, we need to check the same line again
        }
    }
    // スコアを更新
    player.score += calculateScore(clearedLines);
    return clearedLines;
}

function calculateScore(clearedLines) {
    const scores = [0, 100, 300, 500, 800];
    return scores[clearedLines] || 0;
}

function addObstacleBlocks(player, clearedLines) {
    if (clearedLines === 0) return;

    // 対象となるプレイヤーを抽出（自分以外のアクティブなプレイヤー）
    const targets = players.filter((p, idx) => p !== player && activePlayers[idx] && !p.shielded);
    if (targets.length === 0) return;

    const linesPerTarget = Math.floor(clearedLines / targets.length);
    let remainder = clearedLines % targets.length;

    targets.forEach(target => {
        let linesToAdd = linesPerTarget;
        if (remainder > 0) {
            linesToAdd += 1;
            remainder -= 1;
        }
        for (let i = 0; i < linesToAdd; i++) {
            target.board.splice(0, 1);
            target.board.push(
                Array(boardWidth)
                    .fill(0)
                    .map((_, index) => (index === Math.floor(boardWidth / 2) ? 0 : '#808080'))
            );
        }
    });
}

// 特殊ブロックの効果を適用する関数
function applySpecialBlockEffects(player, specialBlocks) {
    specialBlocks.forEach(block => {
        switch (block.type) {
            case 'bomb':
                applyBombEffect(player, block.x, block.y);
                break;
            case 'scoreBooster':
                player.score += 500; // 追加スコア
                showEffect(player.ctx, block.x, block.y, 'Score Boost!');
                break;
            case 'slowMotion':
                applySlowMotionEffect();
                showEffect(player.ctx, block.x, block.y, 'Slow Motion!');
                break;
            case 'shield':
                applyShieldEffect(player);
                showEffect(player.ctx, block.x, block.y, 'Shield!');
                break;
            case 'invisible':
                applyInvisibleEffect(player);
                showEffect(player.ctx, block.x, block.y, 'Invisible!');
                break;
            case 'random':
                applyRandomEffect(player);
                showEffect(player.ctx, block.x, block.y, 'Random!');
                break;
            case 'health':
                applyHealthEffect(player);
                showEffect(player.ctx, block.x, block.y, 'Health!');
                break;
            case 'blind':
                applyBlindEffect(player);
                showEffect(player.ctx, block.x, block.y, 'Blind!');
                break;
        }
    });
}

function applyBombEffect(player, x, y) {
    const radius = 1; // 爆弾の効果範囲
    for (let dy = -radius; dy <= radius; dy++) {
        for (let dx = -radius; dx <= radius; dx++) {
            const newX = x + dx;
            const newY = y + dy;
            if (newX >= 0 && newX < boardWidth && newY >= 0 && newY < boardHeight) {
                player.board[newY][newX] = 0; // ブロックを破壊
            }
        }
    }
    showEffect(player.ctx, x, y, 'Boom!');
}

function applySlowMotionEffect() {
    players.forEach(player => {
        player.dropInterval *= 2; // ゲームスピードを遅くする
        setTimeout(() => {
            player.dropInterval /= 2; // 効果を元に戻す
        }, 5000); // 5秒間持続
    });
}

function applyShieldEffect(player) {
    // 他のプレイヤーからの攻撃を防ぐシールドを付与
    player.shielded = true;
    setTimeout(() => {
        player.shielded = false; // 効果を元に戻す
    }, 5000); // 5秒間持続
}

function applyInvisibleEffect(player) {
    player.ctx.canvas.style.opacity = 0.5; // 透明化
    setTimeout(() => {
        player.ctx.canvas.style.opacity = 1; // 効果を元に戻す
    }, 5000); // 5秒間持続
}

function applyRandomEffect(player) {
    const randomShape = getRandomShape();
    player.currentShape = randomShape;
    player.currentPosition = { x: Math.floor(boardWidth / 2) - 1, y: 0 };
}

function applyHealthEffect(player) {
    const targetPlayer = players.find(p => p !== player && activePlayers[players.indexOf(p)]);
    if (targetPlayer) {
        targetPlayer.score -= 500; // 他のプレイヤーのスコアを減少
        if (targetPlayer.score < 0) targetPlayer.score = 0;
    }
}

function applyBlindEffect(player) {
    const targetPlayer = players.find(p => p !== player && activePlayers[players.indexOf(p)]);
    if (targetPlayer) {
        targetPlayer.ctx.canvas.style.filter = 'blur(5px)'; // 画面をぼかす
        setTimeout(() => {
            targetPlayer.ctx.canvas.style.filter = 'none'; // 効果を元に戻す
        }, 5000); // 5秒間持続
    }
}

function showEffect(ctx, x, y, text) {
    ctx.save();
    ctx.font = '20px Arial';
    ctx.fillStyle = 'yellow';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, x * blockSize + blockSize / 2, y * blockSize + blockSize / 2);
    ctx.restore();
}

gameLoop();
