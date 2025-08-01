document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const canvas = document.getElementById('game-canvas');
    const messageBox = document.getElementById('message-box');
    
    if (!canvas) return; // Si no hay canvas, no hacemos nada

    const ctx = canvas.getContext('2d');
    canvas.width = 800;
    canvas.height = 600;

    let gameState = {}; // Aquí guardaremos el estado del juego que nos envíe el servidor

    // --- Unirse a la arena al cargar la página ---
    const userEmoji = sessionStorage.getItem('user_emoji') || '❓'; // Obtenemos el emoji guardado
    socket.emit('join_arena', { emoji: userEmoji });

    // --- Manejar eventos del servidor ---
    socket.on('waiting_for_opponent', () => {
        messageBox.textContent = 'Esperando Oponente...';
    });

    socket.on('game_started', (data) => {
        messageBox.style.display = 'none';
        console.log('¡Partida empezada!', data);
        // Empezamos a escuchar los eventos del teclado
        listenToKeys();
    });

    socket.on('game_state_update', (state) => {
        gameState = state; // Actualizamos nuestro estado local con el del servidor
    });

    socket.on('game_over', (data) => {
        alert(`¡El ganador es ${data.winner}! Ha ganado ${data.points_won} puntos de Aura.`);
        window.location.href = '/perfil';
    });

    // --- Lógica de renderizado y de envío de inputs ---
    function listenToKeys() {
        document.addEventListener('keydown', (event) => {
            const key = event.key.toLowerCase();
            if (['w', 'a', 's', 'd'].includes(key)) {
                socket.emit('player_input', { key: key });
            }
        });
    }

    function draw() {
        // Limpiar el lienzo
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Dibujar a los jugadores
        if (gameState.players) {
            for (const playerId in gameState.players) {
                const player = gameState.players[playerId];
                ctx.fillStyle = (playerId === socket.id) ? 'lime' : 'cyan';
                
                player.snake.forEach(segment => {
                    ctx.fillRect(segment.x, segment.y, 20, 20);
                });
            }
        }
    }

    // Bucle principal del juego
    function gameLoop() {
        draw();
        requestAnimationFrame(gameLoop);
    }
    
    // Iniciar el bucle de renderizado
    gameLoop();
});