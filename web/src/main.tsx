import React from 'react';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Home from './pages/Home';
import Shop from './pages/Shop';
import Admin from './pages/Admin';
import EmojiLogin from './pages/EmojiLogin';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import './styles/style.css';

const router = createBrowserRouter([
  { path: '/', element: <Home /> },
  { path: '/shop', element: <Shop /> },
  { path: '/admin', element: <Admin /> },
  { path: '/emoji-login', element: <EmojiLogin /> },
  { path: '/profile', element: <Profile /> },
  { path: '/settings', element: <Settings /> },
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
