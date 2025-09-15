import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MatrixBackground from '../components/MatrixBackground';
import { supabase } from '../lib/supabaseClient';

const Home = () => {
  const navigate = useNavigate();
  const [selectedEmoji, setSelectedEmoji] = useState<string | null>(null);
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const EMOJI_AVATARS = ['😀', '🐱', '🦊', '🐼', '🐸', '👾', '🦁', '🐰'];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!selectedEmoji) {
      setError('⚠️ Por favor, selecciona un avatar.');
      return;
    }
    if (!password) {
      setError('⚠️ Ingresa una contraseña.');
      return;
    }

    setLoading(true);

    try {
      const { data: user, error: fetchError } = await supabase
        .from('users')
        .select('*')
        .eq('emoji', selectedEmoji)
        .single();

      if (fetchError && fetchError.code !== 'PGRST116') {
        setError('❌ Error al conectar con la base de datos.');
        setLoading(false);
        return;
      }

      if (!user) {
        const { error: insertError } = await supabase.from('users').insert({
          emoji: selectedEmoji,
          password,
          aura_points: 0,
          aura_level: 1,
        });

        if (insertError) {
          setError('❌ No se pudo registrar el nuevo usuario.');
        } else {
          navigate('/shop');
        }
        setLoading(false);
        return;
      }

      if (user && !user.password) {
        await supabase.from('users').update({ password }).eq('id', user.id);
        navigate('/shop');
      } else if (user.password === password) {
        navigate('/shop');
      } else {
        setError('❌ Contraseña incorrecta');
      }
    } catch (err) {
      console.error(err);
      setError('❌ Error inesperado.');
    }

    setLoading(false);
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-black font-mono">
      <MatrixBackground />
      <div className="relative z-10 w-full max-w-md p-8 bg-gray-900 bg-opacity-90 rounded-lg border-2 border-green-400">
        <h1 className="text-4xl font-bold text-green-400 text-center">⚡ CorakSmart ⚡</h1>
        <form onSubmit={handleSubmit} className="space-y-4 mt-6">
          <div className="grid grid-cols-4 gap-4">
            {EMOJI_AVATARS.map((emoji) => (
              <button
                key={emoji}
                type="button"
                onClick={() => setSelectedEmoji(emoji)}
                className={`text-4xl p-2 rounded-md ${
                  selectedEmoji === emoji
                    ? 'bg-green-900 border-2 border-green-400'
                    : 'bg-gray-800 border-2 border-gray-600 hover:border-green-500'
                }`}
              >
                {emoji}
              </button>
            ))}
          </div>

          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="CONTRASEÑA"
            className="w-full px-4 py-2 text-center bg-transparent border-2 border-green-400 rounded-md text-green-300"
          />

          {error && <p className="text-red-500 text-center">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-green-400 text-black font-bold rounded hover:bg-green-300 disabled:bg-gray-500"
          >
            {loading ? 'CONECTANDO...' : 'ENTRAR'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Home;
