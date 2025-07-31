document.addEventListener('DOMContentLoaded', () => {
    // --- Conexión al Servidor ---
    const socket = io();

    const canvas = document.getElementById('game-canvas');
    const messageBox = document.getElementById('message-box');
    const ctx = canvas.getContext('2d');
    canvas.width = 800;
    canvas.height = 600;

    // --- Unirse a la arena al cargar la página ---
    // En una app real, obtendríamos el emoji de la sesión o de algún otro lado
    const myEmoji = '😀'; // Placeholder
    socket.emit('join_arena', { emoji: myEmoji });

    // --- Manejar eventos del servidor ---
    socket.on('waiting_for_opponent', () => {
        messageBox.textContent = 'Esperando a un oponente...';
    });

    socket.on('game_started', (data) => {
        messageBox.style.display = 'none'; // Ocultamos el mensaje
        console.log('¡Partida empezada!', data);
        
        // Inicia el bucle de renderizado del juego
        requestAnimationFrame(gameLoop);
    });

    socket.on('game_state_update', (gameState) => {
        // Esta función recibirá el estado actualizado del juego desde el servidor
        drawGame(gameState);
    });

    // --- Lógica de renderizado ---
    function drawGame(state) {
        // 1. Limpiar el lienzo
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // 2. Dibujar las serpientes de cada jugador
        for (const playerId in state.players) {
            const player = state.players[playerId];
            ctx.fillStyle = (playerId === socket.id) ? 'lime' : 'cyan'; // Diferente color para ti y el oponente
            
            player.snake.forEach(segment => {
                ctx.fillRect(segment.x, segment.y, 20, 20);
            });
        }
    }

    function gameLoop() {
        // En un juego real, aquí es donde se actualizaría el estado y se dibujaría
        // Por ahora, solo es un placeholder
        requestAnimationFrame(gameLoop);
    }

    // --- Enviar inputs del teclado al servidor ---
    document.addEventListener('keydown', (event) => {
        const key = event.key.toLowerCase();
        if (['w', 'a', 's', 'd'].includes(key)) {
            socket.emit('player_input', { key: key });
        }
    });

});