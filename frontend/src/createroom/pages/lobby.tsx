import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCreateRoom } from '../hooks/useCreateRoom';
import { ColorSelector } from '../components/ColorSelector';

export const CreateRoom: React.FC = () => {
  const navigate = useNavigate();
  const { create, roomCode, loading, error, connected } = useCreateRoom();
  const [name, setName] = useState('');
  const [color, setColor] = useState('');

  const handleCreate = async () => {
    if (!name.trim() || !color) return;
    await create(name.trim(), color);
  };

  if (roomCode) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-700 flex items-center justify-center p-4">
        <div className="bg-white/20 backdrop-blur-xl rounded-3xl p-8 text-center text-white max-w-md w-full shadow-2xl border border-white/30">
          <h2 className="text-3xl font-black mb-2">¡Sala Creada!</h2>
          <p className="text-lg mb-4">Comparte este código con tus amigos:</p>
          <div className="bg-white/30 rounded-2xl px-6 py-4 text-4xl font-bold tracking-widest mb-6">
            {roomCode}
          </div>
          <button
            onClick={() => navigator.clipboard.writeText(roomCode)}
            className="bg-yellow-400 text-gray-900 font-bold px-6 py-3 rounded-2xl hover:scale-105 transition"
          >
            Copiar código
          </button>
          <p className="mt-4 text-sm opacity-80">Esperando jugadores...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 to-purple-700 flex items-center justify-center p-4">
      <div className="bg-white/20 backdrop-blur-xl rounded-3xl p-8 text-center text-white max-w-md w-full shadow-2xl border border-white/30">
        <h2 className="text-3xl font-black mb-6">Crear Sala</h2>

        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Tu nombre"
          className="w-full px-4 py-3 rounded-2xl bg-white/30 text-white placeholder-white/70 border border-white/40 focus:outline-none focus:ring-2 focus:ring-yellow-400 mb-4"
        />

        <ColorSelector onSelect={setColor} selected={color} />

        {error && <p className="text-red-300 text-sm mb-4">{error}</p>}

        <button
          onClick={handleCreate}
          disabled={loading || !name.trim() || !color}
          className="w-full bg-yellow-400 text-gray-900 font-black py-3 rounded-2xl hover:scale-105 transition disabled:opacity-50"
        >
          {loading ? 'Creando...' : 'Crear Sala'}
        </button>
      </div>
    </div>
  );
};