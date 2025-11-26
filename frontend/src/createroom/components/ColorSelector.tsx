import React, { useState } from 'react';

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

export const ColorSelector: React.FC<Props> = ({ selected, onSelect }) => {
  const [hoveredKey, setHoveredKey] = useState<string | null>(null);

  return (
    <div className="w-full px-2 sm:px-4">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 md:gap-6 mb-6">
        {colors.map((c) => {
          const isSelected = selected === c.key;
          const isHovered = hoveredKey === c.key;
          
          return (
            <button
              key={c.key}
              onClick={() => onSelect(c.key)}
              onMouseEnter={() => setHoveredKey(c.key)}
              onMouseLeave={() => setHoveredKey(null)}
              className={`
                relative flex flex-col items-center justify-center 
                p-6 sm:p-8 rounded-3xl border-4 
                transition-all duration-300 ease-out
                transform hover:scale-105 active:scale-95
                ${isSelected
                  ? 'bg-yellow-400 text-gray-900 border-yellow-200 shadow-2xl shadow-yellow-400/50 scale-105'
                  : 'bg-white/20 text-white border-white/30 backdrop-blur-sm hover:bg-white/30 hover:shadow-xl'
                }
              `}
            >
              {/* Efecto de brillo cuando está seleccionado */}
              {isSelected && (
                <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-white/40 to-transparent animate-pulse" />
              )}
              
              {/* Emoji con animación */}
              <span className={`
                text-5xl sm:text-6xl md:text-7xl mb-3 relative z-10
                transition-transform duration-300
                ${(isSelected || isHovered) ? 'scale-110' : ''}
                ${isSelected ? 'animate-bounce' : ''}
              `}>
                {c.emoji}
              </span>
              
              {/* Label */}
              <span className={`
                font-bold text-lg sm:text-xl relative z-10
                ${isSelected ? 'drop-shadow-md' : ''}
              `}>
                {c.label}
              </span>
              
              {/* Checkmark cuando está seleccionado */}
              {isSelected && (
                <div className="absolute top-2 right-2 bg-white rounded-full p-1 shadow-lg">
                  <svg className="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};