import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { supabase } from '../lib/supabaseClient';

interface ProfileData {
  id: string;
  emoji: string;
  aura_points: number;
  aura_level: number;
}

const Profile = () => {
  const { user, loading: authLoading } = useAuth();
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (authLoading) {
      return; // Wait for the auth state to be determined
    }
    if (!user) {
      setLoading(false);
      return; // No user, so no profile to fetch
    }

    const fetchProfile = async () => {
      setLoading(true);
      const { data, error } = await supabase
        .from('users')
        .select('id, aura_points, aura_level')
        .eq('id', user.id)
        .single();

      if (error) {
        setError(error.message);
      } else if (data) {
        // The emoji is in user_metadata, not the table
        const emoji = user.user_metadata?.emoji || '❔';
        setProfile({ ...data, emoji });
      }
      setLoading(false);
    };

    fetchProfile();
  }, [user, authLoading]);

  if (loading || authLoading) {
    return <div className="bg-black text-green-400 min-h-screen flex items-center justify-center font-mono">Cargando perfil...</div>;
  }

  if (!user) {
    return (
      <div className="bg-black text-white min-h-screen flex flex-col items-center justify-center font-mono text-center">
        <h1 className="text-4xl mb-6">Debes iniciar sesión para ver tu perfil.</h1>
        <Link to="/" className="bg-yellow-500 text-black py-2 px-6 rounded hover:bg-yellow-400 transition-colors">
          Ir a Login
        </Link>
      </div>
    );
  }

  if (error || !profile) {
    return <div className="bg-black text-red-500 min-h-screen flex items-center justify-center font-mono">Error al cargar el perfil.</div>;
  }

  return (
    <div className="bg-black text-white min-h-screen flex items-center justify-center font-mono">
      <div className="border-4 border-purple-500 bg-gray-900/90 p-8 rounded-lg text-center shadow-[0_0_20px_rgba(168,85,247,0.7)]">
        <h1 className="text-5xl mb-6 text-purple-400">🧙 Perfil de Usuario</h1>
        <div className="text-8xl mb-6">{profile.emoji}</div>
        <div className="text-left space-y-4">
          <p className="text-2xl">
            <span className="text-green-400">Puntos Aura:</span> {profile.aura_points.toLocaleString()}
          </p>
          <p className="text-2xl">
            <span className="text-cyan-400">Nivel Aura:</span> {profile.aura_level}
          </p>
        </div>
      </div>
    </div>
  );
};

export default Profile;
