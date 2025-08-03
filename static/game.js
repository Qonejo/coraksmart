// Game.js - Snake PvP Arena - Optimizado para carga rápida
const socket = io();
const canvas = document.getElementById('game-canvas');
const ctx = canvas.getContext('2d');
const messageBox = document.getElementById('message-box');

// Configuración optimizada del juego
const CANVAS_WIDTH = 600;  // Reducido para mejor rendimiento
const CANVAS_HEIGHT = 400; // Reducido para mejor rendimiento
const CELL_SIZE = 15;      // Reducido para menos cálculos

canvas.width = CANVAS_WIDTH;
canvas.height = CANVAS_HEIGHT;

// Optimizar contexto para mejor rendimiento
ctx.imageSmoothingEnabled = false;
ctx.textBaseline = 'middle';
ctx.textAlign = 'center';

// Estado del juego simplificado
let gameState = {
    players: {},
    food: null,
    myPlayerId: null,
    gameStarted: false,
    gameOver: false,
    lastUpdate: 0
};

// Colores optimizados (sin transparencias)
const COLORS = {
    BACKGROUND: '#000',
    GRID: '#111',
    PLAYER1: '#0f0',
    PLAYER2: '#f00',
    FOOD: '#ff0',
    TEXT: '#fff'
};

// Eventos de Socket.IO
socket.on('connect', () => {
    console.log('Conectado a la arena');
    // En la arena no necesitamos unirse al lobby
    messageBox.textContent = 'Conectado. Esperando oponente...';
    messageBox.style.display = 'block';
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
    // Actualizar solo lo que cambió para mejor rendimiento
    if (data.players) gameState.players = data.players;
    if (data.food) gameState.food = data.food;
});

socket.on('game_over', (data) => {
    gameState.gameOver = true;
    gameState.players = data.players;
    
    let message = 'Empate!';
    if (data.winner) {
        const winnerPlayer = gameState.players[data.winner];
        if (data.winner === socket.id) {
            message = '¡Ganaste! 🎉 Volviendo al lobby...';
        } else {
            message = `Perdiste... Ganó ${winnerPlayer.emoji} 😢 Volviendo al lobby...`;
        }
    } else {
        message = 'Empate! Volviendo al lobby...';
    }
    
    messageBox.textContent = message;
    messageBox.style.display = 'block';
    
    // Volver al lobby después de 4 segundos
    setTimeout(() => {
        window.location.href = '/lobby';
    }, 4000);
});

socket.on('player_disconnected', () => {
    messageBox.textContent = 'El oponente se desconectó';
    messageBox.style.display = 'block';
    
    setTimeout(() => {
        window.location.href = '/lobby';
    }, 2000);
});

// Control optimizado del juego con limitación de input
let lastInputTime = 0;
const INPUT_DELAY = 100; // 100ms entre inputs para evitar spam

document.addEventListener('keydown', (event) => {
    if (!gameState.gameStarted || gameState.gameOver) return;
    
    const now = performance.now();
    if (now - lastInputTime < INPUT_DELAY) return; // Limitar frecuencia de input
    
    let direction = null;
    const key = event.key.toLowerCase();
    
    // Optimizar detección de teclas
    if (key === 'arrowup' || key === 'w') direction = 'up';
    else if (key === 'arrowdown' || key === 's') direction = 'down';
    else if (key === 'arrowleft' || key === 'a') direction = 'left';
    else if (key === 'arrowright' || key === 'd') direction = 'right';
    
    if (direction) {
        event.preventDefault();
        socket.emit('player_input', { direction: direction });
        lastInputTime = now;
    }
});

// Renderizado optimizado
function drawSnake(snake, color, emoji) {
    ctx.fillStyle = color;
    // Dibujar todo el cuerpo de una vez
    snake.forEach((segment, index) => {
        if (index === 0) {
            // Cabeza más grande
            ctx.fillRect(segment.x, segment.y, CELL_SIZE, CELL_SIZE);
            // Emoji simplificado en la cabeza
            ctx.fillStyle = COLORS.TEXT;
            ctx.fillText(emoji, segment.x + CELL_SIZE/2, segment.y + CELL_SIZE/2);
            ctx.fillStyle = color;
        } else {
            // Cuerpo más pequeño para diferencia visual
            ctx.fillRect(segment.x + 1, segment.y + 1, CELL_SIZE - 2, CELL_SIZE - 2);
        }
    });
}

function drawFood(food) {
    ctx.fillStyle = COLORS.FOOD;
    ctx.fillRect(food.x, food.y, CELL_SIZE, CELL_SIZE);
    // Punto en el centro para indicar comida
    ctx.fillStyle = COLORS.BACKGROUND;
    const center = CELL_SIZE / 3;
    ctx.fillRect(food.x + center, food.y + center, center, center);
}

// Contador de FPS para optimización
let frameCount = 0;
let lastFpsUpdate = 0;
let currentFPS = 0;

function drawUI() {
    ctx.fillStyle = COLORS.TEXT;
    ctx.font = '12px "Press Start 2P", monospace';
    
    let y = 20;
    Object.entries(gameState.players).forEach(([playerId, player], index) => {
        const isMe = playerId === socket.id;
        const prefix = isMe ? 'TU' : 'VS';
        const status = player.alive ? '' : ' X';
        
        ctx.fillText(`${prefix} ${player.emoji}: ${player.score}${status}`, 10, y);
        y += 20;
    });
    
    // Mostrar FPS en desarrollo
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        ctx.font = '8px "Press Start 2P", monospace';
        ctx.fillText(`FPS: ${currentFPS}`, CANVAS_WIDTH - 60, 15);
    }
}

// Grid simplificado - solo bordes
function drawBorders() {
    ctx.strokeStyle = COLORS.GRID;
    ctx.lineWidth = 2;
    ctx.strokeRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
}

function render() {
    // Calcular FPS
    frameCount++;
    const now = performance.now();
    if (now - lastFpsUpdate > 1000) {
        currentFPS = Math.round(frameCount * 1000 / (now - lastFpsUpdate));
        frameCount = 0;
        lastFpsUpdate = now;
    }
    
    // Solo renderizar si hay cambios
    if (now - gameState.lastUpdate < 16) return; // ~60 FPS máximo
    gameState.lastUpdate = now;
    
    // Limpiar canvas de manera eficiente
    ctx.fillStyle = COLORS.BACKGROUND;
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    if (!gameState.gameStarted) return;
    
    // Dibujar bordes
    drawBorders();
    
    // Dibujar comida
    if (gameState.food) {
        drawFood(gameState.food);
    }
    
    // Dibujar serpientes con colores alternos
    const colors = [COLORS.PLAYER1, COLORS.PLAYER2];
    Object.entries(gameState.players).forEach(([playerId, player], index) => {
        const color = colors[index] || COLORS.TEXT;
        if (player.snake && player.snake.length > 0) {
            drawSnake(player.snake, color, player.emoji);
        }
    });
    
    // Dibujar UI
    drawUI();
}

// Loop optimizado del juego
function startGameLoop() {
    let animationId;
    
    function gameLoop() {
        render();
        if (!gameState.gameOver) {
            animationId = requestAnimationFrame(gameLoop);
        }
    }
    
    // Iniciar loop
    gameLoop();
    
    // Función para detener el loop si es necesario
    return () => cancelAnimationFrame(animationId);
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
