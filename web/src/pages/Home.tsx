import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
  const menuOptions = [
    { to: '/shop', emoji: '🛒', text: 'Tienda' },
    { to: '/profile', emoji: '👤', text: 'Perfil' },
    { to: '/settings', emoji: '⚙️', text: 'Ajustes' },
  ];

  return (
    <div className="bg-gray-900 text-white font-mono flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-5xl mb-12 text-yellow-400 tracking-widest">CorakSmart</h1>
      <nav className="flex gap-12">
        {menuOptions.map((option) => (
          <Link
            key={option.to}
            to={option.to}
            className="flex flex-col items-center gap-4 text-gray-400 hover:text-white hover:scale-110 transition-transform duration-300"
          >
            <span className="text-7xl">{option.emoji}</span>
            <span className="text-xl tracking-wider">{option.text}</span>
          </Link>
        ))}
      </nav>
    </div>
  );
};

export default Home;
