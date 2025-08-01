// --- VARIABLES Y FUNCIONES GLOBALES PARA EL MODAL DE IMAGEN ---
let imageModal; 

function closeImageModal() {
    if (imageModal) {
        imageModal.classList.add('modal-hidden');
    }
}
// -----------------------------------------------------------

// --- CÓDIGO DE INICIALIZACIÓN ---
// Se ejecuta cuando la página está completamente cargada.
document.addEventListener('DOMContentLoaded', () => {
    actualizarCarrito();
    setupImageModal(); 
    setupExpandableCart();
    setupProgressBars(); // ¡Llamada a la nueva función para las barras de progreso!
});
// --------------------------------

// ========= FUNCIONES DEL CARRITO =========
function agregarAlCarrito(productId) {
    fetch(`/api/agregar/${productId}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            actualizarVistaCarrito(data);
        });
}

function quitarDelCarrito(productId) {
    fetch(`/api/quitar/${productId}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            actualizarVistaCarrito(data);
        });
}

function actualizarCarrito() {
    fetch('/api/carrito')
        .then(response => response.json())
        .then(data => {
            actualizarVistaCarrito(data);
        });
}

function actualizarVistaCarrito(data) {
    const carritoLista = document.getElementById('carrito-lista');
    const carritoTotalEl = document.getElementById('carrito-total');
    const comprarBtn = document.getElementById('comprar-btn');
    
    if(!carritoLista || !carritoTotalEl || !comprarBtn) return;

    const carrito = data.carrito;
    const productosDetalle = data.productos_detalle;
    const estaVacio = Object.keys(carrito).length === 0;
    const totalFormateado = `$${data.total.toFixed(2)}`;

    carritoTotalEl.textContent = totalFormateado;

    if (estaVacio) {
        comprarBtn.classList.add('disabled');
        comprarBtn.href = "#";
    } else {
        comprarBtn.classList.remove('disabled');
        comprarBtn.href = "/comprar";
    }

    carritoLista.innerHTML = '';
    
    if (estaVacio) {
        carritoLista.innerHTML = '<li class="empty-cart-message">Tu inventario está vacío.</li>';
    } else {
        for (const productId in carrito) {
            const cantidad = carrito[productId];
            
            let nombreProducto = productosDetalle[productId] ? productosDetalle[productId].nombre : "Item";
            if (nombreProducto.length > 15) {
                nombreProducto = nombreProducto.substring(0, 15) + "...";
            }
            
            const itemHTMLDesktop = `<li><span>${cantidad}x ${nombreProducto}</span><span class="item-controles"><button onclick="quitarDelCarrito('${productId}')">-</button><button onclick="agregarAlCarrito('${productId}')">+</button></span></li>`;
            
            carritoLista.innerHTML += itemHTMLDesktop;
        }
    }
}

// ========= FUNCIÓN PARA EL CARRITO EXPANDIBLE EN MÓVIL =========
function setupExpandableCart() {
    const carritoPanel = document.getElementById('carrito-panel');
    const carritoResumen = document.getElementById('carrito-resumen');

    if (!carritoPanel || !carritoResumen) {
        return;
    }
    
    carritoResumen.addEventListener('click', (event) => {
        if (event.target.closest('.boton-comprar')) {
            return;
        }
        carritoPanel.classList.toggle('expanded');
    });
}

// ========= FUNCIÓN PARA CONFIGURAR EL MODAL DE IMAGEN =========
function setupImageModal() {
    imageModal = document.getElementById('image-modal');
    if (!imageModal) return;

    const modalImage = document.getElementById('modal-image');
    const productImages = document.querySelectorAll('.producto-item img');

    productImages.forEach(image => {
        image.addEventListener('click', function(event) {
            event.stopPropagation();
            imageModal.classList.remove('modal-hidden');
            modalImage.src = this.src;
        });
    });

    imageModal.addEventListener('click', function(event) {
        if (event.target === imageModal) {
            closeImageModal();
        }
    });

    document.addEventListener('keydown', function(event) {
        if (event.key === "Escape") {
            closeImageModal();
        }
    });
}

// ========= ¡NUEVA FUNCIÓN PARA LAS BARRAS DE PROGRESO! =========
function setupProgressBars() {
    // Busca todas las barras de progreso en la página
    const progressBars = document.querySelectorAll('.aura-progress-fill');
    
    progressBars.forEach(bar => {
        // Lee el porcentaje desde el atributo 'data-progress'
        const progress = bar.dataset.progress;
        
        // Aplica el ancho usando JavaScript
        if (progress) {
            bar.style.width = progress + '%';
        }
    });
}
