import React from 'react';
import type { ColorJugador } from '../types/gameTypes';
import { getColorHex } from '../types/gameTypes';

interface PremioPopupProps {
  visible: boolean;
  fichasElegibles: Array<{
    id: number;
    color: ColorJugador;
    posicion: number;
  }>;
  onSeleccionarFicha: (fichaId: number) => void;
}

const PremioPopup: React.FC<PremioPopupProps> = ({
  visible,
  fichasElegibles,
  onSeleccionarFicha
}) => {
  if (!visible) return null;

  return (
    <>
      {/* Overlay invisible que solo bloquea clicks - NO oscurece nada */}
      <div 
        className="fixed inset-0 z-40 pointer-events-auto"
        style={{ backgroundColor: 'transparent' }}
      />
      
      {/* Popup compacto en esquina superior derecha */}
      <div className="fixed top-4 right-4 z-50 w-96 pointer-events-auto">
        <div 
          className="bg-gradient-to-br from-yellow-400 via-orange-400 to-red-500 rounded-2xl shadow-2xl p-4 animate-slide-in"
          style={{
            border: '4px solid gold',
            boxShadow: '0 0 40px rgba(251, 191, 36, 0.7), inset 0 0 20px rgba(255, 255, 255, 0.3)'
          }}
        >
          {/* Título compacto */}
          <div className="text-center mb-3">
            <div className="flex items-center justify-center gap-2 mb-2">
              <span className="text-4xl animate-pulse">🏆</span>
              <h2 className="text-2xl font-black text-white drop-shadow-lg">
                PREMIO 3 DOBLES
              </h2>
            </div>
            <p className="text-sm text-white font-bold drop-shadow-md">
              Envía una ficha directo a META
            </p>
          </div>

          {/* Lista de fichas elegibles (más compacta) */}
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {fichasElegibles.map((ficha) => (
              <button
                key={ficha.id}
                onClick={() => onSeleccionarFicha(ficha.id)}
                className="w-full bg-white hover:bg-yellow-50 rounded-lg p-3 shadow-lg
                         transform hover:scale-102 transition-all duration-200
                         border-2 border-transparent hover:border-yellow-400
                         flex items-center gap-3"
              >
                {/* Color de la ficha (más pequeño) */}
                <div 
                  className="w-12 h-12 rounded-full shadow-lg border-3 border-white flex-shrink-0"
                  style={{ 
                    backgroundColor: getColorHex(ficha.color),
                    boxShadow: `0 0 15px ${getColorHex(ficha.color)}`
                  }}
                />
                
                {/* Información */}
                <div className="flex-1 text-left">
                  <p className="font-black text-lg text-gray-800">
                    Ficha #{ficha.id + 1}
                  </p>
                  <p className="text-xs text-gray-600 capitalize">
                    {ficha.color} · Pos: {ficha.posicion}
                  </p>
                </div>

                {/* Icono de selección */}
                <div className="text-yellow-500 font-bold text-xl">
                  ▶
                </div>
              </button>
            ))}
          </div>

          {/* Advertencia compacta */}
          <div className="mt-3 bg-white bg-opacity-90 rounded-lg p-2">
            <p className="text-center text-gray-800 font-bold text-xs">
              ⚠️ Acción irreversible
            </p>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes slide-in {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        .animate-slide-in {
          animation: slide-in 0.3s ease-out;
        }
      `}</style>
    </>
  );
};

export default PremioPopup;
