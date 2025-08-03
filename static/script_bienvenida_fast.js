// Script optimizado de bienvenida - Versión rápida
let allEmojis = [];
let occupiedEmojis = [];
let selectedEmoji = null;

// Función optimizada de Matrix (más simple)
function initMatrix() {
    const canvas = document.getElementById('matrix-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const chars = "01";
    const fontSize = 14;
    const columns = canvas.width / fontSize;
    const drops = Array(Math.floor(columns)).fill(1);
    
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
}

// Cargar emojis de forma optimizada
async function loadEmojis() {
    try {
        const response = await fetch('/api/get-emojis');
        const data = await response.json();
        allEmojis = data.all_emojis;
        occupiedEmojis = data.occupied_emojis;
        renderEmojiGrid();
    } catch (error) {
        console.error('Error cargando emojis:', error);
    }
}

// Renderizar grid de emojis
function renderEmojiGrid() {
    const container = document.getElementById('emoji-grid');
    container.innerHTML = '';
    
    // Mostrar solo primeros 24 emojis para carga rápida
    const visibleEmojis = allEmojis.slice(0, 24);
    
    visibleEmojis.forEach(emoji => {
        const div = document.createElement('div');
        div.className = 'emoji-option';
        div.textContent = emoji;
        
        if (occupiedEmojis.includes(emoji)) {
            div.classList.add('occupied');
            div.title = 'Iniciar sesión con este avatar';
        } else {
            div.title = 'Registrarse con este avatar';
        }
        
        div.addEventListener('click', () => selectEmoji(emoji, div));
        
        container.appendChild(div);
    });
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
        showStatus('Selecciona un avatar primero', 'error');
        return;
    }
    
    const password = document.getElementById('password-input').value.trim();
    if (!password) {
        showStatus('Ingresa una contraseña', 'error');
        return;
    }
    
    const button = document.getElementById('login-button');
    button.disabled = true;
    button.textContent = 'Entrando...';
    
    try {
        const response = await fetch('/api/emoji-access', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emoji: selectedEmoji, password: password })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showStatus('¡Acceso concedido! Redirigiendo...', 'success');
            setTimeout(() => window.location.href = '/', 1000);
        } else {
            showStatus(result.message || 'Error de acceso', 'error');
            button.disabled = false;
            button.textContent = 'Entrar';
        }
    } catch (error) {
        showStatus('Error de conexión', 'error');
        button.disabled = false;
        button.textContent = 'Entrar';
    }
}

// Mostrar mensaje de estado
function showStatus(message, type) {
    const statusEl = document.getElementById('status-message');
    statusEl.textContent = message;
    statusEl.className = type;
    statusEl.style.display = 'block';
    
    if (type === 'error') {
        setTimeout(() => statusEl.style.display = 'none', 3000);
    }
}

// Inicialización rápida
document.addEventListener('DOMContentLoaded', () => {
    initMatrix();
    loadEmojis();
    
    // Event listeners
    document.getElementById('access-form').addEventListener('submit', (e) => {
        e.preventDefault();
        attemptLogin();
    });
    document.getElementById('close-modal-btn').addEventListener('click', closeModal);
});

// CSS adicional para elementos seleccionados
const style = document.createElement('style');
style.textContent = `
    .emoji-option.selected { 
        background: rgba(0,255,0,0.5) !important; 
        box-shadow: 0 0 10px #0f0; 
    }
    .emoji-option.occupied:before {
        content: "🔒 ";
        font-size: 0.8em;
    }
    .modal-hidden { display: none !important; }
    #access-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }
    .modal-content {
        background: #111;
        border: 2px solid #0f0;
        padding: 30px;
        border-radius: 10px;
        text-align: center;
        max-width: 400px;
        width: 90%;
    }
    .modal-emoji {
        font-size: 3rem;
        margin: 10px 0;
    }
    .success { color: #0f0; }
    .error { color: #f00; }
`;
document.head.appendChild(style);
