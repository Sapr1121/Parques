import React from 'react';
import type { ColorJugador } from '../types/gameTypes';
import { esCasillaSalida } from '../utils/posiciones';

// Colores de las fichas
const COLORES: Record<ColorJugador, string> = {
  rojo: '#C41E3A',
  azul: '#0047AB',
  verde: '#228B22',
  amarillo: '#DAA520'
};

interface MiniMenuDadosProps {
  visible: boolean;
  position: { x: number; y: number };
  dado1: number;
  dado2: number;
  suma: number;
  dado1Usado: boolean;
  dado2Usado: boolean;
  fichaColor: ColorJugador;
  fichaId: number;
  fichaEstado?: string;
  posicionMeta?: number | undefined;
  fichaPosicion?: number | undefined;
  onSeleccionarDado: (dado: 1 | 2 | 3) => void;
  onCerrar: () => void;
}

const MiniMenuDados: React.FC<MiniMenuDadosProps> = ({
  visible,
  position,
  dado1,
  dado2,
  suma,
  dado1Usado,
  dado2Usado,
  fichaColor,
  fichaId,
  fichaEstado,
  posicionMeta,
  fichaPosicion,
  onSeleccionarDado,
  onCerrar
}) => {
  if (!visible) return null;

  const colorFicha = COLORES[fichaColor];
  const ambosDisponibles = !dado1Usado && !dado2Usado;

  // Calcular pasos restantes:
  // - Si la ficha está en CAMINO_META: pasos = 7 - posicion_meta
  // - Si la ficha está EN_JUEGO y está justo en la casilla de salida para su color: faltan 8 pasos
  let pasosRestantes: number | null = null;
  if (fichaEstado === 'CAMINO_META' && posicionMeta !== undefined && posicionMeta !== null) {
    pasosRestantes = Math.max(0, 7 - posicionMeta);
  } else if (fichaEstado === 'EN_JUEGO' && fichaPosicion !== undefined && fichaPosicion !== null) {
    if (esCasillaSalida(fichaPosicion, fichaColor)) {
      pasosRestantes = 8;
    }
  }

  const dado1DisabledByMeta = pasosRestantes !== null ? dado1 > pasosRestantes : false;
  const dado2DisabledByMeta = pasosRestantes !== null ? dado2 > pasosRestantes : false;
  const sumaDisabledByMeta = pasosRestantes !== null ? suma > pasosRestantes : false;

  return (
    <>
      {/* Overlay para cerrar al hacer clic fuera */}
      <div
        className="fixed inset-0 z-40"
        onClick={onCerrar}
      />

      {/* Mini menú */}
      <div
        className="fixed z-50 bg-white rounded-xl shadow-2xl border-2 p-3 min-w-[180px]"
        style={{
          left: position.x,
          top: position.y,
          borderColor: colorFicha,
          transform: 'translate(-50%, -100%)',
          marginTop: -10
        }}
      >
        {/* Flecha apuntando hacia abajo */}
        <div
          className="absolute left-1/2 -bottom-2 w-4 h-4 bg-white border-r-2 border-b-2 transform rotate-45 -translate-x-1/2"
          style={{ borderColor: colorFicha }}
        />

        {/* Header */}
        <div
          className="text-center font-bold text-white px-3 py-1 rounded-lg mb-2 text-sm"
          style={{ backgroundColor: colorFicha }}
        >
          Ficha {fichaId + 1}
        </div>

        {/* Mostrar pasos restantes si aplica */}
        {pasosRestantes !== null && (
          <div className="text-center text-sm text-gray-600 mb-2">Faltan {pasosRestantes} paso(s) para META</div>
        )}

        {/* Opciones de dados */}
        <div className="space-y-2">
          {/* Dado 1 */}
          <button
            onClick={() => onSeleccionarDado(1)}
            disabled={dado1Usado || dado1DisabledByMeta}
            className={`w-full flex items-center justify-between px-3 py-2 rounded-lg transition-all
              ${dado1Usado || dado1DisabledByMeta
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-blue-50 hover:bg-blue-100 text-blue-700 hover:scale-105 cursor-pointer'
              }`}
          >
            <span className="font-medium">🎲 Dado 1</span>
            <span className={`font-bold text-lg ${dado1Usado ? 'line-through' : ''}`}>
              +{dado1}
            </span>
          </button>

          {/* Dado 2 */}
          <button
            onClick={() => onSeleccionarDado(2)}
            disabled={dado2Usado || dado2DisabledByMeta}
            className={`w-full flex items-center justify-between px-3 py-2 rounded-lg transition-all
              ${dado2Usado || dado2DisabledByMeta
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-green-50 hover:bg-green-100 text-green-700 hover:scale-105 cursor-pointer'
              }`}
          >
            <span className="font-medium">🎲 Dado 2</span>
            <span className={`font-bold text-lg ${dado2Usado ? 'line-through' : ''}`}>
              +{dado2}
            </span>
          </button>

          {/* Suma (solo si ambos dados disponibles) */}
          {ambosDisponibles && (
            <button
              onClick={() => onSeleccionarDado(3)}
              disabled={sumaDisabledByMeta}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg
                ${sumaDisabledByMeta ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-purple-50 hover:bg-purple-100 text-purple-700 hover:scale-105 transition-all cursor-pointer'}`}
            >
              <span className="font-medium">🎯 Suma</span>
              <span className="font-bold text-lg">+{suma}</span>
            </button>
          )}
        </div>

        {/* Botón cancelar */}
        <button
          onClick={onCerrar}
          className="w-full mt-2 px-3 py-1 text-gray-500 hover:text-gray-700 text-sm hover:bg-gray-100 rounded transition-all"
        >
          Cancelar
        </button>
      </div>
    </>
  );
};

export default MiniMenuDados;
