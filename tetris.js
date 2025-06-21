// ゲームの設定と定数
const blockSize = 32;
const boardWidth = 10;
const boardHeight = 20;
const INPUT_INTERVAL = 180; // 入力の最小間隔(ms)

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
    }

    start() {
        this.currentShape = getRandomShape();
        this.nextShape = getRandomShape();
        this.updateGhostPosition();
        this.lastDropTime = performance.now();
        this.lastCPUMoveTime = performance.now();
        this.draw();
        this.drawNext();
    }

    update(time) {
        if (this.gameOver) return 0;
        
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
        
        // Draw board
        this.board.forEach((row, y) => {
            row.forEach((color, x) => {
                if (color) {
                    this.drawBlock(x, y, color);
                }
            });
        });
        
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
        if (lines <= 0) return;
        
        for (let i = 0; i < lines; i++) {
            this.board.splice(0, 1);
            const obstacleRow = Array(boardWidth).fill('#808080');
            obstacleRow[Math.floor(Math.random() * boardWidth)] = 0; // ランダムな位置に穴を開ける
            this.board.push(obstacleRow);
        }
    }
}