import React, { useEffect, useState } from 'react';
import { supabase } from '../lib/supabaseClient';

const Shop = () => {
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      const { data, error } = await supabase
        .from('products')
        .select('*');

      if (error) {
        console.error('Error fetching products:', error);
      } else {
        setProducts(data);
      }
      setLoading(false);
    };

    fetchProducts();
  }, []);

  if (loading) {
    return <div className="p-4">Loading products...</div>;
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Shop</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {products.map(product => (
          <div key={product.id} className="border p-4 rounded">
            <h2 className="text-xl font-semibold">{product.nombre}</h2>
            <p>{product.descripcion}</p>
            <p className="font-bold mt-2">${product.precio}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Shop;
