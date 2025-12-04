import React from 'react';
import type { ColorJugador } from '../types/gameTypes';

// Casillas de entrada a meta por color (donde entran al camino final)
const ENTRADAS_META: Record<ColorJugador, number> = {
  rojo: 33,    // Casilla segura antes de entrar al camino rojo
  azul: 16,    // Casilla segura antes de entrar al camino azul
  verde: 50,   // Casilla segura antes de entrar al camino verde
  amarillo: 67 // Casilla segura antes de entrar al camino amarillo
};

/**
 * Calcula cuántos pasos faltan para que una ficha EN_JUEGO llegue a su entrada de meta.
 * Retorna null si la ficha no está cerca (más de 8 pasos).
 */
function calcularPasosAEntradaMeta(posicion: number, color: ColorJugador): number | null {
  const entradaMeta = ENTRADAS_META[color];
  let pasosHastaEntrada = 0;
  
  // Si la ficha está antes de su entrada de meta (sin dar la vuelta)
  if (posicion <= entradaMeta) {
    pasosHastaEntrada = entradaMeta - posicion;
  } else {
    // Si la ficha pasó su entrada, debe dar la vuelta al tablero (68 casillas totales)
    pasosHastaEntrada = (68 - posicion) + entradaMeta;
  }
  
  // Solo considerar si está cerca (8 pasos o menos, ya que luego tiene 7 casillas de camino meta)
  if (pasosHastaEntrada <= 8) {
    return pasosHastaEntrada;
  }
  
  return null;
}

// Colores de las fichas
const COLORES: Record<ColorJugador, string> = {
  rojo: '#C41E3A',
  azul: '#0047AB',
  verde: '#228B22',
  amarillo: '#DAA520'
};

interface Ficha {
  id: number;
  estado: string;
  posicion?: number;
  posicion_meta?: number | null;
}

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
  todasLasFichas?: Ficha[]; // Todas las fichas del jugador actual
  dadosUsados?: number[]; // Array de dados ya usados [1, 2]
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
  todasLasFichas = [],
  dadosUsados = [],
  onSeleccionarDado,
  onCerrar
}) => {
  if (!visible) return null;

  const colorFicha = COLORES[fichaColor];
  const ambosDisponibles = !dado1Usado && !dado2Usado;

  // ⭐ SUMA OBLIGATORIA: Contar fichas movibles REALES (que puedan usar AL MENOS un dado)
  // Replicando la lógica del backend (game_manager.py líneas 781-796)
  let fichasMovibles = 0;
  
  for (const f of todasLasFichas) {
    // Ignorar fichas bloqueadas (en cárcel) o que ya llegaron a META
    if (f.estado === 'BLOQUEADO' || f.estado === 'META') {
      continue;
    }
    
    // Fichas EN_JUEGO en el tablero principal SIEMPRE pueden moverse
    if (f.estado === 'EN_JUEGO' && (f.posicion_meta === undefined || f.posicion_meta === null)) {
      fichasMovibles += 1;
    }
    // Fichas en CAMINO_META: solo contar si pueden usar AL MENOS un dado individual
    else if (f.estado === 'CAMINO_META' && f.posicion_meta !== undefined && f.posicion_meta !== null) {
      const pasosRestantesF = 7 - f.posicion_meta;
      // Verificar si puede usar algún dado individual (no suma)
      if (dado1 <= pasosRestantesF || dado2 <= pasosRestantesF) {
        fichasMovibles += 1;
      }
    }
  }

  // Verificar si debemos forzar el uso de la suma
  const enCaminoMeta = fichaEstado === 'CAMINO_META';
  const fichaCercaMeta = fichaPosicion !== undefined 
    ? calcularPasosAEntradaMeta(fichaPosicion, fichaColor) !== null
    : false;
  
  // ⭐ FORZAR SUMA cuando:
  // - Solo hay 1 ficha movible
  // - La ficha NO está en camino a meta
  // - La ficha NO está cerca de su entrada a meta (8 pasos o menos)
  // - NO se han usado dados aún (ambos disponibles)
  const debeUsarSumaObligatoria = 
    fichasMovibles === 1 && 
    !enCaminoMeta && 
    !fichaCercaMeta && 
    dadosUsados.length === 0;

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

  // Calcular pasos restantes para llegar a la meta
  let pasosRestantes: number | null = null;
  let mensaje: string = '';
  
  if (fichaEstado === 'CAMINO_META' && posicionMeta !== undefined && posicionMeta !== null) {
    // Caso 1: Ficha YA está en el camino final a la meta (sv1, sv2, ..., sv8/META)
    // Cada posicion_meta representa una casilla del camino: 0=sv1, 1=sv2, ..., 7=sv8/META
    pasosRestantes = Math.max(0, 7 - posicionMeta);
    mensaje = `Faltan ${pasosRestantes} paso(s) para META`;
  } else if (fichaEstado === 'EN_JUEGO' && fichaPosicion !== undefined && fichaPosicion !== null) {
    // Caso 2: Ficha está en el tablero principal, cerca de su entrada a meta
    const pasosAEntrada = calcularPasosAEntradaMeta(fichaPosicion, fichaColor);
    
    if (pasosAEntrada !== null) {
      // La ficha está cerca de su entrada (8 pasos o menos)
      // Total de pasos = pasos hasta entrada + 8 pasos del camino meta
      pasosRestantes = pasosAEntrada + 8;
      mensaje = `A ${pasosAEntrada} paso(s) de entrar al camino final (+8 a META)`;
    }
    // Si pasosAEntrada es null, la ficha está lejos y puede moverse libremente
  }

  const dado1DisabledByMeta = pasosRestantes !== null ? dado1 > pasosRestantes : false;
  const dado2DisabledByMeta = pasosRestantes !== null ? dado2 > pasosRestantes : false;
  const sumaDisabledByMeta = pasosRestantes !== null ? suma > pasosRestantes : false;

  // ⭐ BLOQUEAR dados individuales si debe usar suma obligatoria
  const dado1Disabled = dado1Usado || dado1DisabledByMeta || debeUsarSumaObligatoria;
  const dado2Disabled = dado2Usado || dado2DisabledByMeta || debeUsarSumaObligatoria;

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
        {pasosRestantes !== null && mensaje && (
          <div className="text-center text-sm text-gray-600 mb-2 px-2">
            {mensaje}
          </div>
        )}

        {/* Mostrar mensaje de suma obligatoria */}
        {debeUsarSumaObligatoria && ambosDisponibles && (
          <div className="text-center text-sm text-purple-600 font-semibold mb-2 px-2 bg-purple-50 rounded py-1">
            ⚠️ Debes usar la SUMA (solo 1 ficha disponible)
          </div>
        )}

        {/* Opciones de dados */}
        <div className="space-y-2">
          {/* Dado 1 */}
          <button
            onClick={() => onSeleccionarDado(1)}
            disabled={dado1Disabled}
            className={`w-full flex items-center justify-between px-3 py-2 rounded-lg transition-all
              ${dado1Disabled
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
            disabled={dado2Disabled}
            className={`w-full flex items-center justify-between px-3 py-2 rounded-lg transition-all
              ${dado2Disabled
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
