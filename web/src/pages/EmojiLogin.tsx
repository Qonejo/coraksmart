import React, { useState, useEffect } from 'react';
import MatrixBackground from '../components/MatrixBackground';

const EmojiLogin = () => {
  const [emojis, setEmojis] = useState<string[]>([]);
  const [selectedEmoji, setSelectedEmoji] = useState<string | null>(null);
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // A hardcoded list of emojis as a fallback or for initial display
  const EMOJI_AVATARS = ['😀', '🚀', '👻', '🌵', '🎮', '💎', '👽', '💀', '🤖', '🦊', '🐱', '🐼'];

  useEffect(() => {
    // You can replace this with a fetch call if needed
    setEmojis(EMOJI_AVATARS);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!selectedEmoji) {
      setError('Por favor, selecciona un emoji.');
      return;
    }
    setLoading(true);
    console.log(`Logging in with ${selectedEmoji} and password ${password}`);
    // Mock login logic
    setTimeout(() => {
      setLoading(false);
      if (password === '123') {
        alert('Login successful!');
      } else {
        setError('Contraseña incorrecta.');
      }
    }, 1000);
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
