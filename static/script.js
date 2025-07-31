// --- VARIABLES Y FUNCIONES GLOBALES PARA EL MODAL DE IMAGEN ---
let imageModal; 
function closeImageModal() {
    if (imageModal) { imageModal.classList.add('modal-hidden'); }
}

// --- CÓDIGO DE INICIALIZACIÓN ---
document.addEventListener('DOMContentLoaded', () => {
    actualizarCarrito();
    setupImageModal(); 
    setupExpandableCart();
});

// ========= FUNCIONES DEL CARRITO =========
function agregarAlCarrito(productId) {
    fetch(`/api/agregar/${productId}`, { method: 'POST' }).then(res => res.json()).then(data => actualizarVistaCarrito(data));
}
function quitarDelCarrito(productId) {
    fetch(`/api/quitar/${productId}`, { method: 'POST' }).then(res => res.json()).then(data => actualizarVistaCarrito(data));
}
function actualizarCarrito() {
    fetch('/api/carrito').then(res => res.json()).then(data => actualizarVistaCarrito(data));
}

function actualizarVistaCarrito(data) {
    const carritoLista = document.getElementById('carrito-lista');
    const carritoTotalEl = document.getElementById('carrito-total');
    const comprarBtn = document.getElementById('comprar-btn');
    const carritoListaMobile = document.getElementById('carrito-contenido-mobile');
    const carritoTotalMobile = document.getElementById('carrito-total-mobile');
    const comprarBtnMobile = document.getElementById('comprar-btn-mobile');
    
    if (!carritoLista || !carritoTotalEl || !comprarBtn) return;

    const carrito = data.carrito;
    const productosDetalle = data.productos_detalle;
    const estaVacio = Object.keys(carrito).length === 0;
    const totalFormateado = `$${data.total.toFixed(2)}`;

    carritoTotalEl.textContent = totalFormateado;
    if (carritoTotalMobile) { carritoTotalMobile.textContent = totalFormateado; }

    if (estaVacio) {
        comprarBtn.classList.add('disabled');
        comprarBtn.href = "#";
        if (comprarBtnMobile) { comprarBtnMobile.classList.add('disabled'); }
    } else {
        comprarBtn.classList.remove('disabled');
        comprarBtn.href = "/comprar";
        if (comprarBtnMobile) { comprarBtnMobile.classList.remove('disabled'); }
    }

    carritoLista.innerHTML = '';
    if (carritoListaMobile) carritoListaMobile.innerHTML = '';
    
    if (estaVacio) {
        const mensajeVacio = '<li class="empty-cart-message">Tu inventario está vacío.</li>';
        carritoLista.innerHTML = mensajeVacio;
        if (carritoListaMobile) carritoListaMobile.innerHTML = '<li class="empty-cart-message">Vacío</li>';
    } else {
        for (const productId in carrito) {
            const cantidad = carrito[productId];
            
            // --- ¡LÓGICA CORREGIDA PARA ABREVIAR EL NOMBRE! ---
            let nombreProducto = productosDetalle[productId] ? productosDetalle[productId].nombre : "Item";
            if (nombreProducto.length > 15) {
                nombreProducto = nombreProducto.substring(0, 15) + "...";
            }
            // ------------------------------------------------
            
            const itemHTMLDesktop = `<li><span>${cantidad}x ${nombreProducto}</span><span class="item-controles"><button onclick="quitarDelCarrito('${productId}')">-</button><button onclick="agregarAlCarrito('${productId}')">+</button></span></li>`;
            const itemHTMLMobile = `<li><span>${cantidad}x ${nombreProducto}</span></li>`;
            
            carritoLista.innerHTML += itemHTMLDesktop;
            if (carritoListaMobile) {
                carritoListaMobile.innerHTML += itemHTMLMobile;
            }
        }
    }
}

// ========= FUNCIÓN PARA EL CARRITO EXPANDIBLE EN MÓVIL =========
function setupExpandableCart() {
    const carritoPanel = document.getElementById('carrito-panel');
    const carritoResumen = document.getElementById('carrito-resumen');
    if (!carritoPanel || !carritoResumen) return;
    carritoResumen.addEventListener('click', (event) => {
        if (event.target.closest('.boton-comprar')) return;
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