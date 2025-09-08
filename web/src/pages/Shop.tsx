import React, { useEffect, useState } from 'react';
import { supabase } from '../lib/supabaseClient';

interface Product {
  id: string;
  nombre: string;
  descripcion: string;
  precio: number;
  image_url: string;
}

interface CartItem extends Product {
  quantity: number;
}

const Shop = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<Record<string, CartItem>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      const { data, error } = await supabase
        .from('products')
        .select('*')
        .eq('is_active', true);

      if (error) {
        setError(error.message);
      } else {
        setProducts(data);
      }
      setLoading(false);
    };

    fetchProducts();
  }, []);

  const addToCart = (product: Product) => {
    setCart(prevCart => {
      const existingItem = prevCart[product.id];
      if (existingItem) {
        return { ...prevCart, [product.id]: { ...existingItem, quantity: existingItem.quantity + 1 } };
      }
      return { ...prevCart, [product.id]: { ...product, quantity: 1 } };
    });
  };

  const totalItems = Object.values(cart).reduce((sum, item) => sum + item.quantity, 0);

  if (loading) {
    return <div className="bg-black text-green-400 min-h-screen flex items-center justify-center font-mono">Cargando productos...</div>;
  }

  if (error) {
    return <div className="bg-black text-red-500 min-h-screen flex items-center justify-center font-mono">Error: {error}</div>;
  }

  return (
    <div className="bg-black text-white min-h-screen font-mono p-4 sm:p-8">
      <header className="flex justify-between items-center mb-8 border-b-2 border-green-400 pb-4">
        <h1 className="text-4xl text-green-400">🛒 Tienda</h1>
        <div className="text-2xl text-yellow-400">
          Carrito: {totalItems} item(s)
        </div>
      </header>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {products.map(product => (
          <div key={product.id} className="bg-gray-900 border-2 border-gray-700 rounded-lg p-4 flex flex-col justify-between hover:border-green-400 transition-colors">
            <img src={product.image_url} alt={product.nombre} className="w-full h-48 object-cover mb-4 rounded" />
            <div>
              <h2 className="text-xl text-green-400 mb-2">{product.nombre}</h2>
              <p className="text-gray-400 text-sm mb-4">{product.descripcion}</p>
              <p className="text-2xl text-yellow-400 mb-4">
                ${product.precio.toLocaleString('es-MX')}
              </p>
              <button
                onClick={() => addToCart(product)}
                className="w-full py-2 font-bold text-gray-900 bg-green-400 rounded-md hover:bg-green-300 transition-colors"
              >
                Agregar al Carrito
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Shop;
