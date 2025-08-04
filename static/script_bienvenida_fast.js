// Script optimizado de bienvenida - Versión rápida
let allEmojis = [];
let occupiedEmojis = [];
let selectedEmoji = null;

// Función optimizada de Matrix (más simple)
function initMatrix() {
    const canvas = document.getElementById('matrix-canvas');
    if (!canvas) {
        console.error('No se encontró el canvas matrix-canvas');
        return;
    }
    
    console.log('Iniciando animación Matrix...');
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン";
    const fontSize = 14;
    const columns = Math.floor(canvas.width / fontSize);
    const drops = Array(columns).fill(1);
    
    function draw() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = '#0f0';
        ctx.font = fontSize + 'px monospace';
        
        for (let i = 0; i < drops.length; i++) {
            const text = chars[Math.floor(Math.random() * chars.length)];
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);
            
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }
    }
    
    setInterval(draw, 33); // ~30 FPS
    console.log('Matrix animación iniciada');
}

// Cargar emojis de forma optimizada
async function loadEmojis() {
    try {
        console.log('Cargando emojis...');
        const response = await fetch('/api/get-emojis');
        const data = await response.json();
        allEmojis = data.all_emojis;
        occupiedEmojis = data.occupied_emojis;
        console.log('Emojis cargados:', allEmojis.length, 'total,', occupiedEmojis.length, 'ocupados');
        renderEmojiGrid();
    } catch (error) {
        console.error('Error cargando emojis:', error);
    }
}

// Renderizar grid de emojis
function renderEmojiGrid() {
    const container = document.getElementById('emoji-grid');
    if (!container) {
        console.error('No se encontró el contenedor emoji-grid');
        return;
    }
    
    container.innerHTML = '';
    
    // Mostrar todos los emojis para mejor UX
    const visibleEmojis = allEmojis;
    console.log('Renderizando', visibleEmojis.length, 'emojis');
    
    visibleEmojis.forEach(emoji => {
        const div = document.createElement('div');
        div.className = 'emoji-option';
        
        if (occupiedEmojis.includes(emoji)) {
            div.classList.add('occupied');
            div.innerHTML = `${emoji}<span class="occupied-icon">🔒</span>`;
            div.title = 'Iniciar sesión con este avatar';
        } else {
            div.textContent = emoji;
            div.title = 'Registrarse con este avatar';
        }
        
        div.addEventListener('click', () => selectEmoji(emoji, div));
        
        container.appendChild(div);
    });
    
    console.log('Grid renderizado con', container.children.length, 'elementos');
}

// Seleccionar emoji (permitir tanto ocupados como libres)
function selectEmoji(emoji, element) {
    // Remover selección anterior
    document.querySelectorAll('.emoji-option.selected').forEach(el => {
        el.classList.remove('selected');
    });
    
    selectedEmoji = emoji;
    element.classList.add('selected');
    
    // Mostrar modal
    showAccessModal(emoji);
}

// Mostrar modal de acceso
function showAccessModal(emoji) {
    const modal = document.getElementById('access-modal');
    const selectedEmojiEl = document.getElementById('selected-emoji');
    const modalTitle = document.getElementById('modal-title');
    const passwordInput = document.getElementById('password-input');
    
    selectedEmojiEl.textContent = emoji;
    
    if (occupiedEmojis.includes(emoji)) {
        modalTitle.textContent = 'Iniciar Sesión';
        passwordInput.placeholder = 'Introduce tu contraseña';
    } else {
        modalTitle.textContent = 'Crear Nueva Cuenta';
        passwordInput.placeholder = 'Crea una contraseña nueva';
    }
    
    modal.classList.remove('modal-hidden');
    passwordInput.value = '';
    passwordInput.focus();
}

// Cerrar modal
function closeModal() {
    document.getElementById('access-modal').classList.add('modal-hidden');
    document.getElementById('error-message').textContent = '';
    selectedEmoji = null;
}

// Login optimizado
async function attemptLogin() {
    if (!selectedEmoji) {
        showError('Selecciona un avatar primero');
        return;
    }
    
    const password = document.getElementById('password-input').value.trim();
    if (!password) {
        showError('Ingresa una contraseña');
        return;
    }
    
    const button = document.querySelector('#access-form button[type="submit"]');
    const originalText = button.textContent;
    button.disabled = true;
    button.textContent = 'Entrando...';
    
    console.log('Intentando login con emoji:', selectedEmoji);
    
    try {
        const response = await fetch('/api/emoji-access', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emoji: selectedEmoji, password: password })
        });
        
        const result = await response.json();
        console.log('Respuesta del servidor:', result);
        
        if (result.success) {
            showError('¡Acceso concedido! Redirigiendo...', 'success');
            closeModal();
            setTimeout(() => {
                console.log('Redirigiendo a /');
                window.location.href = '/';
            }, 1500);
        } else {
            showError(result.message || 'Error de acceso');
            button.disabled = false;
            button.textContent = originalText;
        }
    } catch (error) {
        console.error('Error en attemptLogin:', error);
        showError('Error de conexión');
        button.disabled = false;
        button.textContent = originalText;
    }
}

// Mostrar mensaje de estado en el modal y/o página principal
function showError(message, type = 'error') {
    // Mostrar en el modal si está abierto
    const errorEl = document.getElementById('error-message');
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.className = type === 'success' ? 'success' : 'error';
        errorEl.style.display = 'block';
        
        if (type === 'error') {
            setTimeout(() => errorEl.style.display = 'none', 3000);
        }
    }
    
    // También mostrar en la página principal para mensajes de éxito
    if (type === 'success') {
        const statusEl = document.getElementById('status-message');
        if (statusEl) {
            statusEl.textContent = message;
            statusEl.className = 'success';
            statusEl.style.display = 'block';
        }
    }
    
    console.log('Mensaje mostrado:', message, type);
}

// Mostrar mensaje de estado (función legacy)
function showStatus(message, type) {
    showError(message, type);
}

// Inicialización rápida
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM cargado, iniciando...');
    
    // Inicializar Matrix después de un pequeño delay
    setTimeout(() => {
        initMatrix();
        console.log('Matrix iniciado');
    }, 100);
    
    // Cargar emojis
    loadEmojis();
    
    // Event listeners
    const form = document.getElementById('access-form');
    const closeBtn = document.getElementById('close-modal-btn');
    
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            attemptLogin();
        });
    }
    
    if (closeBtn) {
        closeBtn.addEventListener('click', closeModal);
    }
});

// CSS adicional para elementos seleccionados
const style = document.createElement('style');
style.textContent = `
    .emoji-option.selected { 
        border-color: #ffcc00 !important; 
        transform: scale(1.2) !important; 
        box-shadow: 0 0 15px #ffcc00; 
    }
    .occupied-icon {
        position: absolute;
        bottom: 2px;
        right: 2px;
        font-size: 0.4em;
        color: #ff3333;
        font-family: 'Segoe UI Emoji', 'Apple Color Emoji', sans-serif;
    }
    .modal-hidden { display: none !important; }
    #access-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 100;
    }
    .modal-content {
        background: #111;
        padding: 30px;
        border: 4px solid #fff;
        text-align: center;
        font-family: 'Press Start 2P', cursive;
    }
    .modal-emoji {
        font-size: 4em;
        margin-bottom: 15px;
    }
    #access-form input {
        font-family: inherit;
        font-size: 1em;
        padding: 10px;
        border: 2px solid #888;
        background-color: #333;
        color: #fff;
        text-align: center;
        width: 80%;
    }
    #access-form button, #close-modal-btn {
        font-family: inherit;
        font-size: 0.9em;
        padding: 10px 20px;
        margin-top: 20px;
        border: none;
        cursor: pointer;
    }
    #access-form button {
        background-color: #ffcc00;
        color: #000;
    }
    #close-modal-btn {
        background-color: #555;
        color: #fff;
        margin-left: 10px;
    }
    .success { color: #0f0; }
    .error { color: #ff3333; }
`;
document.head.appendChild(style);
