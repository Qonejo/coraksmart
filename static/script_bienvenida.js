document.addEventListener('DOMContentLoaded', () => {

    // ========= CÓDIGO PARA LA ANIMACIÓN DE MATRIX CON LETRAS =========
    const canvas = document.getElementById('matrix-canvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        const matrixChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()-_=+[]{}|;:',.<>/?~";
        const fontSize = 16;
        const columns = Math.floor(canvas.width / fontSize);
        const drops = [];
        for (let i = 0; i < columns; i++) {
            drops[i] = 1;
        }
        function draw() {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#0F0';
            ctx.font = `${fontSize}px monospace`;
            for (let i = 0; i < drops.length; i++) {
                const text = matrixChars.charAt(Math.floor(Math.random() * matrixChars.length));
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                    drops[i] = 0;
                }
                drops[i]++;
            }
        }
        const intervalId = setInterval(draw, 33);
        window.addEventListener('resize', () => {
            clearInterval(intervalId);
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            const newColumns = Math.floor(canvas.width / fontSize);
            drops.length = 0;
            for (let i = 0; i < newColumns; i++) {
                drops[i] = 1;
            }
            setInterval(draw, 33);
        });
    }

    // ========= CÓDIGO DEL LOGIN CON EMOJIS =========
    const grid = document.getElementById('emoji-grid');
    const modal = document.getElementById('access-modal');
    const modalTitle = document.getElementById('modal-title');
    const selectedEmojiEl = document.getElementById('selected-emoji');
    const form = document.getElementById('access-form');
    const passwordInput = document.getElementById('password-input');
    const errorMessage = document.getElementById('error-message');
    const closeModalBtn = document.getElementById('close-modal-btn');

    let isOccupied = false;

    function loadEmojis() {
        fetch('/api/get-emojis')
            .then(res => res.json())
            .then(data => {
                if(grid){
                    grid.innerHTML = '';
                    data.all_emojis.forEach(emoji => {
                        const slot = document.createElement('div');
                        slot.classList.add('emoji-slot');
                        slot.textContent = emoji;
                        if (data.occupied_emojis.includes(emoji)) {
                            const icon = document.createElement('span');
                            icon.classList.add('occupied-icon');
                            icon.textContent = '🔒';
                            slot.appendChild(icon);
                        }
                        slot.addEventListener('click', () => openModal(emoji, data.occupied_emojis.includes(emoji)));
                        grid.appendChild(slot);
                    });
                }
            });
    }

    function openModal(emoji, occupied) {
        isOccupied = occupied;
        selectedEmojiEl.textContent = emoji;
        modalTitle.textContent = isOccupied ? 'Acceder con tu Avatar' : 'Registra tu Avatar';
        passwordInput.value = '';
        errorMessage.textContent = '';
        modal.classList.remove('modal-hidden');
        passwordInput.focus();
    }

    function closeModal() {
        modal.classList.add('modal-hidden');
    }

    if(closeModalBtn) {
        closeModalBtn.addEventListener('click', closeModal);
    }

    if(form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const emoji = selectedEmojiEl.textContent;
            const password = passwordInput.value;
            errorMessage.textContent = 'Procesando...';
            fetch('/api/emoji-access', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ emoji, password })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // ¡LÍNEA AÑADIDA AQUÍ!
                    sessionStorage.setItem('user_emoji', emoji);
                    window.location.href = '/';
                } else {
                    errorMessage.textContent = data.message;
                }
            });
        });
    }

    loadEmojis();
});