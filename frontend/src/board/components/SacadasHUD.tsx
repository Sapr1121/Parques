import React from 'react';
import type { ColorJugador } from '../types/gameTypes';

interface Props {
  count: number;
  total?: number;
  playerName?: string;
  color?: ColorJugador | string;
}

const SacadasHUD: React.FC<Props> = ({ count, total = 4, playerName, color = 'gray' }) => {
  return (
    <div className="mb-4 p-3 rounded-lg shadow-lg bg-white border-2 flex items-center gap-3" style={{ borderColor: typeof color === 'string' ? color : undefined }}>
      <div className="flex flex-col">
        <span className="text-sm text-gray-500">Fichas sacadas</span>
        <span className="text-2xl font-bold text-gray-800">{count}/{total}</span>
      </div>
      {playerName && (
        <div className="ml-auto text-sm text-gray-600">{playerName}</div>
      )}
    </div>
  );
};

export default SacadasHUD;
