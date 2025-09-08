import React, { useEffect, useState } from "react";
import { supabase } from "../lib/supabaseClient";

interface Product {
  id: string;
  nombre: string;
  descripcion: string;
  precio: number;
  stock: number;
  image?: string; // ej: gomita.png en public/
}

const Shop = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cart, setCart] = useState<Product[]>([]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      setError(null);

      const { data, error } = await supabase.from("product").select("*");

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

  const handleCheckout = async () => {
    if (cart.length === 0) {
      setError("⚠️ Tu carrito está vacío.");
      return;
    }

    setSaving(true);
    setError(null);

    // Crear orden en tabla orders
    const { data: order, error: orderError } = await supabase
      .from("orders")
      .insert({
        status: "pending",
        total: cart.reduce((sum, item) => sum + item.precio, 0),
      })
      .select()
      .single();

    if (orderError) {
      console.error("Error creando orden:", orderError);
      setError("❌ No se pudo crear la orden.");
      setSaving(false);
      return;
    }

    // Insertar items en order_items
    const orderItems = cart.map((item) => ({
      order_id: order.id,
      product_id: item.id,
      quantity: 1,
      price: item.precio,
    }));

    const { error: itemsError } = await supabase
      .from("order_items")
      .insert(orderItems);

    if (itemsError) {
      console.error("Error guardando productos de la orden:", itemsError);
      setError("❌ No se pudieron guardar los productos en la orden.");
      setSaving(false);
      return;
    }

    setCart([]);
    alert("✅ ¡Tu compra fue registrada con éxito!");
    setSaving(false);
  };

  if (loading) {
    return <div className="p-4 text-green-400">Cargando productos...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500">{error}</div>;
  }

  return (
    <div className="rpg-container">
      {/* Panel de Productos */}
      <div id="productos-panel">
        <h2>Productos</h2>
        <div className="productos-grid">
          {products.map((product) => (
            <div key={product.id} className="producto-item">
              {product.image && (
                <img
                  src={`/${product.image}`} // desde public/
                  alt={product.nombre}
                  className="producto-imagen"
                />
              )}
              <div className="producto-nombre">{product.nombre}</div>
              <div className="producto-precio">${product.precio}</div>
              <div
                className={`producto-stock ${
                  product.stock > 0 ? "" : "stock-agotado"
                }`}
              >
                Stock: {product.stock}
              </div>
              <button
                onClick={() => addToCart(product)}
                disabled={product.stock === 0}
                className="boton-agregar"
              >
                ➕ Agregar
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Panel del Carrito */}
      <div id="carrito-panel">
        <h2>Carrito</h2>
        <div id="carrito-contenido">
          {cart.length === 0 ? (
            <p className="empty-cart-message">Tu carrito está vacío.</p>
          ) : (
            <ul id="carrito-lista">
              {cart.map((item, index) => (
                <li key={index}>
                  {item.nombre} — ${item.precio}
                </li>
              ))}
            </ul>
          )}
        </div>
        <div id="carrito-resumen">
          <div className="total-line">
            <span>Total:</span>
            <span id="carrito-total">
              ${cart.reduce((sum, i) => sum + i.precio, 0)}
            </span>
          </div>
          <button
            onClick={handleCheckout}
            disabled={saving}
            className={`boton-comprar ${cart.length === 0 ? "disabled" : ""}`}
          >
            {saving ? "Guardando..." : "Comprar"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Shop;
