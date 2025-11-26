import type { ColorJugador } from '../types/gameTypes';

// ============================================
// MAPEO DE POSICIONES LÓGICAS A VISUALES
// ============================================
// El backend usa posiciones 0-67 para el tablero principal
// Aquí mapeamos cada posición a coordenadas de grid CSS

interface PosicionVisual {
  gridRow: string;
  gridColumn: string;
}

// Mapeo completo de las 68 casillas del tablero
// Las posiciones corresponden a la numeración del backend (0-indexed)
export const POSICIONES_TABLERO: Record<number, PosicionVisual> = {
  // BRAZO INFERIOR (amarillo) - Columna derecha subiendo
  0: { gridRow: '19', gridColumn: '11' },   // Casilla 1
  1: { gridRow: '18', gridColumn: '11' },   // Casilla 2
  2: { gridRow: '17', gridColumn: '11' },   // Casilla 3
  3: { gridRow: '16', gridColumn: '11' },   // Casilla 4
  4: { gridRow: '15', gridColumn: '11' },   // Casilla 5 - SALIDA AMARILLO
  5: { gridRow: '14', gridColumn: '11' },   // Casilla 6
  6: { gridRow: '13', gridColumn: '11' },   // Casilla 7
  7: { gridRow: '12', gridColumn: '11' },   // Casilla 8
  
  // BRAZO DERECHO (azul) - Fila inferior hacia derecha
  8: { gridRow: '11', gridColumn: '12' },   // Casilla 9
  9: { gridRow: '11', gridColumn: '13' },   // Casilla 10
  10: { gridRow: '11', gridColumn: '14' },  // Casilla 11
  11: { gridRow: '11', gridColumn: '15' },  // Casilla 12 - SEGURO
  12: { gridRow: '11', gridColumn: '16' },  // Casilla 13
  13: { gridRow: '11', gridColumn: '17' },  // Casilla 14
  14: { gridRow: '11', gridColumn: '18' },  // Casilla 15
  15: { gridRow: '11', gridColumn: '19' },  // Casilla 16
  16: { gridRow: '10', gridColumn: '19' },  // Casilla 17 - SEGURO META AZUL
  17: { gridRow: '9', gridColumn: '19' },   // Casilla 18
  18: { gridRow: '9', gridColumn: '18' },   // Casilla 19
  19: { gridRow: '9', gridColumn: '17' },   // Casilla 20
  20: { gridRow: '9', gridColumn: '16' },   // Casilla 21
  21: { gridRow: '9', gridColumn: '15' },   // Casilla 22 - SALIDA AZUL
  22: { gridRow: '9', gridColumn: '14' },   // Casilla 23
  23: { gridRow: '9', gridColumn: '13' },   // Casilla 24
  24: { gridRow: '9', gridColumn: '12' },   // Casilla 25
  
  // BRAZO SUPERIOR (rojo) - Columna derecha bajando
  25: { gridRow: '8', gridColumn: '11' },   // Casilla 26
  26: { gridRow: '7', gridColumn: '11' },   // Casilla 27
  27: { gridRow: '6', gridColumn: '11' },   // Casilla 28
  28: { gridRow: '5', gridColumn: '11' },   // Casilla 29 - SEGURO
  29: { gridRow: '4', gridColumn: '11' },   // Casilla 30
  30: { gridRow: '3', gridColumn: '11' },   // Casilla 31
  31: { gridRow: '2', gridColumn: '11' },   // Casilla 32
  32: { gridRow: '1', gridColumn: '11' },   // Casilla 33
  33: { gridRow: '1', gridColumn: '10' },   // Casilla 34 - SEGURO META ROJO
  34: { gridRow: '1', gridColumn: '9' },    // Casilla 35
  35: { gridRow: '2', gridColumn: '9' },    // Casilla 36
  36: { gridRow: '3', gridColumn: '9' },    // Casilla 37
  37: { gridRow: '4', gridColumn: '9' },    // Casilla 38
  38: { gridRow: '5', gridColumn: '9' },    // Casilla 39 - SALIDA ROJO
  39: { gridRow: '6', gridColumn: '9' },    // Casilla 40
  40: { gridRow: '7', gridColumn: '9' },    // Casilla 41
  41: { gridRow: '8', gridColumn: '9' },    // Casilla 42
  
  // BRAZO IZQUIERDO (verde) - Fila superior hacia izquierda
  42: { gridRow: '9', gridColumn: '8' },    // Casilla 43
  43: { gridRow: '9', gridColumn: '7' },    // Casilla 44
  44: { gridRow: '9', gridColumn: '6' },    // Casilla 45
  45: { gridRow: '9', gridColumn: '5' },    // Casilla 46 - SEGURO
  46: { gridRow: '9', gridColumn: '4' },    // Casilla 47
  47: { gridRow: '9', gridColumn: '3' },    // Casilla 48
  48: { gridRow: '9', gridColumn: '2' },    // Casilla 49
  49: { gridRow: '9', gridColumn: '1' },    // Casilla 50
  50: { gridRow: '10', gridColumn: '1' },   // Casilla 51 - SEGURO META VERDE
  51: { gridRow: '11', gridColumn: '1' },   // Casilla 52
  52: { gridRow: '11', gridColumn: '2' },   // Casilla 53
  53: { gridRow: '11', gridColumn: '3' },   // Casilla 54
  54: { gridRow: '11', gridColumn: '4' },   // Casilla 55
  55: { gridRow: '11', gridColumn: '5' },   // Casilla 56 - SALIDA VERDE
  56: { gridRow: '11', gridColumn: '6' },   // Casilla 57
  57: { gridRow: '11', gridColumn: '7' },   // Casilla 58
  58: { gridRow: '11', gridColumn: '8' },   // Casilla 59
  
  // BRAZO INFERIOR (amarillo) - Columna izquierda bajando
  59: { gridRow: '12', gridColumn: '9' },   // Casilla 60
  60: { gridRow: '13', gridColumn: '9' },   // Casilla 61
  61: { gridRow: '14', gridColumn: '9' },   // Casilla 62
  62: { gridRow: '15', gridColumn: '9' },   // Casilla 63 - SEGURO
  63: { gridRow: '16', gridColumn: '9' },   // Casilla 64
  64: { gridRow: '17', gridColumn: '9' },   // Casilla 65
  65: { gridRow: '18', gridColumn: '9' },   // Casilla 66
  66: { gridRow: '19', gridColumn: '9' },   // Casilla 67
  67: { gridRow: '19', gridColumn: '10' },  // Casilla 68 - SEGURO META AMARILLO
};

// Posiciones de las cárceles por color (para fichas bloqueadas)
export const POSICIONES_CARCEL: Record<ColorJugador, PosicionVisual> = {
  rojo: { gridRow: '1/9', gridColumn: '1/9' },
  azul: { gridRow: '1/9', gridColumn: '12/20' },
  verde: { gridRow: '12/20', gridColumn: '1/9' },
  amarillo: { gridRow: '12/20', gridColumn: '12/20' }
};

// Posiciones dentro de la cárcel para cada ficha (0-3)
export const POSICIONES_FICHAS_CARCEL: Record<ColorJugador, PosicionVisual[]> = {
  rojo: [
    { gridRow: '3', gridColumn: '3' },
    { gridRow: '3', gridColumn: '6' },
    { gridRow: '6', gridColumn: '3' },
    { gridRow: '6', gridColumn: '6' }
  ],
  azul: [
    { gridRow: '3', gridColumn: '14' },
    { gridRow: '3', gridColumn: '17' },
    { gridRow: '6', gridColumn: '14' },
    { gridRow: '6', gridColumn: '17' }
  ],
  verde: [
    { gridRow: '14', gridColumn: '3' },
    { gridRow: '14', gridColumn: '6' },
    { gridRow: '17', gridColumn: '3' },
    { gridRow: '17', gridColumn: '6' }
  ],
  amarillo: [
    { gridRow: '14', gridColumn: '14' },
    { gridRow: '14', gridColumn: '17' },
    { gridRow: '17', gridColumn: '14' },
    { gridRow: '17', gridColumn: '17' }
  ]
};

// Posiciones del camino a meta por color (0-6, la 7 es la meta final)
export const POSICIONES_CAMINO_META: Record<ColorJugador, PosicionVisual[]> = {
  rojo: [
    { gridRow: '2', gridColumn: '10' },  // sr1
    { gridRow: '3', gridColumn: '10' },  // sr2
    { gridRow: '4', gridColumn: '10' },  // sr3
    { gridRow: '5', gridColumn: '10' },  // sr4
    { gridRow: '6', gridColumn: '10' },  // sr5
    { gridRow: '7', gridColumn: '10' },  // sr6
    { gridRow: '8', gridColumn: '10' },  // sr7
  ],
  azul: [
    { gridRow: '10', gridColumn: '18' }, // sB1
    { gridRow: '10', gridColumn: '17' }, // sB2
    { gridRow: '10', gridColumn: '16' }, // sB3
    { gridRow: '10', gridColumn: '15' }, // sB4
    { gridRow: '10', gridColumn: '14' }, // sB5
    { gridRow: '10', gridColumn: '13' }, // sB6
    { gridRow: '10', gridColumn: '12' }, // sB7
  ],
  verde: [
    { gridRow: '10', gridColumn: '2' },  // sv1
    { gridRow: '10', gridColumn: '3' },  // sv2
    { gridRow: '10', gridColumn: '4' },  // sv3
    { gridRow: '10', gridColumn: '5' },  // sv4
    { gridRow: '10', gridColumn: '6' },  // sv5
    { gridRow: '10', gridColumn: '7' },  // sv6
    { gridRow: '10', gridColumn: '8' },  // sv7
  ],
  amarillo: [
    { gridRow: '18', gridColumn: '10' }, // sa1
    { gridRow: '17', gridColumn: '10' }, // sa2
    { gridRow: '16', gridColumn: '10' }, // sa3
    { gridRow: '15', gridColumn: '10' }, // sa4
    { gridRow: '14', gridColumn: '10' }, // sa5
    { gridRow: '13', gridColumn: '10' }, // sa6
    { gridRow: '12', gridColumn: '10' }, // sa7
  ]
};

// Centro del tablero (meta final)
export const POSICION_CENTRO: PosicionVisual = { gridRow: '9/12', gridColumn: '9/12' };

// ============================================
// FUNCIONES HELPER
// ============================================

/**
 * Obtiene la posición visual de una ficha según su estado y posición lógica
 */
export function obtenerPosicionVisual(
  estado: string,
  posicion: number,
  posicionMeta: number | undefined,
  color: ColorJugador,
  fichaId: number
): PosicionVisual | null {
  switch (estado) {
    case 'BLOQUEADO':
      // Ficha en cárcel
      return POSICIONES_FICHAS_CARCEL[color]?.[fichaId] || null;
    
    case 'EN_JUEGO':
      // Ficha en tablero principal
      return POSICIONES_TABLERO[posicion] || null;
    
    case 'CAMINO_META':
      // Ficha en camino a meta
      if (posicionMeta !== undefined && posicionMeta >= 0 && posicionMeta < 7) {
        return POSICIONES_CAMINO_META[color]?.[posicionMeta] || null;
      }
      return null;
    
    case 'META':
      // Ficha llegó a la meta (centro)
      return POSICION_CENTRO;
    
    default:
      return null;
  }
}

/**
 * Verifica si una casilla es segura
 */
export function esCasillaSeguira(posicion: number): boolean {
  // Casillas seguras (0-indexed): 11, 16, 28, 33, 45, 50, 62, 67
  const casillasSeguras = [11, 16, 28, 33, 45, 50, 62, 67];
  return casillasSeguras.includes(posicion);
}

/**
 * Verifica si una casilla es de salida
 */
export function esCasillaSalida(posicion: number, color: ColorJugador): boolean {
  const salidas: Record<ColorJugador, number> = {
    rojo: 38,
    verde: 55,
    amarillo: 4,
    azul: 21
  };
  return salidas[color] === posicion;
}

/**
 * Agrupa fichas por posición para mostrarlas juntas
 */
export interface FichaEnPosicion {
  id: number;
  color: ColorJugador;
  estado: string;
}

export function agruparFichasPorPosicion(
  jugadores: Array<{ color: ColorJugador; fichas: Array<{ id: number; estado: string; posicion: number; posicion_meta?: number }> }>
): Map<string, FichaEnPosicion[]> {
  const mapa = new Map<string, FichaEnPosicion[]>();
  
  for (const jugador of jugadores) {
    for (const ficha of jugador.fichas) {
      const posVisual = obtenerPosicionVisual(
        ficha.estado,
        ficha.posicion,
        ficha.posicion_meta,
        jugador.color,
        ficha.id
      );
      
      if (posVisual) {
        const key = `${posVisual.gridRow}-${posVisual.gridColumn}`;
        const fichasEnPos = mapa.get(key) || [];
        fichasEnPos.push({
          id: ficha.id,
          color: jugador.color,
          estado: ficha.estado
        });
        mapa.set(key, fichasEnPos);
      }
    }
  }
  
  return mapa;
}
