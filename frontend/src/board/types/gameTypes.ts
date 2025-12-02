// ============================================
// TIPOS PARA EL ESTADO DEL JUEGO
// ============================================

// Estados posibles de una ficha
export type FichaEstado = 'BLOQUEADO' | 'EN_JUEGO' | 'CAMINO_META' | 'META';

// Colores del juego
export type ColorJugador = 'rojo' | 'azul' | 'verde' | 'amarillo';

// Información de una ficha
export interface Ficha {
  id: number;
  color: ColorJugador;
  estado: FichaEstado;
  posicion: number;      // -1 si está en cárcel, 0-67 si está en tablero
  posicion_meta?: number; // 0-7 si está en camino a meta
}

// Información de un jugador en el tablero
export interface JugadorTablero {
  nombre: string;
  color: ColorJugador;
  fichas: Ficha[];
  bloqueadas: number;
  en_juego: number;
  en_meta: number;
}

// Estado completo del tablero desde el servidor
export interface EstadoTablero {
  jugadores: JugadorTablero[];
  turno_actual: number;
  dados_lanzados: boolean;
  ultimo_dado1: number;
  ultimo_dado2: number;
  ultima_suma: number;
  ultimo_es_doble: boolean;
  dobles_consecutivos: number;
}

// ============================================
// TIPOS DE MENSAJES DEL PROTOCOLO
// ============================================

// Tipos de mensajes
export type TipoMensaje = 
  | 'CONECTAR'
  | 'BIENVENIDA'
  | 'ESPERANDO'
  | 'LISTO'
  | 'INICIO_JUEGO'
  | 'TURNO'
  | 'LANZAR_DADOS'
  | 'DADOS'
  | 'TABLERO'
  | 'SACAR_CARCEL'
  | 'SACAR_TODAS'
  | 'MOVER_FICHA'
  | 'MOVIMIENTO_OK'
  | 'CAPTURA'
  | 'ERROR'
  | 'INFO'
  | 'VICTORIA'
  | 'JUGADOR_DESCONECTADO'
  | 'DETERMINACION_INICIO'
  | 'DETERMINACION_TIRADA'
  | 'DETERMINACION_RESULTADO'
  | 'DETERMINACION_EMPATE'
  | 'DETERMINACION_GANADOR'
  | 'SOLICITAR_COLORES'
  | 'COLORES_DISPONIBLES'
  | 'PREMIO_TRES_DOBLES'
  | 'ELEGIR_FICHA_PREMIO';

// Mensaje base
export interface MensajeBase {
  tipo: TipoMensaje;
}

// Mensaje de bienvenida
export interface MensajeBienvenida extends MensajeBase {
  tipo: 'BIENVENIDA';
  color: ColorJugador;
  jugador_id: number;
  nombre: string;
}

// Mensaje de turno
export interface MensajeTurno extends MensajeBase {
  tipo: 'TURNO';
  nombre: string;
  color: ColorJugador;
}

// Mensaje de dados
export interface MensajeDados extends MensajeBase {
  tipo: 'DADOS';
  dado1: number;
  dado2: number;
  suma: number;
  es_doble: boolean;
}

// Mensaje de tablero
export interface MensajeTablero extends MensajeBase {
  tipo: 'TABLERO';
  jugadores: JugadorTablero[];
  turno_actual: number;
  dados_lanzados: boolean;
  ultimo_dado1: number;
  ultimo_dado2: number;
  ultima_suma: number;
  ultimo_es_doble: boolean;
  dobles_consecutivos: number;
}

// Mensaje de movimiento OK
export interface MensajeMovimientoOK extends MensajeBase {
  tipo: 'MOVIMIENTO_OK';
  nombre: string;
  color: ColorJugador;
  desde: number;
  hasta: number;
  accion?: 'mover' | 'liberar_ficha';
  capturas?: CapturaInfo[];
}

// Información de captura
export interface CapturaInfo {
  nombre: string;
  color: ColorJugador;
  ficha_id: number;
}

// Mensaje de captura
export interface MensajeCaptura extends MensajeBase {
  tipo: 'CAPTURA';
  capturado: CapturaInfo;
}

// Mensaje de error
export interface MensajeError extends MensajeBase {
  tipo: 'ERROR';
  mensaje: string;
}

// Mensaje de victoria
export interface MensajeVictoria extends MensajeBase {
  tipo: 'VICTORIA';
  ganador: string;
  color: ColorJugador;
}

// ⭐ NUEVO: Mensaje de premio por 3 dobles consecutivos
export interface MensajePremioTresDobles extends MensajeBase {
  tipo: 'PREMIO_TRES_DOBLES';
  nombre: string;
  fichas_elegibles: Array<{
    id: number;
    estado: string;
    color: ColorJugador;
    posicion: number;
    posicion_meta: number | null;
    en_camino_meta: boolean;
  }>;
  mensaje: string;
}

// ============================================
// POSICIONES DEL TABLERO
// ============================================

// Casillas de salida por color
export const CASILLAS_SALIDA: Record<ColorJugador, number> = {
  rojo: 38,
  verde: 55,
  amarillo: 4,
  azul: 21
};

// Casillas seguras antes de meta
export const CASILLAS_SEGURO_META: Record<ColorJugador, number> = {
  rojo: 33,
  verde: 50,
  amarillo: 67,
  azul: 16
};

// Casillas seguras normales (0-indexed)
export const CASILLAS_SEGURAS = [11, 16, 28, 33, 45, 50, 62, 67];

// ============================================
// HELPERS
// ============================================

// Obtener emoji según estado de ficha
export const getEstadoEmoji = (estado: FichaEstado): string => {
  const emojis: Record<FichaEstado, string> = {
    'BLOQUEADO': '🔒',
    'EN_JUEGO': '🎮',
    'CAMINO_META': '🎯',
    'META': '🏁'
  };
  return emojis[estado] || '❓';
};

// Obtener color hex según color del jugador
export const getColorHex = (color: ColorJugador): string => {
  const colores: Record<ColorJugador, string> = {
    rojo: '#E00000',
    azul: '#0058E1',
    verde: '#1EC61F',
    amarillo: '#E8E300'
  };
  return colores[color];
};

// Obtener color más oscuro para el borde
export const getColorBorde = (color: ColorJugador): string => {
  const colores: Record<ColorJugador, string> = {
    rojo: '#A00000',
    azul: '#003899',
    verde: '#158915',
    amarillo: '#B0A000'
  };
  return colores[color];
};
