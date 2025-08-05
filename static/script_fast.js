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
    
    // Limpiar elementos de galería dinámicos
    const galleryCounter = document.getElementById('gallery-counter');
    const prevBtn = document.getElementById('gallery-prev');
    const nextBtn = document.getElementById('gallery-next');
    
    if (galleryCounter) galleryCounter.style.display = 'none';
    if (prevBtn) prevBtn.style.display = 'none';
    if (nextBtn) nextBtn.style.display = 'none';
    
    // Resetear variables de galería
    currentGalleryProduct = '';
    currentGalleryIndex = 0;
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
        // Forzar posicionamiento en móvil
        function enforceFixedPosition() {
            if (window.innerWidth <= 850) {
                carritoPanel.style.position = 'fixed';
                carritoPanel.style.bottom = '0';
                carritoPanel.style.left = '0';
                carritoPanel.style.right = '0';
                carritoPanel.style.zIndex = '9999';
                carritoPanel.style.width = '100vw';
                
                carritoResumen.style.position = 'absolute';
                carritoResumen.style.bottom = '0';
                carritoResumen.style.left = '0';
                carritoResumen.style.right = '0';
                carritoResumen.style.zIndex = '10000';
            }
        }
        
        // Aplicar al cargar
        enforceFixedPosition();
        
        carritoResumen.addEventListener('click', (e) => {
            // Solo en móvil (ancho menor a 850px)
            if (window.innerWidth <= 850) {
                // No hacer toggle si se clickeó el botón de comprar
                if (!e.target.matches('.boton-comprar') && !e.target.closest('.boton-comprar')) {
                    carritoPanel.classList.toggle('expanded');
                    console.log('Carrito móvil toggled');
                    enforceFixedPosition(); // Re-aplicar posicionamiento
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
        
        // Manejar cambios de orientación/tamaño de pantalla
        window.addEventListener('resize', () => {
            if (window.innerWidth > 850) {
                carritoPanel.classList.remove('expanded');
            } else {
                enforceFixedPosition(); // Re-aplicar en móvil
            }
        });
        
        // Listener adicional para scroll (algunos navegadores móviles)
        window.addEventListener('scroll', () => {
            if (window.innerWidth <= 850) {
                enforceFixedPosition();
            }
        });
        
        // Listener para cuando la página regana foco (cambio de tab)
        window.addEventListener('focus', () => {
            if (window.innerWidth <= 850) {
                enforceFixedPosition();
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

// Sistema de galería de productos
let productGalleries = {};
let currentGalleryProduct = '';
let currentGalleryIndex = 0;

function setProductGallery(productId, images) {
    productGalleries[productId] = images;
}

function openProductGallery(productId, imageIndex = 0) {
    if (!productGalleries[productId]) {
        // Si no hay galería definida, usar solo la imagen principal
        const productImg = document.querySelector(`[onclick*="${productId}"] img, img[onclick*="${productId}"]`);
        if (productImg) {
            abrirImagenModal(productImg.src, productImg.alt);
        }
        return;
    }
    
    currentGalleryProduct = productId;
    currentGalleryIndex = imageIndex;
    
    const images = productGalleries[productId];
    if (images && images[imageIndex]) {
        showGalleryImage();
        setupGalleryModal();
    }
}

function showGalleryImage() {
    const images = productGalleries[currentGalleryProduct];
    const modalImage = document.getElementById('modal-image');
    const modal = document.getElementById('image-modal');
    
    if (images && images[currentGalleryIndex]) {
        modalImage.src = '/static/' + images[currentGalleryIndex];
        modal.classList.remove('modal-hidden');
        modal.classList.add('modal-visible');
        currentModal = modal;
        updateGalleryInfo();
        
        // Cerrar con ESC
        document.addEventListener('keydown', cerrarModalConESC);
    }
}

function updateGalleryInfo() {
    const images = productGalleries[currentGalleryProduct];
    const totalImages = images ? images.length : 1;
    
    let galleryCounter = document.getElementById('gallery-counter');
    if (!galleryCounter) {
        galleryCounter = document.createElement('div');
        galleryCounter.id = 'gallery-counter';
        galleryCounter.style.cssText = `
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 5px 15px;
            border-radius: 15px;
            font-family: 'Press Start 2P', cursive;
            font-size: 10px;
            z-index: 10001;
        `;
        document.getElementById('image-modal').appendChild(galleryCounter);
    }
    
    galleryCounter.textContent = `${currentGalleryIndex + 1} / ${totalImages}`;
    galleryCounter.style.display = totalImages > 1 ? 'block' : 'none';
}

function setupGalleryModal() {
    const modal = document.getElementById('image-modal');
    const images = productGalleries[currentGalleryProduct];
    
    if (!images || images.length <= 1) return;
    
    let prevBtn = document.getElementById('gallery-prev');
    let nextBtn = document.getElementById('gallery-next');
    
    if (!prevBtn) {
        prevBtn = document.createElement('button');
        prevBtn.id = 'gallery-prev';
        prevBtn.innerHTML = '‹';
        prevBtn.style.cssText = `
            position: absolute;
            left: 20px;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(0, 0, 0, 0.7);
            color: white;
            border: none;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            font-size: 24px;
            cursor: pointer;
            z-index: 10001;
            font-family: Arial, sans-serif;
        `;
        prevBtn.addEventListener('click', prevGalleryImage);
        modal.appendChild(prevBtn);
    }
    
    if (!nextBtn) {
        nextBtn = document.createElement('button');
        nextBtn.id = 'gallery-next';
        nextBtn.innerHTML = '›';
        nextBtn.style.cssText = `
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(0, 0, 0, 0.7);
            color: white;
            border: none;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            font-size: 24px;
            cursor: pointer;
            z-index: 10001;
            font-family: Arial, sans-serif;
        `;
        nextBtn.addEventListener('click', nextGalleryImage);
        modal.appendChild(nextBtn);
    }
    
    prevBtn.style.display = 'block';
    nextBtn.style.display = 'block';
}

function prevGalleryImage() {
    const images = productGalleries[currentGalleryProduct];
    if (images && images.length > 1) {
        currentGalleryIndex = (currentGalleryIndex - 1 + images.length) % images.length;
        showGalleryImage();
    }
}

function nextGalleryImage() {
    const images = productGalleries[currentGalleryProduct];
    if (images && images.length > 1) {
        currentGalleryIndex = (currentGalleryIndex + 1) % images.length;
        showGalleryImage();
    }
}

// Navegación con teclado para galería
document.addEventListener('keydown', function(e) {
    const modal = document.getElementById('image-modal');
    if (!modal.classList.contains('modal-hidden') && currentGalleryProduct) {
        if (e.key === 'ArrowLeft') {
            e.preventDefault();
            prevGalleryImage();
        } else if (e.key === 'ArrowRight') {
            e.preventDefault();
            nextGalleryImage();
        }
    }
});

// Exponer funciones globalmente (necesario para onclick en HTML)
window.agregarAlCarrito = agregarAlCarrito;
window.quitarDelCarrito = quitarDelCarrito;
window.abrirImagenModal = abrirImagenModal;
window.cerrarImagenModal = cerrarImagenModal;
window.openProductGallery = openProductGallery;
window.setProductGallery = setProductGallery;
