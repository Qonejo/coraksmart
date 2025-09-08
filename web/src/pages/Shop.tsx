import React, { useEffect, useState } from "react";
import { supabase } from "../lib/supabaseClient";

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
        .from("product") // 👈 nombre correcto de la tabla
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

  if (loading) return <div className="p-4 text-green-400">Cargando productos...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;

  return (
    <div className="min-h-screen bg-black text-green-300 p-6 font-mono">
      <h1 className="text-3xl font-bold text-green-400 mb-6">🛒 Tienda CorakSmart</h1>

      {/* --- Sección Promociones (Dorado) --- */}
      <h2 className="text-2xl font-bold text-yellow-400 mb-4">✨ Promociones</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        {products
          .filter((p) => p.is_promo)
          .map((product) => (
            <div
              key={product.id}
              className="bg-gray-900 border-4 border-yellow-400 p-4 rounded-lg shadow-[0_0_15px_rgba(255,215,0,0.8)]"
            >
              {product.image_url && (
                <img
                  src={product.image_url}
                  alt={product.nombre}
                  className="w-full h-40 object-cover rounded mb-3"
                />
              )}
              <h2 className="text-xl font-bold text-yellow-300">{product.nombre}</h2>
              <p className="text-sm text-yellow-200">{product.descripcion}</p>
              <p className="font-bold mt-2 text-yellow-400">${product.precio.toFixed(2)}</p>
              <p className="text-sm text-gray-400">Stock: {product.stock}</p>

              <button
                onClick={() => addToCart(product)}
                className="mt-3 w-full py-2 bg-yellow-400 text-black font-bold rounded hover:bg-yellow-300 transition-colors"
              >
                ➕ Agregar al carrito
              </button>
            </div>
          ))}
      </div>

      {/* --- Sección Productos Normales (Azules) --- */}
      <h2 className="text-2xl font-bold text-blue-400 mb-4">🛍️ Objetos en venta</h2>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {products
          .filter((p) => !p.is_promo)
          .map((product) => (
            <div
              key={product.id}
              className="bg-gray-900 border-2 border-blue-400 p-4 rounded-lg shadow-[0_0_10px_rgba(0,0,255,0.6)]"
            >
              {product.image_url && (
                <img
                  src={product.image_url}
                  alt={product.nombre}
                  className="w-full h-40 object-cover rounded mb-3"
                />
              )}
              <h2 className="text-lg font-bold text-blue-300">{product.nombre}</h2>
              <p className="text-sm text-blue-200">{product.descripcion}</p>
              <p className="font-bold mt-2 text-blue-400">${product.precio.toFixed(2)}</p>
              <p className="text-sm text-gray-400">Stock: {product.stock}</p>

              <button
                onClick={() => addToCart(product)}
                className="mt-3 w-full py-2 bg-blue-400 text-black font-bold rounded hover:bg-blue-300 transition-colors"
              >
                ➕ Agregar al carrito
              </button>
            </div>
          ))}
      </div>

      {/* --- Carrito --- */}
      <div className="mt-10 p-6 bg-gray-900 border-2 border-pink-500 rounded-lg">
        <h2 className="text-2xl font-bold text-pink-400">🛍️ Carrito</h2>
        {cart.length === 0 ? (
          <p className="text-gray-400">Tu carrito está vacío.</p>
        ) : (
          <ul className="mt-4 space-y-2">
            {cart.map((item, index) => (
              <li
                key={index}
                className="flex justify-between items-center border-b border-green-700 pb-1"
              >
                <span>{item.nombre}</span>
                <span>${item.precio.toFixed(2)}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default Shop;
