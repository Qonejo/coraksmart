import React, { useEffect, useState } from 'react';
import { supabase } from '../lib/supabaseClient';

interface Product {
  id: string;
  nombre: string;
  descripcion: string;
  precio: number;
  stock: number;
  image?: string;
  is_active?: boolean;
  is_promo?: boolean; // 👈 nueva columna en DB
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
        .from('product')
        .select('*')
        .eq('is_active', true);

      if (error) {
        console.error('Error fetching products:', error);
        setError('❌ No se pudieron cargar los productos.');
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

  const promos = products.filter(p => p.is_promo);
  const normales = products.filter(p => !p.is_promo);

  return (
    <div className="min-h-screen bg-black text-green-300 p-6 font-mono">
      <header className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-green-400">🛒 CorakSmart</h1>
        <div className="text-right">
          <p className="text-yellow-400 font-bold">Nivel 1</p>
          <p className="text-red-400">100 pts de Aura</p>
        </div>
      </header>

      {/* Sección promociones */}
      <section className="mb-10">
        <h2 className="text-center text-green-400 text-2xl font-bold mb-4">🔥 Promociones 🔥</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {promos.map(product => (
            <div
              key={product.id}
              className="bg-gray-900 border-4 border-yellow-400 p-4 rounded-lg shadow-lg text-center"
            >
              {product.image && (
                <img
                  src={`/${product.image}`}
                  alt={product.nombre}
                  className="w-24 h-24 mx-auto mb-2 object-contain"
                />
              )}
              <h3 className="text-yellow-300 font-bold">{product.nombre}</h3>
              <p className="text-sm">{product.descripcion}</p>
              <p className="font-bold text-green-400">${product.precio.toFixed(2)}</p>
              <button
                onClick={() => addToCart(product)}
                className="mt-2 w-full py-2 bg-yellow-400 text-black font-bold rounded hover:bg-yellow-300"
              >
                ➕ Agregar
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Sección productos normales */}
      <section>
        <h2 className="text-center text-green-400 text-2xl font-bold mb-4">Objetos en venta</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {normales.map(product => (
            <div
              key={product.id}
              className="bg-gray-900 border-4 border-blue-400 p-4 rounded-lg shadow-lg text-center"
            >
              {product.image && (
                <img
                  src={`/${product.image}`}
                  alt={product.nombre}
                  className="w-24 h-24 mx-auto mb-2 object-contain"
                />
              )}
              <h3 className="text-blue-300 font-bold">{product.nombre}</h3>
              <p className="text-sm">{product.descripcion}</p>
              <p className="font-bold text-green-400">${product.precio.toFixed(2)}</p>
              <button
                onClick={() => addToCart(product)}
                className="mt-2 w-full py-2 bg-blue-400 text-black font-bold rounded hover:bg-blue-300"
              >
                ➕ Agregar
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Carrito */}
      <aside className="mt-10 p-6 bg-gray-900 border-2 border-pink-500 rounded-lg">
        <h2 className="text-2xl font-bold text-pink-400">🛍️ Carrito</h2>
        {cart.length === 0 ? (
          <p className="text-gray-400">Tu carrito está vacío.</p>
        ) : (
          <ul className="mt-4 space-y-2">
            {cart.map((item, idx) => (
              <li key={idx} className="flex justify-between items-center">
                <span>{item.nombre}</span>
                <span>${item.precio.toFixed(2)}</span>
              </li>
            ))}
          </ul>
        )}
      </aside>
    </div>
  );
};

export default Shop;
