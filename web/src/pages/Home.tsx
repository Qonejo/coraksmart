import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MatrixBackground from '../components/MatrixBackground';
import { supabase } from '../lib/supabaseClient';

const Home = () => {
  const navigate = useNavigate();
  const [selectedEmoji, setSelectedEmoji] = useState<string | null>(null);
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const EMOJI_AVATARS = ['😀', '🐱', '🦊', '🐼', '🐸', '👾', '🦁', '🐰'];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!selectedEmoji) {
      setError('❌ Por favor, selecciona un avatar.');
      return;
    }
    if (!password) {
      setError('❌ Por favor, introduce una contraseña.');
      return;
    }

    setLoading(true);

    // 1. Buscar si ya existe el usuario en la tabla "users"
    const { data: user, error: fetchError } = await supabase
      .from('users')
      .select('*')
      .eq('emoji', selectedEmoji)
      .single();

    if (fetchError && fetchError.code !== 'PGRST116') {
      console.error('Error al consultar usuario:', fetchError);
      setError('❌ Error al conectar con la base de datos.');
      setLoading(false);
      return;
    }

    // 2. Si no existe → crear usuario nuevo
    if (!user) {
      const { error: insertError } = await supabase.from('users').insert({
        emoji: selectedEmoji,
        password: password,
        aura_points: 0,
        aura_level: 1,
      });

      if (insertError) {
        console.error('Error creando usuario:', insertError);
        setError('❌ No se pudo registrar el nuevo usuario.');
      } else {
        navigate('/shop');
      }
      setLoading(false);
      return;
    }

    // 3. Si existe pero no tiene contraseña → asignar
    if (user && !user.password) {
      const { error: updateError } = await supabase
        .from('users')
        .update({ password: password })
        .eq('id', user.id);

      if (updateError) {
        console.error('Error asignando contraseña:', updateError);
        setError('❌ No se pudo asignar la contraseña.');
      } else {
        navigate('/shop');
      }
      setLoading(false);
      return;
    }

    // 4. Si existe y coincide contraseña → login correcto
    if (user.password === password) {
      navigate('/shop');
      setLoading(false);
      return;
    }

    // 5. Contraseña incorrecta
    setError('❌ Contraseña incorrecta');
    setLoading(false);
  };

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center overflow-hidden font-mono bg-black">
      <MatrixBackground />
      <div className="relative z-10 w-full max-w-md p-8 space-y-6 bg-gray-900 bg-opacity-90 rounded-lg border-2 border-green-400 shadow-[0_0_20px_rgba(0,255,0,0.8)]">

        <div className="text-center">
          <h1 className="text-4xl font-bold text-green-400">⚡ CorakSmart ⚡</h1>
          <p className="text-green-300 mt-2">Selecciona tu avatar y entra a la tienda</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Emoji Grid */}
          <div className="grid grid-cols-4 gap-4">
            {EMOJI_AVATARS.map((emoji) => (
              <button
                type="button"
                key={emoji}
                onClick={() => setSelectedEmoji(emoji)}
                className={`text-4xl p-2 rounded-md transition-all duration-300 ${
                  selectedEmoji === emoji
                    ? 'bg-green-900 border-2 border-green-400 ring-2 ring-green-400'
                    : 'bg-gray-800 border-2 border-gray-600 hover:border-green-500'
                }`}
              >
                {emoji}
              </button>
            ))}
          </div>

          {/* Password Input */}
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="CONTRASEÑA"
            required
            className="w-full px-4 py-2 text-center bg-transparent border-2 border-green-400 rounded-md text-green-300 placeholder-green-700 focus:outline-none focus:ring-2 focus:ring-green-400"
          />

          {error && <p className="text-red-500 text-center text-sm">{error}</p>}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 font-bold text-gray-900 bg-green-400 rounded-md hover:bg-green-300 transition-colors duration-300 shadow-[0_0_15px_rgba(0,255,0,0.6)] disabled:bg-gray-500"
          >
            {loading ? 'CONECTANDO...' : 'ENTRAR'}
          </button>
        </form>

        <p className="text-center text-pink-500 text-sm">
          🛑 Tienda privada – Solo usuarios autorizados
        </p>
      </div>
    </div>
  );
};

export default Home;
