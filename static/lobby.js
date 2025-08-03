// Lobby.js - Palco de Espectadores Interactivo
const socket = io();

// Estado del cliente
let clientState = {
    userEmoji: null,
    isSearching: false,
    connected: false
};

// Elementos del DOM
const elements = {
    searchButton: document.getElementById('search-button'),
    cancelButton: document.getElementById('cancel-button'),
    backButton: document.getElementById('back-button'),
    statusMessage: document.getElementById('status-message'),
    inCombatList: document.getElementById('in-combat-list'),
    searchingList: document.getElementById('searching-list'),
    spectatorsList: document.getElementById('spectators-list')
};

// Obtener emoji del usuario
function getUserEmoji() {
    return document.body.dataset.userEmoji || '🎮';
}

// Mostrar mensaje de estado
function showStatus(message, type = 'info') {
    const statusEl = elements.statusMessage;
    statusEl.textContent = message;
    statusEl.className = `status-message status-${type}`;
    statusEl.style.display = 'block';
    
    // Auto-ocultar después de 5 segundos si no es error
    if (type !== 'error') {
        setTimeout(() => {
            statusEl.style.display = 'none';
        }, 5000);
    }
}

// Formatear puntos de aura
function formatAuraPoints(points) {
    if (points >= 1000000) {
        return `${(points / 1000000).toFixed(1)}M`;
    } else if (points >= 1000) {
        return `${(points / 1000).toFixed(1)}K`;
    }
    return points.toString();
}

// Renderizar lista de combates
function renderInCombat(combatList) {
    const container = elements.inCombatList;
    
    if (!combatList || combatList.length === 0) {
        container.innerHTML = '<div class="empty-list">No hay combates activos</div>';
        return;
    }
    
    const combatHTML = combatList.map(combat => `
        <div class="combat-item">
            <div class="combat-players">
                <span class="player-emoji">${combat.player1.emoji}</span>
                <span class="player-aura">${formatAuraPoints(combat.player1.aura_points)}</span>
            </div>
            <div class="vs-text">VS</div>
            <div class="combat-players">
                <span class="player-emoji">${combat.player2.emoji}</span>
                <span class="player-aura">${formatAuraPoints(combat.player2.aura_points)}</span>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = combatHTML;
}

// Renderizar lista de buscando duelo
function renderSearching(searchingList) {
    const container = elements.searchingList;
    
    if (!searchingList || searchingList.length === 0) {
        container.innerHTML = '<div class="empty-list">Nadie buscando duelo</div>';
        return;
    }
    
    const searchingHTML = searchingList.map(player => {
        const isCurrentUser = player.emoji === clientState.userEmoji;
        const extraClass = isCurrentUser ? ' style="border-color: #ff0; box-shadow: 0 0 10px rgba(255, 255, 0, 0.5);"' : '';
        
        return `
            <div class="player-item"${extraClass}>
                <span class="player-emoji">${player.emoji}</span>
                <span class="player-name">${isCurrentUser ? 'TÚ' : 'Oponente'}</span>
                <span class="player-aura">${formatAuraPoints(player.aura_points)} Aura</span>
            </div>
        `;
    }).join('');
    
    container.innerHTML = searchingHTML;
}

// Renderizar lista de espectadores
function renderSpectators(spectatorsList) {
    const container = elements.spectatorsList;
    
    if (!spectatorsList || spectatorsList.length === 0) {
        container.innerHTML = '<div class="empty-list">No hay espectadores</div>';
        return;
    }
    
    const spectatorsHTML = spectatorsList.map(player => {
        const isCurrentUser = player.emoji === clientState.userEmoji;
        const extraClass = isCurrentUser ? ' style="border-color: #0f0; box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);"' : '';
        
        return `
            <div class="player-item"${extraClass}>
                <span class="player-emoji">${player.emoji}</span>
                <span class="player-name">${isCurrentUser ? 'TÚ' : 'Espectador'}</span>
                <span class="player-aura">${formatAuraPoints(player.aura_points)} Aura</span>
            </div>
        `;
    }).join('');
    
    container.innerHTML = spectatorsHTML;
}

// Actualizar estado de los botones
function updateButtonStates() {
    if (clientState.isSearching) {
        elements.searchButton.style.display = 'none';
        elements.cancelButton.style.display = 'inline-block';
        elements.cancelButton.disabled = false;
    } else {
        elements.searchButton.style.display = 'inline-block';
        elements.searchButton.disabled = !clientState.connected;
        elements.cancelButton.style.display = 'none';
    }
}

// Manejar actualización del estado del lobby
function handleLobbyUpdate(lobbyData) {
    console.log('[LOBBY] Actualizando estado:', lobbyData);
    
    // Renderizar cada sección
    renderInCombat(lobbyData.in_combat);
    renderSearching(lobbyData.searching);
    renderSpectators(lobbyData.spectators);
    
    // Verificar si el usuario está buscando
    const userIsSearching = lobbyData.searching.some(player => player.emoji === clientState.userEmoji);
    clientState.isSearching = userIsSearching;
    
    // Actualizar botones
    updateButtonStates();
    
    // Mostrar estadísticas en consola
    console.log(`[STATS] Combates: ${lobbyData.in_combat.length}, Buscando: ${lobbyData.searching.length}, Espectadores: ${lobbyData.spectators.length}`);
}

// Event Listeners de Socket.IO
socket.on('connect', () => {
    console.log('[SOCKET] Conectado al servidor');
    clientState.connected = true;
    clientState.userEmoji = getUserEmoji();
    
    // Unirse al lobby
    socket.emit('join_lobby', { emoji: clientState.userEmoji });
    
    showStatus('Conectado al lobby', 'success');
    updateButtonStates();
});

socket.on('disconnect', () => {
    console.log('[SOCKET] Desconectado del servidor');
    clientState.connected = false;
    showStatus('Desconectado del servidor', 'error');
    updateButtonStates();
});

socket.on('update_lobby_state', (lobbyData) => {
    handleLobbyUpdate(lobbyData);
});

socket.on('searching_started', () => {
    showStatus('¡Buscando oponente! Espera a que alguien se una...', 'info');
    clientState.isSearching = true;
    updateButtonStates();
});

socket.on('search_cancelled', () => {
    showStatus('Búsqueda cancelada', 'info');
    clientState.isSearching = false;
    updateButtonStates();
});

socket.on('game_started', (gameData) => {
    showStatus('¡Oponente encontrado! Iniciando duelo...', 'success');
    
    // Redirigir a la arena después de 2 segundos
    setTimeout(() => {
        window.location.href = '/arena';
    }, 2000);
});

socket.on('error', (errorData) => {
    console.error('[ERROR]', errorData);
    showStatus(errorData.message || 'Error desconocido', 'error');
});

// Event Listeners de botones
elements.searchButton.addEventListener('click', () => {
    if (!clientState.connected) {
        showStatus('No conectado al servidor', 'error');
        return;
    }
    
    if (clientState.isSearching) {
        showStatus('Ya estás buscando duelo', 'error');
        return;
    }
    
    console.log('[ACTION] Buscando duelo...');
    socket.emit('search_for_game');
    elements.searchButton.disabled = true;
    elements.searchButton.textContent = 'Buscando...';
    
    setTimeout(() => {
        elements.searchButton.textContent = '🗡️ Buscar Duelo';
    }, 2000);
});

elements.cancelButton.addEventListener('click', () => {
    if (!clientState.isSearching) {
        showStatus('No estás buscando duelo', 'error');
        return;
    }
    
    console.log('[ACTION] Cancelando búsqueda...');
    socket.emit('cancel_search');
    elements.cancelButton.disabled = true;
});

// Reconexión automática
socket.on('connect_error', (error) => {
    console.error('[SOCKET] Error de conexión:', error);
    showStatus('Error de conexión. Reintentando...', 'error');
});

socket.on('reconnect', (attemptNumber) => {
    console.log(`[SOCKET] Reconectado después de ${attemptNumber} intentos`);
    showStatus('Reconectado al servidor', 'success');
    
    // Volver a unirse al lobby
    setTimeout(() => {
        socket.emit('join_lobby', { emoji: clientState.userEmoji });
    }, 500);
});

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    console.log('[LOBBY] Lobby inicializado');
    clientState.userEmoji = getUserEmoji();
    updateButtonStates();
    
    // Mostrar emoji del usuario en la interfaz
    const currentUserSpan = document.querySelector('.current-user');
    if (currentUserSpan) {
        currentUserSpan.textContent = clientState.userEmoji;
    }
});

// Manejo de visibilidad de la página
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && clientState.connected) {
        // Refrescar estado cuando la página vuelve a ser visible
        socket.emit('join_lobby', { emoji: clientState.userEmoji });
    }
});

// Heartbeat para mantener conexión
setInterval(() => {
    if (clientState.connected) {
        socket.emit('ping');
    }
}, 45000); // Cada 45 segundos
