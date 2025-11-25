import React, { useState } from 'react';
import { useJoinRoom } from '../hooks/useJoinRoom';

const JoinRoomModal = ({ isOpen, onClose, onJoin }) => {
  const [joinCode, setJoinCode] = useState('');
  const { status, error, handleJoin } = useJoinRoom();

  if (!isOpen) return null;

  const handleJoinSubmit = async () => {
    const code = joinCode.trim().toUpperCase();
    if (code.length !== 8) {
      alert('El código debe tener exactamente 8 caracteres');
      return;
    }
    const hexRegex = /^[0-9A-F]{8}$/;
    if (!hexRegex.test(code)) {
      alert('El código debe contener solo números y letras (A-F)');
      return;
    }
    const lobby = await handleJoin(code);
    if (lobby) {
      onJoin(code); // Aquí puedes pasar también lobby info si lo necesitas
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleJoinSubmit();
    }
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ 
        backdropFilter: 'blur(10px)', 
        backgroundColor: 'rgba(0,0,0,0.6)',
        animation: 'fadeIn 0.3s ease-out'
      }}
      onClick={onClose}>
      
      <div 
        className="bg-white rounded-3xl shadow-2xl p-6 sm:p-8 max-w-md w-full transform transition-all"
        onClick={(e) => e.stopPropagation()}
        style={{
          animation: 'slideUp 0.3s ease-out'
        }}>
        
        {/* Título */}
        <div className="text-center mb-6">
          <div className="text-5xl sm:text-6xl mb-3">🔗</div>
          <h2 className="text-2xl sm:text-3xl font-black"
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
            Unirse con Código
          </h2>
          <p className="text-gray-600 text-sm mt-2">
            Ingresa el código de sala para unirte a la partida
          </p>
        </div>

        {/* Input del Código */}
        <div className="mb-6">
          <label className="block text-gray-700 font-bold mb-3 text-sm sm:text-base">
            Código de Sala:
          </label>
          <input
            type="text"
            value={joinCode}
            onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
            onKeyPress={handleKeyPress}
            maxLength={8}
            placeholder="A1B2C3D4"
            autoFocus
            className="w-full px-4 py-3 sm:py-4 border-4 border-purple-300 rounded-xl text-center text-xl sm:text-2xl font-bold tracking-widest uppercase focus:outline-none focus:border-purple-500 transition-all"
            style={{ 
              fontFamily: 'monospace',
              background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)'
            }}
          />
      
          <div className="flex items-center justify-between mt-2 text-xs sm:text-sm">
            <span className="text-gray-500">
              {joinCode.length}/8 caracteres
            </span>
            {joinCode.length === 8 && (
              <span className="text-green-600 font-bold">✓ Código completo</span>
            )}
          </div>
        </div>


        {/* Información */}
        <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-3 sm:p-4 mb-6">
          <p className="text-xs sm:text-sm text-blue-800">
            <span className="font-bold">💡 Consejo:</span> El código debe ser proporcionado por el anfitrión de la sala.
          </p>
        </div>

        {/* Botones */}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 py-3 sm:py-4 px-4 sm:px-6 rounded-xl font-bold text-base sm:text-lg transform transition-all hover:scale-105 active:scale-95 shadow-lg"
            style={{
              background: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%)',
              color: 'white',
              textShadow: '1px 1px 2px rgba(0,0,0,0.2)'
            }}>
            <span className="mr-2">❌</span>
            Cancelar
          </button>
          
          <button
            onClick={handleJoinSubmit}
            disabled={joinCode.length !== 8}
            className={`flex-1 py-3 sm:py-4 px-4 sm:px-6 rounded-xl font-bold text-base sm:text-lg transform transition-all shadow-lg
              ${joinCode.length === 8 
                ? 'hover:scale-105 active:scale-95' 
                : 'opacity-50 cursor-not-allowed'
              }`}
            style={{
              background: joinCode.length === 8 
                ? 'linear-gradient(135deg, #4facfe 0%, #00a8e8 100%)' 
                : '#cbd5e0',
              color: 'white',
              textShadow: joinCode.length === 8 ? '1px 1px 2px rgba(0,0,0,0.2)' : 'none'
            }}>
            <span className="mr-2">🚀</span>
            Unirse
          </button>
        </div>

        {/* Decoración inferior */}
        <div className="mt-6 flex justify-center gap-2">
          <div className="w-2 h-2 rounded-full bg-yellow-400 animate-bounce" style={{ animationDelay: '0s' }}></div>
          <div className="w-2 h-2 rounded-full bg-blue-400 animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2 h-2 rounded-full bg-red-400 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          <div className="w-2 h-2 rounded-full bg-green-400 animate-bounce" style={{ animationDelay: '0.3s' }}></div>
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px) scale(0.95);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }
      `}</style>
    </div>
  );
};

export default JoinRoomModal;