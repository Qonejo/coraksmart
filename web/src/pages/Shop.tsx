import React, { useEffect, useState } from 'react';
import { supabase } from '../lib/supabaseClient';
import '../styles/style.css';

interface Product {
  id: string;
  nombre: string;
  descripcion: string;
  precio: number;
  image_url: string;
  is_promo?: boolean;
}

const Shop = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProducts = async () => {
      const { data, error } = await supabase.from('products').select('*').eq('is_active', true);
      if (!error && data) setProducts(data);
      setLoading(false);
    };
    fetchProducts();
  }, []);

  const addToCart = (product: Product) => setCart([...cart, product]);

  if (loading) return <div className="p-6 text-green-400">Cargando...</div>;

  return (
    <div className="rpg-container">
      <header>
        <img id="logo" src="/logo.png" alt="logo" />
        <h1 style={{ color: '#33ff33' }}>Tienda CorakSmart</h1>
      </header>

      <div id="productos-panel">
        <h2>Objetos en venta</h2>
        <div className="productos-grid">
          {products.filter(p => !p.is_promo).map(product => (
            <div key={product.id} className="producto-item border-blue-400">
              <img src={product.image_url} alt={product.nombre} />
              <div className="producto-nombre">{product.nombre}</div>
              <div className="producto-precio">${product.precio}</div>
              <button onClick={() => addToCart(product)} className="boton-agregar">➕ Agregar</button>
            </div>
          ))}
        </div>

        <h2>Promociones</h2>
        <div className="productos-grid">
          {products.filter(p => p.is_promo).map(product => (
            <div key={product.id} className="producto-item border-yellow-400 promo-item">
              <img src={product.image_url} alt={product.nombre} />
              <div className="producto-nombre">{product.nombre}</div>
              <div className="producto-precio promo-precio">${product.precio}</div>
              <button onClick={() => addToCart(product)} className="boton-agregar">⚡ Añadir Promo</button>
            </div>
          ))}
        </div>
      </div>

      <div id="carrito-panel">
        <h2>🛍️ Carrito</h2>
        <div id="carrito-contenido">
          {cart.length === 0 ? <p className="empty-cart-message">Tu carrito está vacío.</p> : (
            <ul id="carrito-lista">
              {cart.map((item, idx) => (
                <li key={idx}>{item.nombre} – ${item.precio}</li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
};

export default Shop;
