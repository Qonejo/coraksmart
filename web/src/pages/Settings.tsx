import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const Settings = () => {
  const { signOut, user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await signOut();
    navigate('/'); // Redirect to home after logout
  };

  if (!user) {
    return (
        <div className="bg-black text-white min-h-screen flex flex-col items-center justify-center font-mono text-center">
            <h1 className="text-4xl">No has iniciado sesión.</h1>
        </div>
    );
  }

  return (
    <div className="bg-black text-white min-h-screen flex items-center justify-center font-mono">
      <div className="border-4 border-red-500 bg-gray-900/90 p-8 rounded-lg text-center shadow-[0_0_20px_rgba(255,0,0,0.7)]">
        <h1 className="text-5xl mb-6 text-red-400">⚙️ Configuración</h1>
        <p className="text-gray-300 mb-8">Aquí podrás cambiar tus opciones.</p>
        <button
          onClick={handleLogout}
          className="w-full py-3 font-bold text-white bg-red-600 rounded-md hover:bg-red-500 transition-colors"
        >
          Cerrar Sesión
        </button>
      </div>
    </div>
  );
};

export default Settings;
