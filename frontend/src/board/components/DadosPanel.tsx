import React from 'react';
import type { ColorJugador } from '../types/gameTypes';
import { getColorHex } from '../types/gameTypes';

interface DadosPanelProps {
  dado1: number;
  dado2: number;
  suma: number;
  esDoble: boolean;
  dadosLanzados: boolean;
  dadosUsados: number[];
  esMiTurno: boolean;
  puedeTomarAccion: boolean;
  fichasEnCarcel: number;
  fichaSeleccionada: { color: ColorJugador; id: number } | null;
  onLanzarDados: () => void;
  onSacarDeCarcel: () => void;
  onSacarTodasDeCarcel: () => void;
  onMoverFicha: (dadoElegido: 1 | 2 | 3) => void;
  miColor: ColorJugador | null;
}

// Componente para dibujar un dado
const Dado: React.FC<{ valor: number; usado?: boolean; onClick?: () => void; seleccionable?: boolean }> = ({
  valor,
  usado = false,
  onClick,
  seleccionable = false
}) => {
  // Posiciones de los puntos según el valor del dado
  const puntos: Record<number, Array<{ x: number; y: number }>> = {
    1: [{ x: 50, y: 50 }],
    2: [{ x: 25, y: 25 }, { x: 75, y: 75 }],
    3: [{ x: 25, y: 25 }, { x: 50, y: 50 }, { x: 75, y: 75 }],
    4: [{ x: 25, y: 25 }, { x: 75, y: 25 }, { x: 25, y: 75 }, { x: 75, y: 75 }],
    5: [{ x: 25, y: 25 }, { x: 75, y: 25 }, { x: 50, y: 50 }, { x: 25, y: 75 }, { x: 75, y: 75 }],
    6: [{ x: 25, y: 25 }, { x: 75, y: 25 }, { x: 25, y: 50 }, { x: 75, y: 50 }, { x: 25, y: 75 }, { x: 75, y: 75 }]
  };

  return (
    <div
      onClick={seleccionable ? onClick : undefined}
      className={`
        relative w-16 h-16 rounded-xl shadow-lg
        ${usado ? 'bg-gray-300 opacity-50' : 'bg-white'}
        ${seleccionable && !usado ? 'cursor-pointer hover:scale-110 hover:shadow-xl ring-2 ring-purple-400' : ''}
        transition-all duration-200
      `}
      style={{
        border: seleccionable && !usado ? '3px solid #7c3aed' : '2px solid #374151'
      }}
    >
      <svg viewBox="0 0 100 100" className="w-full h-full">
        {puntos[valor]?.map((punto, idx) => (
          <circle
            key={idx}
            cx={punto.x}
            cy={punto.y}
            r="12"
            fill={usado ? '#9ca3af' : '#1f2937'}
          />
        ))}
      </svg>
      {usado && (
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-gray-600 text-xl">✓</span>
        </div>
      )}
    </div>
  );
};

const DadosPanel: React.FC<DadosPanelProps> = ({
  dado1,
  dado2,
  suma,
  esDoble,
  dadosLanzados,
  dadosUsados,
  esMiTurno,
  puedeTomarAccion,
  fichasEnCarcel,
  fichaSeleccionada,
  onLanzarDados,
  onSacarDeCarcel,
  onSacarTodasDeCarcel,
  onMoverFicha,
  miColor
}) => {
  const dado1Usado = dadosUsados.includes(1);
  const dado2Usado = dadosUsados.includes(2);
  const puedeLanzar = esMiTurno && !dadosLanzados;
  // Puede sacar de cárcel si es mi turno, hay dados, son dobles Y hay fichas en cárcel
  const puedeSacarCarcel = esMiTurno && dadosLanzados && esDoble && fichasEnCarcel > 0;
  // Sacar TODAS: cuando TODAS las fichas (4) están en cárcel y son dobles
  const puedesSacarTodas = puedeSacarCarcel && fichasEnCarcel === 4;
  const puedeSeleccionarDado = puedeTomarAccion && fichaSeleccionada !== null;

  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 w-80">
      {/* Header con color del jugador */}
      <div 
        className="flex items-center gap-3 mb-4 pb-3 border-b-2"
        style={{ borderColor: miColor ? getColorHex(miColor) : '#e5e7eb' }}
      >
        <div 
          className="w-4 h-4 rounded-full"
          style={{ backgroundColor: miColor ? getColorHex(miColor) : '#9ca3af' }}
        />
        <h3 className="text-lg font-bold text-gray-800">
          {esMiTurno ? '🎯 Tu Turno' : '⏳ Esperando...'}
        </h3>
      </div>

      {/* Dados */}
      <div className="flex flex-col items-center gap-4">
        {dadosLanzados ? (
          <>
            {/* Dados visuales */}
            <div className="flex gap-4 items-center">
              <Dado 
                valor={dado1} 
                usado={dado1Usado}
                seleccionable={puedeSeleccionarDado && !dado1Usado}
                onClick={() => onMoverFicha(1)}
              />
              <Dado 
                valor={dado2} 
                usado={dado2Usado}
                seleccionable={puedeSeleccionarDado && !dado2Usado}
                onClick={() => onMoverFicha(2)}
              />
            </div>

            {/* Suma */}
            <div className="flex items-center gap-2">
              <span className="text-gray-600">Suma:</span>
              <span 
                className={`text-2xl font-bold ${esDoble ? 'text-purple-600' : 'text-gray-800'}`}
              >
                {suma}
              </span>
              {esDoble && (
                <span className="bg-purple-100 text-purple-700 px-2 py-1 rounded-full text-sm font-bold">
                  ¡DOBLES!
                </span>
              )}
            </div>

            {/* Botón para usar suma */}
            {puedeSeleccionarDado && !dado1Usado && !dado2Usado && (
              <button
                onClick={() => onMoverFicha(3)}
                className="w-full py-2 px-4 bg-gradient-to-r from-purple-500 to-indigo-500 
                           text-white font-bold rounded-xl shadow-lg
                           hover:from-purple-600 hover:to-indigo-600
                           transform hover:scale-105 transition-all"
              >
                Usar Suma ({suma})
              </button>
            )}

            {/* Mensaje de ficha seleccionada */}
            {fichaSeleccionada && (
              <div className="text-sm text-purple-600 font-medium animate-pulse">
                Ficha {fichaSeleccionada.id + 1} seleccionada - Elige un dado
              </div>
            )}
          </>
        ) : (
          /* Placeholder cuando no hay dados */
          <div className="flex gap-4 items-center opacity-30">
            <div className="w-16 h-16 rounded-xl bg-gray-200 border-2 border-gray-300" />
            <div className="w-16 h-16 rounded-xl bg-gray-200 border-2 border-gray-300" />
          </div>
        )}

        {/* Botones de acción */}
        <div className="w-full space-y-2 mt-4">
          {/* Botón Lanzar Dados */}
          {puedeLanzar && (
            <button
              onClick={onLanzarDados}
              className="w-full py-3 px-4 bg-gradient-to-r from-green-500 to-emerald-500 
                         text-white font-bold rounded-xl shadow-lg
                         hover:from-green-600 hover:to-emerald-600
                         transform hover:scale-105 transition-all
                         flex items-center justify-center gap-2"
            >
              <span className="text-xl">🎲</span>
              Lanzar Dados
            </button>
          )}

          {/* Botón Sacar TODAS de Cárcel (4 fichas = todas) */}
          {puedesSacarTodas && (
            <button
              onClick={onSacarTodasDeCarcel}
              className="w-full py-3 px-4 bg-gradient-to-r from-orange-500 to-red-500 
                         text-white font-bold rounded-xl shadow-lg
                         hover:from-orange-600 hover:to-red-600
                         transform hover:scale-105 transition-all
                         flex items-center justify-center gap-2
                         animate-pulse"
            >
              <span className="text-xl">🔓</span>
              ¡SACAR TODAS! ({fichasEnCarcel} fichas)
            </button>
          )}

          {/* Botón Sacar de Cárcel (1-3 fichas) */}
          {puedeSacarCarcel && !puedesSacarTodas && (
            <button
              onClick={onSacarDeCarcel}
              className="w-full py-3 px-4 bg-gradient-to-r from-yellow-500 to-orange-500 
                         text-white font-bold rounded-xl shadow-lg
                         hover:from-yellow-600 hover:to-orange-600
                         transform hover:scale-105 transition-all
                         flex items-center justify-center gap-2"
            >
              <span className="text-xl">🔓</span>
              Sacar de Cárcel ({fichasEnCarcel} en cárcel)
            </button>
          )}
        </div>

        {/* Estado */}
        {!esMiTurno && (
          <div className="text-center text-gray-500 italic mt-2">
            Espera tu turno para jugar
          </div>
        )}

        {esMiTurno && dadosLanzados && !fichaSeleccionada && (
          <div className="text-center text-purple-600 font-medium mt-2">
            👆 Selecciona una ficha para mover
          </div>
        )}
      </div>
    </div>
  );
};

export default DadosPanel;
