import React, { useEffect } from 'react';
import type { ColorJugador } from '../types/gameTypes';

interface Props {
  visible: boolean;
  nombre: string;
  color?: ColorJugador | string;
  onClose?: () => void;
}

const VictoryPopup: React.FC<Props> = ({ visible, nombre, color = 'gold', onClose }) => {
  useEffect(() => {
    if (!visible) return;
    const t = setTimeout(() => {
      onClose?.();
    }, 5000);
    return () => clearTimeout(t);
  }, [visible, onClose]);

  if (!visible) return null;

  return (
    <div className="fixed left-0 top-0 w-full h-full pointer-events-none z-50 p-4">
      <div className="absolute left-1/2 top-10 sm:top-20 -translate-x-1/2 pointer-events-auto w-full max-w-xs sm:max-w-md">
        <div className="flex items-center gap-2 sm:gap-4 bg-gradient-to-r from-yellow-300 to-yellow-400 border-3 sm:border-4 border-yellow-500 rounded-2xl sm:rounded-3xl p-3 sm:p-6 shadow-2xl transform transition-transform animate-bounce">
          <div className="text-2xl sm:text-4xl">✨✨</div>
          <div className="text-center flex-1">
            <div className="text-lg sm:text-2xl font-extrabold text-yellow-900">¡{nombre} ha ganado!</div>
            <div className="text-xs sm:text-sm text-yellow-800">Felicidades — Partida finalizada</div>
          </div>
          <div className="text-2xl sm:text-4xl">🏆</div>
        </div>
      </div>
    </div>
  );
};

export default VictoryPopup;
