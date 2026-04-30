import React, { useEffect, useMemo, useState } from 'react';
import { supabase } from '../lib/supabaseClient';
import '../styles/style.css';

interface Product {
  id: string;
  name?: string;
  nombre?: string;
  descripcion?: string;
  price?: number;
  precio?: number;
  aura?: number;
  image?: string;
  image_url?: string;
  is_promo?: boolean;
}

const Shop = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<Product[]>([]);
  const [inventory, setInventory] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [aura, setAura] = useState(0);
  const [lastLootIndex, setLastLootIndex] = useState<number | null>(null);

  const user = {
    nombre: 'Aventurero',
    avatar: '/logo.png',
  };

  const level = Math.floor(aura / 100);
  const auraProgress = Math.min(100, aura % 100);

  const isAdmin = new URLSearchParams(window.location.search).get('admin') === '1';

  const getName = (product: Product) => product.name ?? product.nombre ?? 'Objeto misterioso';
  const getPrice = (product: Product) => product.price ?? product.precio ?? 0;
  const getAura = (product: Product) => product.aura ?? Math.max(5, Math.floor(getPrice(product) / 10));
  const getImage = (product: Product) => product.image ?? product.image_url ?? '/logo.png';

  const playSound = () => {
    const audio = new Audio('/sounds/loot.mp3');
    audio.play().catch(() => null);
  };

  useEffect(() => {
    const fetchProductos = async () => {
      const { data, error } = await supabase
        .from('products')
        .select('*');

      if (error) {
        console.error('Error productos:', error);
      } else {
        setProducts(data ?? []);
      }
      setLoading(false);
    };

    fetchProductos();
  }, []);

  const addToCart = (product: Product) => setCart((prev) => [...prev, product]);

  const removeFromCart = (index: number) => {
    setCart((prev) => prev.filter((_, idx) => idx !== index));
  };

  const addToInventory = (item: Product) => {
    setInventory((prev) => {
      const next = [...prev, item];
      setLastLootIndex(next.length - 1);
      setTimeout(() => setLastLootIndex(null), 450);
      return next;
    });
  };

  const confirmPurchase = () => {
    cart.forEach((item) => addToInventory(item));
    setCart([]);
    playSound();
  };

  const consumeItem = (index: number) => {
    const item = inventory[index];
    if (!item) return;
    setAura((prev) => prev + getAura(item));
    setInventory((prev) => prev.filter((_, i) => i !== index));
    playSound();
  };

  const total = useMemo(() => cart.reduce((acc, item) => acc + getPrice(item), 0), [cart]);

  if (loading) return <div className="shop-loading">Cargando tienda del reino...</div>;

  return (
    <div className="shop-container mmorpg-shop">
      <header className="shop-header panel">
        <div className="shop-user">
          <img className="shop-avatar" src={user.avatar} alt="Avatar" />
          <div>
            <h1 className="shop-title">Mercado Arcano</h1>
            <p className="shop-user-name">{user.nombre}</p>
            <p className="shop-level">Level {level}</p>
          </div>
        </div>

        <div className="shop-aura-wrapper">
          <p className="panel-title">Aura {aura}</p>
          <div className="aura-bar">
            <div className="aura-fill" style={{ width: `${auraProgress}%` }} />
          </div>
          <p className="shop-aura-text">EXP hacia nivel {level + 1}: {aura % 100}/100</p>
        </div>
      </header>

      <div className="shop-main">
        <div className="shop-left">
          <section id="productos-panel" className="panel">
            <h2 className="panel-title">Loot del Mercader</h2>
            <div className="productos-grid">
              {products.map((product) => (
                <div key={product.id} className="producto-item">
                  <img src={getImage(product)} alt={getName(product)} />
                  <p>{getName(product)}</p>
                  <p>${getPrice(product)}</p>
                  <p className="producto-aura">+{getAura(product)} aura</p>
                  <button onClick={() => addToCart(product)} className="boton-agregar">Añadir al carrito</button>
                </div>
              ))}
            </div>
          </section>

          <section id="recompensas-panel" className="panel">
            <h2 className="panel-title">Backpack</h2>
            <div className="inventory-grid">
              {inventory.map((item, i) => (
                <button
                  type="button"
                  className={`inventory-slot ${lastLootIndex === i ? 'loot-animation' : ''}`}
                  key={`${item.id}-${i}`}
                  onClick={() => consumeItem(i)}
                  title={`Consumir ${getName(item)} (+${getAura(item)} aura)`}
                >
                  <img src={getImage(item)} alt={getName(item)} />
                </button>
              ))}
            </div>
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
                  <span>{getName(item)}</span>
                  <span>${getPrice(item)}</span>
                  <button className="remove-item" onClick={() => removeFromCart(idx)}>x</button>
                </li>
              ))}
            </ul>
          )}

          <div className="carrito-footer">
            <p className="carrito-total">Total: ${total}</p>
            <button className="boton-comprar" onClick={confirmPurchase} disabled={cart.length === 0}>Confirmar compra</button>
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
