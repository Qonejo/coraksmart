import React, { useEffect, useState } from 'react';
import { supabase } from '../lib/supabaseClient';

interface Product {
  id: string;
  nombre: string;
  descripcion: string;
  precio: number;
  stock: number;
  image_url?: string;
  is_active?: boolean;
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

      const { data, error } = await supabase
        .from('products')
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

  const handleCheckout = async () => {
    if (cart.length === 0) {
      setError('⚠️ Tu carrito está vacío.');
      return;
    }

    setSaving(true);
    setError(null);

    // Crear un nuevo pedido en la tabla "orders"
    const { data: order, error: orderError } = await supabase
      .from('orders')
      .insert({
        status: 'pending',
        total: cart.reduce((sum, item) => sum + item.precio, 0),
      })
      .select()
      .single();

    if (orderError) {
      console.error('Error creando orden:', orderError);
      setError('❌ No se pudo crear la orden.');
      setSaving(false);
      return;
    }

    // Insertar cada producto del carrito en una tabla "order_items"
    const orderItems = cart.map((item) => ({
      order_id: order.id,
      product_id: item.id,
      quantity: 1,
      price: item.precio,
    }));

    const { error: itemsError } = await supabase.from('order_items').insert(orderItems);

    if (itemsError) {
      console.error('Error guardando productos de la orden:', itemsError);
      setError('❌ No se pudieron guardar los productos en la orden.');
      setSaving(false);
      return;
    }

    // Resetear carrito tras compra exitosa
    setCart([]);
    alert('✅ ¡Tu compra fue registrada con éxito!');
    setSaving(false);
  };

  if (loading) {
    return <div className="p-4 text-green-400">Cargando productos...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500">{error}</div>;
  }

  return (
    <div className="min-h-screen bg-black text-green-300 p-6 font-mono">
      <h1 className="text-3xl font-bold text-green-400 mb-6">🛒 Tienda CorakSmart</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {products.map((product) => (
          <div
            key={product.id}
            className="bg-gray-900 border-2 border-green-400 p-4 rounded-lg shadow-[0_0_15px_rgba(0,255,0,0.6)]"
          >
            {product.image_url && (
              <img
                src={product.image_url}
                alt={product.nombre}
                className="w-full h-40 object-cover rounded mb-3"
              />
            )}
            <h2 className="text-xl font-bold">{product.nombre}</h2>
            <p className="text-sm text-green-400">{product.descripcion}</p>
            <p className="font-bold mt-2 text-green-300">${product.precio.toFixed(2)}</p>
            <p className="text-sm text-gray-400">Stock: {product.stock}</p>

            <button
              onClick={() => addToCart(product)}
              className="mt-3 w-full py-2 bg-green-400 text-black font-bold rounded hover:bg-green-300 transition-colors"
            >
              ➕ Agregar al carrito
            </button>
          </div>
        ))}
      </div>

      {/* Carrito */}
      <div className="mt-10 p-6 bg-gray-900 border-2 border-pink-500 rounded-lg">
        <h2 className="text-2xl font-bold text-pink-400">🛍️ Carrito</h2>
        {cart.length === 0 ? (
          <p className="text-gray-400">Tu carrito está vacío.</p>
        ) : (
          <>
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

            <button
              onClick={handleCheckout}
              disabled={saving}
              className="mt-6 w-full py-3 font-bold bg-pink-500 text-black rounded hover:bg-pink-400 transition-colors disabled:bg-gray-500"
            >
              {saving ? 'Guardando...' : '✅ Finalizar Compra'}
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default Shop;
