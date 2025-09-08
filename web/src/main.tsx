import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import './index.css'

import Home from './pages/Home'
import Shop from './pages/Shop'
import Admin from './pages/Admin'
import EmojiLogin from './pages/EmojiLogin' // Importar el nuevo componente

const Placeholder = ({ pageName }: { pageName: string }) => (
  <div className="bg-gray-900 text-white min-h-screen flex items-center justify-center font-mono">
    <h1 className="text-4xl">Página de {pageName} (En construcción)</h1>
  </div>
);

const router = createBrowserRouter([
  {
    path: '/',
    element: <Home />,
  },
  {
    path: '/shop',
    element: <Shop />,
  },
  {
    path: '/profile',
    element: <Placeholder pageName="Perfil" />,
  },
  {
    path: '/settings',
    element: <Placeholder pageName="Ajustes" />,
  },
  {
    path: '/admin',
    element: <Admin />,
  },
  {
    path: '/login',
    element: <EmojiLogin />, // Usar el nuevo componente para la ruta /login
  },
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)
