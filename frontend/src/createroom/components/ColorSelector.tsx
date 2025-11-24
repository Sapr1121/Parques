import React from 'react';

const colors = [
  { key: 'rojo', emoji: '🔴', label: 'Rojo' },
  { key: 'azul', emoji: '🔵', label: 'Azul' },
  { key: 'amarillo', emoji: '🟡', label: 'Amarillo' },
  { key: 'verde', emoji: '🟢', label: 'Verde' },
];

interface Props {
  selected: string;
  onSelect: (color: string) => void;
}

export const ColorSelector: React.FC<Props> = ({ selected, onSelect }) => (
  <div className="grid grid-cols-2 gap-4 mb-6">
    {colors.map((c) => (
      <button
        key={c.key}
        onClick={() => onSelect(c.key)}
        className={`flex flex-col items-center justify-center p-4 rounded-2xl border-2 transition transform hover:scale-105 ${
          selected === c.key
            ? 'bg-yellow-400 text-gray-900 border-yellow-200'
            : 'bg-white/20 text-white border-white/30'
        }`}
      >
        <span className="text-3xl mb-1">{c.emoji}</span>
        <span className="font-bold">{c.label}</span>
      </button>
    ))}
  </div>
);