import React, { useEffect, useState } from "react";
import { supabase } from "../lib/supabaseClient";
import "../styles/style.css"; // 👈 importamos tu CSS RPG

interface Product {
  id: string;
  nombre: string;
  descripcion: string;
  precio: number;
  stock: number;
  image_url?: string;
  is_active?: boolean;
  is_promo?: boolean;
}

const Shop = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cart, setCart] = useState<Product[]>([]);

  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      setError(null);

      const { data, error } = await supabase
        .from("product") // 👈 tu tabla real
        .select("*")
        .eq("is_active", true);

      if (error) {
        console.error("Error fetching products:", error);
        setError("❌ No se pudieron cargar los productos.");
      } else {
        setProducts(data || []);
      }

      setLoading(false);
    };

    fetchProducts();
  }, []);

  const addToCart = (product: Product) => {
    setCart([...cart, product]);
  };

  if (loading) return <div className="p-4">Cargando...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;

  return (
    <div className="rpg-container">
      {/* Header RPG */}
      <header>
        <img id="logo" src="/logo.png" alt="logo" />
        <div className="header-user-info">
          <div className="perfil-link">
            <span className="perfil-emoji-header">🙂</span>
            <span>Nivel 1 – 100 pts de aura</span>
          </div>
        </div>
      </header>

      {/* Panel de productos */}
      <div id="productos-panel">
        <h2>Objetos en venta</h2>
        <div className="productos-grid">
          {products
            .filter((p) => !p.is_promo)
            .map((product) => (
              <div key={product.id} className="producto-item">
                {product.image_url && (
                  <img src={product.image_url} alt={product.nombre} />
                )}
                <div className="producto-nombre">{product.nombre}</div>
                <div className="producto-precio">${product.precio}</div>
                <button
                  className="boton-agregar"
                  onClick={() => addToCart(product)}
                >
                  ➕ Agregar
                </button>
              </div>
            ))}
        </div>

        <h2>Promociones</h2>
        <div className="productos-grid">
          {products
            .filter((p) => p.is_promo)
            .map((product) => (
              <div key={product.id} className="producto-item promo-item">
                {product.image_url && (
                  <img src={product.image_url} alt={product.nombre} />
                )}
                <div className="producto-nombre">{product.nombre}</div>
                <div className="producto-precio promo-precio">
                  ${product.precio}
                </div>
                <button
                  className="boton-agregar"
                  onClick={() => addToCart(product)}
                >
                  ⚡ Añadir Promo
                </button>
              </div>
            ))}
        </div>
      </div>

      {/* Panel del carrito RPG */}
      <div id="carrito-panel">
        <h2>🛍️ Carrito</h2>
        <div id="carrito-contenido">
          {cart.length === 0 ? (
            <p className="empty-cart-message">Tu carrito está vacío.</p>
          ) : (
            <ul id="carrito-lista">
              {cart.map((item, idx) => (
                <li key={idx}>
                  {item.nombre} – ${item.precio}
                </li>
              ))}
            </ul>
          )}
        </div>
        <div id="carrito-resumen">
          <div className="total-line">
            <span>TOTAL</span>
            <span>
              $
              {cart.reduce((sum, item) => sum + item.precio, 0).toFixed(2)}
            </span>
          </div>
          <button className="boton-comprar">Finalizar compra</button>
        </div>
      </div>
    </div>
  );
};

export default Shop;
