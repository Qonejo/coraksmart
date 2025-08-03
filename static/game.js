// Game.js - Snake PvP Arena
const socket = io();
const canvas = document.getElementById('game-canvas');
const ctx = canvas.getContext('2d');
const messageBox = document.getElementById('message-box');

// Configuración del juego
const CANVAS_WIDTH = 800;
const CANVAS_HEIGHT = 600;
const CELL_SIZE = 20;

canvas.width = CANVAS_WIDTH;
canvas.height = CANVAS_HEIGHT;

// Estado del juego
let gameState = {
    players: {},
    food: null,
    myPlayerId: null,
    gameStarted: false,
    gameOver: false
};

// Colores para jugadores
const playerColors = {
    0: '#00ff00', // Verde
    1: '#ff0000'  // Rojo
};

// Eventos de Socket.IO
socket.on('connect', () => {
    console.log('Conectado al servidor');
    const userEmoji = document.body.dataset.userEmoji || '🎮';
    socket.emit('join_lobby', { emoji: userEmoji });
});

socket.on('waiting_for_opponent', () => {
    messageBox.textContent = 'Esperando oponente...';
    messageBox.style.display = 'block';
});

socket.on('game_started', (data) => {
    console.log('Juego iniciado:', data);
    gameState.players = data.players;
    gameState.food = data.food;
    gameState.gameStarted = true;
    gameState.myPlayerId = socket.id;
    
    messageBox.style.display = 'none';
    startGameLoop();
});

socket.on('game_update', (data) => {
    gameState.players = data.players;
    gameState.food = data.food;
});

socket.on('game_over', (data) => {
    gameState.gameOver = true;
    gameState.players = data.players;
    
    let message = 'Empate!';
    if (data.winner) {
        const winnerPlayer = gameState.players[data.winner];
        if (data.winner === socket.id) {
            message = '¡Ganaste! 🎉';
        } else {
            message = `Perdiste... Ganó ${winnerPlayer.emoji}`;
        }
    }
    
    messageBox.textContent = message;
    messageBox.style.display = 'block';
    
    // Volver al lobby después de 3 segundos
    setTimeout(() => {
        window.location.href = '/lobby';
    }, 3000);
});

socket.on('player_disconnected', () => {
    messageBox.textContent = 'El oponente se desconectó';
    messageBox.style.display = 'block';
    
    setTimeout(() => {
        window.location.href = '/lobby';
    }, 2000);
});

// Control del juego
document.addEventListener('keydown', (event) => {
    if (!gameState.gameStarted || gameState.gameOver) return;
    
    let direction = null;
    
    switch(event.key) {
        case 'ArrowUp':
        case 'w':
        case 'W':
            direction = 'up';
            break;
        case 'ArrowDown':
        case 's':
        case 'S':
            direction = 'down';
            break;
        case 'ArrowLeft':
        case 'a':
        case 'A':
            direction = 'left';
            break;
        case 'ArrowRight':
        case 'd':
        case 'D':
            direction = 'right';
            break;
    }
    
    if (direction) {
        event.preventDefault();
        socket.emit('player_input', { direction: direction });
    }
});

// Renderizado
function drawSnake(snake, color, emoji) {
    // Dibujar cuerpo de la serpiente
    ctx.fillStyle = color;
    snake.forEach((segment, index) => {
        if (index === 0) {
            // Cabeza con emoji
            ctx.fillRect(segment.x, segment.y, CELL_SIZE, CELL_SIZE);
            ctx.fillStyle = 'white';
            ctx.font = `${CELL_SIZE - 4}px Arial`;
            ctx.textAlign = 'center';
            ctx.fillText(emoji, segment.x + CELL_SIZE/2, segment.y + CELL_SIZE - 4);
            ctx.fillStyle = color;
        } else {
            // Cuerpo
            ctx.fillRect(segment.x + 2, segment.y + 2, CELL_SIZE - 4, CELL_SIZE - 4);
        }
    });
}

function drawFood(food) {
    ctx.fillStyle = '#ffff00';
    ctx.fillRect(food.x, food.y, CELL_SIZE, CELL_SIZE);
    
    // Dibujar símbolo de comida
    ctx.fillStyle = 'red';
    ctx.font = `${CELL_SIZE - 4}px Arial`;
    ctx.textAlign = 'center';
    ctx.fillText('🍎', food.x + CELL_SIZE/2, food.y + CELL_SIZE - 4);
}

function drawScore() {
    ctx.fillStyle = 'white';
    ctx.font = '16px "Press Start 2P"';
    ctx.textAlign = 'left';
    
    let y = 30;
    Object.entries(gameState.players).forEach(([playerId, player], index) => {
        const isMe = playerId === socket.id;
        const prefix = isMe ? 'TÚ' : 'RIVAL';
        const status = player.alive ? '' : ' (MUERTO)';
        
        ctx.fillText(`${prefix} ${player.emoji}: ${player.score}${status}`, 10, y);
        y += 25;
    });
}

function drawGrid() {
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1;
    
    // Líneas verticales
    for (let x = 0; x <= CANVAS_WIDTH; x += CELL_SIZE) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, CANVAS_HEIGHT);
        ctx.stroke();
    }
    
    // Líneas horizontales
    for (let y = 0; y <= CANVAS_HEIGHT; y += CELL_SIZE) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(CANVAS_WIDTH, y);
        ctx.stroke();
    }
}

function render() {
    // Limpiar canvas
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    if (!gameState.gameStarted) return;
    
    // Dibujar grid
    drawGrid();
    
    // Dibujar comida
    if (gameState.food) {
        drawFood(gameState.food);
    }
    
    // Dibujar serpientes
    Object.entries(gameState.players).forEach(([playerId, player], index) => {
        const color = playerColors[index] || '#ffffff';
        if (player.snake && player.snake.length > 0) {
            drawSnake(player.snake, color, player.emoji);
        }
    });
    
    // Dibujar puntuación
    drawScore();
}

// Loop del juego
function startGameLoop() {
    function gameLoop() {
        render();
        if (!gameState.gameOver) {
            requestAnimationFrame(gameLoop);
        }
    }
    gameLoop();
}

// Obtener emoji del usuario del DOM
document.addEventListener('DOMContentLoaded', () => {
    // Intentar obtener el emoji del usuario desde la sesión
    fetch('/api/get-emojis')
        .then(response => response.json())
        .then(data => {
            // El emoji se pasará automáticamente cuando se conecte
        });
});

// Inicializar el renderizado
render();
