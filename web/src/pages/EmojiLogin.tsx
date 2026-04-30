import React, { useEffect, useState } from 'react';
import MatrixBackground from '../components/MatrixBackground';
import { supabase } from '../lib/supabaseClient';

const EMOJI_AVATARS = ['😀', '🚀', '👻', '🌵', '🎮', '💎', '👽', '💀', '🤖', '🦊', '🐱', '🐼'];

const EmojiLogin = () => {
  const [emojis, setEmojis] = useState<string[]>([]);
  const [selectedEmoji, setSelectedEmoji] = useState<string | null>(null);
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setEmojis(EMOJI_AVATARS);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!selectedEmoji) {
      setError('Por favor, selecciona un emoji.');
      return;
    }

    if (!password.trim()) {
      setError('Por favor, ingresa tu contraseña.');
      return;
    }

    setLoading(true);

    try {
      const { data, error: queryError } = await supabase
        .from('users')
        .select('*')
        .eq('emoji', selectedEmoji)
        .eq('password', password)
        .single();

      if (queryError) {
        if (queryError.code === 'PGRST116') {
          setError('Usuario no encontrado');
        } else {
          const isConnectionError = /Failed to fetch|NetworkError|ERR_NAME_NOT_RESOLVED/i.test(queryError.message || '');
          if (isConnectionError) {
            setError('Error al conectar con la base de datos');
          } else {
            setError(queryError.message || 'Error desconocido en el login.');
          }
        }
        return;
      }

      if (!data) {
        setError('Usuario no encontrado');
        return;
      }

      setSuccess('Login exitoso');
    } catch (unexpectedError) {
      const message = unexpectedError instanceof Error ? unexpectedError.message : 'Error inesperado en el login.';
      const isConnectionError = /Failed to fetch|NetworkError|ERR_NAME_NOT_RESOLVED/i.test(message);
      setError(isConnectionError ? 'Error al conectar con la base de datos' : message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full h-screen overflow-hidden">
      <MatrixBackground />

      <div className="login-container">
        <h1 className="matrix-title text-3xl mb-4">⚡ CorakSmart ⚡</h1>

        <form onSubmit={handleSubmit}>
          <div className="emoji-grid">
            {emojis.map((emoji) => (
              <button
                key={emoji}
                type="button"
                onClick={() => setSelectedEmoji(emoji)}
                className={selectedEmoji === emoji ? 'selected' : ''}
              >
                {emoji}
              </button>
            ))}
          </div>

          <div className="input-section">
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="CONTRASEÑA"
              className="w-full px-4 py-2 text-center bg-gray-800 border-2 border-gray-600 rounded-md text-green-300 focus:outline-none focus:border-green-400"
            />
          </div>

          {error && <p className="text-red-500 mt-3">{error}</p>}
          {success && <p className="text-green-400 mt-3">{success}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-4 py-2 bg-green-500 text-black font-bold rounded-md hover:bg-green-400 transition-colors disabled:bg-gray-600"
          >
            {loading ? 'ACCEDIENDO...' : 'ENTRAR'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default EmojiLogin;
