import React, { useEffect, useMemo, useState } from 'react';
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

  const user = {
    nombre: 'Aventurero',
    nivel: 12,
    avatar: '/logo.png',
  };

  const auraTotal = useMemo(
    () => cart.reduce((acc, item) => acc + Math.max(5, Math.floor(item.precio / 10)), 0),
    [cart]
  );
  const auraToNextLevel = 500;
  const auraProgress = Math.min(100, Math.round((auraTotal / auraToNextLevel) * 100));

  const isAdmin = new URLSearchParams(window.location.search).get('admin') === '1';

  useEffect(() => {
    const fetchProducts = async () => {
      const { data, error } = await supabase
        .from('products')
        .select('*')
        .eq('is_active', true);
      if (!error && data) {
        setProducts(data);
      }
      setLoading(false);
    };

    fetchProducts();
  }, []);

  const addToCart = (product: Product) => setCart((prev) => [...prev, product]);

  const removeFromCart = (index: number) => {
    setCart((prev) => prev.filter((_, idx) => idx !== index));
  };

  const total = cart.reduce((acc, item) => acc + item.precio, 0);

  if (loading) return <div className="shop-loading">Cargando...</div>;

  return (
    <div className="shop-container">
      <header className="shop-header panel">
        <div className="shop-user">
          <img className="shop-avatar" src={user.avatar} alt="Avatar" />
          <div>
            <h1 className="shop-title">Tienda CorakSmart</h1>
            <p className="shop-user-name">{user.nombre}</p>
            <p className="shop-level">Nivel {user.nivel}</p>
          </div>
        </div>

        <div className="shop-aura-wrapper">
          <p className="panel-title">Aura</p>
          <div className="aura-bar">
            <div className="aura-fill" style={{ width: `${auraProgress}%` }} />
          </div>
          <p className="shop-aura-text">{auraTotal} / {auraToNextLevel}</p>
        </div>
      </header>

      <div className="shop-main">
        <div className="shop-left">
          <section id="productos-panel" className="panel">
            <h2 className="panel-title">Objetos en venta</h2>
            <div className="productos-grid">
              {products.map((product) => {
                const auraReward = Math.max(5, Math.floor(product.precio / 10));
                return (
                  <div key={product.id} className="producto-item">
                    <img src={product.image_url} alt={product.nombre} />
                    <p>{product.nombre}</p>
                    <p>${product.precio}</p>
                    <p className="producto-aura">+{auraReward} aura</p>
                    <button onClick={() => addToCart(product)} className="boton-agregar">Agregar</button>
                  </div>
                );
              })}
            </div>
          </section>

          <section id="recompensas-panel" className="panel">
            <h2 className="panel-title">Recompensas</h2>
            <ul className="rewards-list">
              <li>Bono nivel 5: +50 aura</li>
              <li>Bono nivel 10: Cofre raro</li>
              <li>Desbloqueable: Montura oscura</li>
              <li>Aura acumulada: {auraTotal}</li>
            </ul>
          </section>
        </div>

        <aside id="carrito-panel" className="panel">
          <h2 className="panel-title">Carrito</h2>
          {cart.length === 0 ? (
            <p className="empty-cart-message">Tu carrito está vacío.</p>
          ) : (
            <ul id="carrito-lista">
              {cart.map((item, idx) => (
                <li key={`${item.id}-${idx}`}>
                  <span>{item.nombre}</span>
                  <span>${item.precio}</span>
                  <button className="remove-item" onClick={() => removeFromCart(idx)}>x</button>
                </li>
              ))}
            </ul>
          )}

          <div className="carrito-footer">
            <p className="carrito-total">Total: ${total}</p>
            <button className="boton-comprar">Finalizar compra</button>
          </div>
        </aside>
      </div>

      {isAdmin && (
        <aside id="admin-panel" className="panel">
          <h3 className="panel-title">Admin</h3>
          <div className="admin-actions">
            <button>Agregar producto</button>
            <button>Editar precios</button>
            <button>Ver usuarios</button>
          </div>
        </aside>
      )}
    </div>
  );
};

export default Shop;
