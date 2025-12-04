import React from 'react';
import type { ColorJugador } from '../types/gameTypes';

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

  // ⭐ Detectar si el menú debe aparecer ABAJO en lugar de arriba
  // Esto incluye:
  // 1. Casillas superiores del tablero (29-39)
  // 2. Camino a meta (posicionMeta >= 0 y la Y del menú está arriba)
  // 3. Cualquier posición donde la Y del menú esté cerca del borde superior
  const estaEnZonaSuperior = 
    // Casillas del tablero en fila superior
    (fichaPosicion !== undefined && fichaPosicion >= 29 && fichaPosicion <= 39) ||
    // O está en camino a meta y el menú está muy arriba (menos de 150px desde el top)
    (fichaEstado === 'CAMINO_META' && position.y < 150) ||
    // O simplemente el menú está muy arriba en la pantalla
    (position.y < 120);

  // Calcular pasos restantes:
  // - Si la ficha está en CAMINO_META: pasos = 7 - posicion_meta
  // - Si la ficha está EN_JUEGO: NO validar, puede moverse libremente por el tablero
  let pasosRestantes: number | null = null;
  if (fichaEstado === 'CAMINO_META' && posicionMeta !== undefined && posicionMeta !== null) {
    // Solo cuando está en el camino final a la meta, limitar movimientos
    pasosRestantes = Math.max(0, 7 - posicionMeta);
  }
  // ✅ ELIMINADO: La validación incorrecta de "faltan 8 pasos desde la salida"
  // Las fichas EN_JUEGO pueden moverse libremente por el tablero

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
          // Si está en zona superior, mostrar ABAJO (+10px), si no, ARRIBA (-100%)
          transform: estaEnZonaSuperior ? 'translate(-50%, 10px)' : 'translate(-50%, -100%)',
          marginTop: estaEnZonaSuperior ? 0 : -10
        }}
      >
        {/* Flecha apuntando hacia la ficha */}
        <div
          className={`absolute left-1/2 w-4 h-4 bg-white transform -translate-x-1/2 ${
            estaEnZonaSuperior 
              ? '-top-2 border-l-2 border-t-2 -rotate-45' // Flecha arriba cuando menú está abajo
              : '-bottom-2 border-r-2 border-b-2 rotate-45' // Flecha abajo cuando menú está arriba
          }`}
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
