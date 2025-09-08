import React, { useState, useEffect } from 'react';

// Define the structure of the data from the API
interface EmojiData {
  all_emojis: string[];
  occupied_emojis: string[];
}

const EmojiLogin = () => {
  const [emojiData, setEmojiData] = useState<EmojiData>({ all_emojis: [], occupied_emojis: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // State for the modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedEmoji, setSelectedEmoji] = useState<string | null>(null);
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [modalMessage, setModalMessage] = useState('');

  // Fetch emoji data on component mount
  useEffect(() => {
    const fetchEmojis = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/get-emojis');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data: EmojiData = await response.json();
        setEmojiData(data);
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };

    fetchEmojis();
  }, []);

  // Handlers for modal
  const handleEmojiClick = (emoji: string) => {
    setSelectedEmoji(emoji);
    setModalMessage('');
    setPassword('');
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedEmoji(null);
  };

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedEmoji) return;

    setIsSubmitting(true);
    setModalMessage('');

    try {
      const response = await fetch('/api/emoji-access', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ emoji: selectedEmoji, password }),
      });

      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(result.message || 'Login failed');
      }

      // On successful login, redirect to the main page
      window.location.href = '/';

    } catch (e: any) {
      setModalMessage(e.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Render logic
  if (loading) {
    return <div className="bg-gray-900 text-white min-h-screen flex items-center justify-center font-mono">Cargando avatares...</div>;
  }

  if (error) {
    return <div className="bg-gray-900 text-white min-h-screen flex items-center justify-center font-mono">Error: {error}</div>;
  }

  return (
    <div className="bg-black text-white min-h-screen p-4 font-mono text-center">
      <h1 className="text-2xl sm:text-3xl border-b-4 border-white pb-4 mb-4">Elige tu Avatar de Acceso</h1>
      <p className="text-yellow-300 bg-black/70 border-2 border-red-500 p-4 max-w-2xl mx-auto mb-6">
        Selecciona un avatar libre para registrarte, o selecciona tu avatar con 🔒 para iniciar sesión.
      </p>

      <div className="grid grid-cols-5 sm:grid-cols-8 md:grid-cols-10 lg:grid-cols-12 gap-4 max-w-4xl mx-auto">
        {emojiData.all_emojis.map((emoji) => {
          const isOccupied = emojiData.occupied_emojis.includes(emoji);
          return (
            <div
              key={emoji}
              className="relative cursor-pointer border-2 border-gray-600 bg-gray-900 p-2 transition-transform hover:scale-125 hover:border-yellow-400"
              onClick={() => handleEmojiClick(emoji)}
            >
              <span className="text-4xl">{emoji}</span>
              {isOccupied && <span className="absolute bottom-0 right-0 text-lg">🔒</span>}
            </div>
          );
        })}
      </div>

      {/* Access Modal */}
      {isModalOpen && selectedEmoji && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
          <div className="bg-gray-800 border-4 border-yellow-400 p-8 rounded-lg text-center">
            <h2 className="text-2xl mb-4">Acceder como</h2>
            <div className="text-7xl mb-6">{selectedEmoji}</div>
            <form onSubmit={handleLoginSubmit}>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="bg-gray-900 border-2 border-gray-600 rounded p-2 w-full mb-4 text-center text-white"
                placeholder="Contraseña"
                required
              />
              <button
                type="submit"
                disabled={isSubmitting}
                className="bg-green-600 hover:bg-green-500 w-full p-3 rounded disabled:bg-gray-500"
              >
                {isSubmitting ? 'Accediendo...' : 'Continuar'}
              </button>
            </form>
            {modalMessage && <p className="text-red-500 mt-4">{modalMessage}</p>}
            <button
              onClick={closeModal}
              className="mt-4 text-gray-400 hover:text-white"
            >
              Cerrar
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmojiLogin;
