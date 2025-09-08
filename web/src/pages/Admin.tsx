import React, { useState } from 'react';

const Admin = () => {
  const [productName, setProductName] = useState('');
  const [price, setPrice] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('');

    // This is a placeholder for the API call.
    // In a real app, you would use fetch or axios to send this data.
    try {
      const response = await fetch('/api/admin/products-create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: productName, price: parseFloat(price) }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const result = await response.json();
      setMessage(`Success: ${JSON.stringify(result)}`);
      setProductName('');
      setPrice('');
    } catch (error: any) {
      setMessage(`Error: ${error.message}`);
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Admin - Create Product</h1>
      <form onSubmit={handleSubmit} className="max-w-md">
        <div className="mb-4">
          <label className="block mb-1">Product Name</label>
          <input
            type="text"
            className="w-full border p-2 rounded"
            value={productName}
            onChange={(e) => setProductName(e.target.value)}
            required
          />
        </div>
        <div className="mb-4">
          <label className="block mb-1">Price</label>
          <input
            type="number"
            className="w-full border p-2 rounded"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="bg-blue-500 text-white p-2 rounded">
          Create Product
        </button>
        {message && <p className="mt-4">{message}</p>}
      </form>
    </div>
  );
};

export default Admin;
