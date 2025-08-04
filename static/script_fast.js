// Script optimizado de la página principal
let carrito = {};
let productosDetalle = {};

// Cache para evitar recálculos
let carritoCache = null;
let lastUpdate = 0;

// Funciones de carrito optimizadas - GLOBALES
window.agregarAlCarrito = async function(productId) {
    try {
        const response = await fetch(`/api/agregar/${productId}`, { method: 'POST' });
        const data = await response.json();
        actualizarCarrito(data);
    } catch (error) {
        console.error('Error al agregar producto:', error);
    }
}

window.quitarDelCarrito = async function(productId) {
    try {
        const response = await fetch(`/api/quitar/${productId}`, { method: 'POST' });
        const data = await response.json();
        actualizarCarrito(data);
    } catch (error) {
        console.error('Error al quitar producto:', error);
    }
}

window.limpiarCarrito = async function() {
    try {
        const response = await fetch('/api/limpiar', { method: 'POST' });
        const data = await response.json();
        actualizarCarrito(data);
    } catch (error) {
        console.error('Error al limpiar carrito:', error);
    }
}

// Actualizar carrito de forma eficiente
function actualizarCarrito(data) {
    carrito = data.carrito;
    productosDetalle = data.productos_detalle;
    
    // Solo actualizar DOM si hay cambios reales
    const now = Date.now();
    if (now - lastUpdate < 50) return; // Throttle de 50ms
    lastUpdate = now;
    
    const carritoElement = document.getElementById('carrito-lista');
    const totalElement = document.getElementById('carrito-total');
    const btnComprar = document.getElementById('comprar-btn');
    
    if (!carritoElement || !totalElement || !btnComprar) return;
    
    // Limpiar carrito
    carritoElement.innerHTML = '';
    
    let total = 0;
    let itemCount = 0;
    
    // Construir HTML del carrito de forma eficiente
    const itemsHTML = [];
    
    for (const [productId, cantidad] of Object.entries(carrito)) {
        const producto = productosDetalle[productId];
        if (!producto) continue;
        
        const subtotal = producto.precio * cantidad;
        total += subtotal;
        itemCount += cantidad;
        
        itemsHTML.push(`
            <li class="carrito-item">
                <div class="item-info">
                    <span class="item-nombre">${producto.nombre}</span>
                    <span class="item-precio">$${producto.precio.toFixed(2)}</span>
                </div>
                <div class="item-controles">
                    <button onclick="quitarDelCarrito('${productId}')" class="btn-cantidad">-</button>
                    <span class="cantidad">${cantidad}</span>
                    <button onclick="agregarAlCarrito('${productId}')" class="btn-cantidad">+</button>
                </div>
                <div class="item-subtotal">$${subtotal.toFixed(2)}</div>
            </li>
        `);
    }
    
    // Actualizar DOM de una vez
    if (itemsHTML.length > 0) {
        carritoElement.innerHTML = itemsHTML.join('');
    } else {
        carritoElement.innerHTML = '<li class="empty-cart-message">Tu inventario está vacío.</li>';
    }
    
    totalElement.textContent = `$${total.toFixed(2)}`;
    
    // Actualizar botón de compra
    if (itemCount > 0) {
        btnComprar.classList.remove('disabled');
        btnComprar.textContent = `FINALIZAR COMPRA`;
    } else {
        btnComprar.classList.add('disabled');
        btnComprar.textContent = 'FINALIZAR COMPRA';
    }
}

// Cargar estado inicial del carrito
async function cargarCarrito() {
    try {
        const response = await fetch('/api/carrito');
        const data = await response.json();
        actualizarCarrito(data);
    } catch (error) {
        console.error('Error al cargar carrito:', error);
    }
}

// Modal de imagen optimizado
let currentModal = null;

window.abrirImagenModal = function(imageSrc, title) {
    if (currentModal) return; // Evitar múltiples modales
    
    const modal = document.getElementById('image-modal');
    const modalImg = document.getElementById('modal-image');
    
    if (!modal || !modalImg) return;
    
    modalImg.src = imageSrc;
    modalImg.alt = title;
    modal.classList.remove('modal-hidden');
    modal.classList.add('modal-visible');
    currentModal = modal;
    
    // Cerrar con ESC
    document.addEventListener('keydown', cerrarModalConESC);
}

window.cerrarImagenModal = function() {
    if (!currentModal) return;
    
    currentModal.classList.remove('modal-visible');
    currentModal.classList.add('modal-hidden');
    currentModal = null;
    
    document.removeEventListener('keydown', cerrarModalConESC);
}

function cerrarModalConESC(e) {
    if (e.key === 'Escape') {
        cerrarImagenModal();
    }
}

// Event listeners optimizados
function initEventListeners() {
    // Delegación de eventos para botones de agregar/quitar
    document.addEventListener('click', (e) => {
        if (e.target.matches('.btn-agregar')) {
            e.preventDefault();
            const productId = e.target.dataset.productId;
            if (productId) agregarAlCarrito(productId);
        }
        
        if (e.target.matches('.btn-cantidad')) {
            e.preventDefault();
            // Estos ya tienen onclick definido
        }
        
        if (e.target.matches('.producto-imagen')) {
            e.preventDefault();
            const src = e.target.src;
            const title = e.target.alt;
            abrirImagenModal(src, title);
        }
        
        if (e.target.id === 'close-modal' || e.target === currentModal) {
            cerrarImagenModal();
        }
    });
    
    // Limpiar carrito
    const btnLimpiar = document.getElementById('limpiar-carrito');
    if (btnLimpiar) {
        btnLimpiar.addEventListener('click', limpiarCarrito);
    }
    
    // Toggle del carrito móvil
    initMobileCartToggle();
}

// Función para el carrito móvil desplegable
function initMobileCartToggle() {
    const carritoPanel = document.getElementById('carrito-panel');
    const carritoResumen = document.getElementById('carrito-resumen');
    
    if (carritoPanel && carritoResumen) {
        carritoResumen.addEventListener('click', (e) => {
            // Solo en móvil (ancho menor a 850px)
            if (window.innerWidth <= 850) {
                // No hacer toggle si se clickeó el botón de comprar
                if (!e.target.matches('.boton-comprar')) {
                    carritoPanel.classList.toggle('expanded');
                    console.log('Carrito móvil toggled');
                }
            }
        });
        
        // Cerrar carrito si se toca fuera de él en móvil
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 850 && carritoPanel.classList.contains('expanded')) {
                if (!carritoPanel.contains(e.target)) {
                    carritoPanel.classList.remove('expanded');
                }
            }
        });
    }
}

// Lazy loading para imágenes
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px 0px'
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback para navegadores sin IntersectionObserver
        images.forEach(img => {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });
    }
}

// Inicialización rápida
document.addEventListener('DOMContentLoaded', () => {
    cargarCarrito();
    initEventListeners();
    initLazyLoading();
    
    // Mostrar progreso de carga de aura
    const progressBars = document.querySelectorAll('.aura-progress-fill');
    progressBars.forEach(bar => {
        const progress = bar.dataset.progress;
        if (progress) {
            setTimeout(() => {
                bar.style.width = `${Math.min(progress, 100)}%`;
            }, 100);
        }
    });
});

// Exponer funciones globalmente (necesario para onclick en HTML)
window.agregarAlCarrito = agregarAlCarrito;
window.quitarDelCarrito = quitarDelCarrito;
window.abrirImagenModal = abrirImagenModal;
window.cerrarImagenModal = cerrarImagenModal;
