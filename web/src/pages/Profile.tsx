import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

interface ProfileData {
  emoji: string;
  aura_points: number;
  aura_level: number;
  level_name: string;
}

const Profile = () => {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await fetch('/api/profile');
        if (response.status === 401) {
          throw new Error('Not authenticated');
        }
        if (!response.ok) {
          throw new Error('Failed to fetch profile data');
        }
        const data: ProfileData = await response.json();
        setProfile(data);
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  if (loading) {
    return <div className="bg-gray-900 text-white min-h-screen flex items-center justify-center font-mono">Cargando perfil...</div>;
  }

  if (error === 'Not authenticated') {
    return (
      <div className="bg-gray-900 text-white min-h-screen flex flex-col items-center justify-center font-mono text-center">
        <h1 className="text-4xl mb-6">Debes iniciar sesión para ver tu perfil.</h1>
        <Link to="/login" className="bg-yellow-500 text-black py-2 px-6 rounded hover:bg-yellow-400 transition-colors">
          Ir a Login
        </Link>
      </div>
    );
  }

  if (error || !profile) {
    return <div className="bg-gray-900 text-white min-h-screen flex items-center justify-center font-mono">Error al cargar el perfil.</div>;
  }

  return (
    <div className="bg-gray-900 text-white min-h-screen flex items-center justify-center font-mono">
      <div className="border-4 border-purple-500 bg-black/50 p-8 rounded-lg text-center">
        <h1 className="text-5xl mb-6">🧙 Perfil de Usuario</h1>
        <div className="text-8xl mb-6">{profile.emoji}</div>
        <div className="text-left space-y-4">
          <p className="text-2xl">
            <span className="text-green-400">Puntos Aura:</span> {profile.aura_points.toLocaleString()}
          </p>
          <p className="text-2xl">
            <span className="text-cyan-400">Nivel Aura:</span> {profile.aura_level} ({profile.level_name})
          </p>
        </div>
      </div>
    </div>
  );
};

export default Profile;
