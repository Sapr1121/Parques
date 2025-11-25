import { useState, useEffect, useCallback } from 'react';
import { useSocket } from '../../contexts/SocketContext';
import type { 
  JugadorTablero, 
  ColorJugador, 
  MensajeDados,
  MensajeTablero,
  MensajeTurno,
  MensajeMovimientoOK,
  CapturaInfo
} from '../types/gameTypes';

// Estado del juego
interface GameState {
  // Jugadores
  jugadores: JugadorTablero[];
  miColor: ColorJugador | null;
  miNombre: string;
  miId: number;
  
  // Turno
  turnoActual: number;
  esMiTurno: boolean;
  jugadorActual: { nombre: string; color: ColorJugador } | null;
  
  // Dados
  dadosLanzados: boolean;
  dado1: number;
  dado2: number;
  suma: number;
  esDoble: boolean;
  doblesConsecutivos: number;
  dadosUsados: number[];
  
  // Estado de acción
  puedeTomarAccion: boolean;
  fichasMovibles: Array<{ color: ColorJugador; id: number; posicion: number }>;
  fichasEnCarcel: Array<{ color: ColorJugador; id: number }>;
  
  // Eventos
  ultimaCaptura: CapturaInfo | null;
  ultimoMovimiento: { desde: number; hasta: number } | null;
  
  // Juego
  juegoTerminado: boolean;
  ganador: { nombre: string; color: ColorJugador } | null;
}

// Acciones disponibles
interface GameActions {
  lanzarDados: () => void;
  sacarDeCarcel: () => void;
  sacarTodasDeCarcel: () => void;
  moverFicha: (fichaId: number, dadoElegido: 1 | 2 | 3) => void;
  seleccionarFicha: (color: ColorJugador, id: number) => void;
  deseleccionarFicha: () => void;
}

export interface UseGameStateReturn {
  state: GameState;
  actions: GameActions;
  fichaSeleccionada: { color: ColorJugador; id: number } | null;
}

export const useGameState = (
  miColor: ColorJugador | null,
  miNombre: string,
  miId: number
): UseGameStateReturn => {
  const { send, lastMessage, messageQueue, clearQueue } = useSocket();
  
  // Estado principal
  const [jugadores, setJugadores] = useState<JugadorTablero[]>([]);
  const [turnoActual, setTurnoActual] = useState(0);
  const [esMiTurno, setEsMiTurno] = useState(false);
  const [jugadorActual, setJugadorActual] = useState<{ nombre: string; color: ColorJugador } | null>(null);
  
  // Estado de dados
  const [dadosLanzados, setDadosLanzados] = useState(false);
  const [dado1, setDado1] = useState(0);
  const [dado2, setDado2] = useState(0);
  const [suma, setSuma] = useState(0);
  const [esDoble, setEsDoble] = useState(false);
  const [doblesConsecutivos, setDoblesConsecutivos] = useState(0);
  const [dadosUsados, setDadosUsados] = useState<number[]>([]);
  
  // Ficha seleccionada
  const [fichaSeleccionada, setFichaSeleccionada] = useState<{ color: ColorJugador; id: number } | null>(null);
  
  // Eventos
  const [ultimaCaptura, setUltimaCaptura] = useState<CapturaInfo | null>(null);
  const [ultimoMovimiento, setUltimoMovimiento] = useState<{ desde: number; hasta: number } | null>(null);
  
  // Juego terminado
  const [juegoTerminado, setJuegoTerminado] = useState(false);
  const [ganador, setGanador] = useState<{ nombre: string; color: ColorJugador } | null>(null);
  
  // Procesar mensajes del servidor
  useEffect(() => {
    if (!lastMessage) return;
    
    console.log('🎮 useGameState recibió:', lastMessage);
    
    switch (lastMessage.tipo) {
      case 'TURNO': {
        const msg = lastMessage as MensajeTurno;
        setJugadorActual({ nombre: msg.nombre, color: msg.color });
        const esMyTurno = msg.color === miColor;
        setEsMiTurno(esMyTurno);
        
        // Resetear estado de dados si es un nuevo turno
        if (esMyTurno) {
          setDadosLanzados(false);
          setDadosUsados([]);
          setFichaSeleccionada(null);
        }
        break;
      }
      
      case 'DADOS': {
        const msg = lastMessage as MensajeDados;
        setDado1(msg.dado1);
        setDado2(msg.dado2);
        setSuma(msg.suma);
        setEsDoble(msg.es_doble);
        setDadosLanzados(true);
        setDadosUsados([]);
        
        // AUTOMATICO: Si es mi turno, son dobles, y TODAS las fichas están en cárcel
        // enviar SACAR_TODAS automáticamente (como el cliente Python)
        if (esMiTurno && msg.es_doble && miColor) {
          const miJugador = jugadores.find(j => j.color === miColor);
          if (miJugador) {
            const todasEnCarcel = miJugador.fichas.every(f => f.estado === 'BLOQUEADO');
            if (todasEnCarcel && miJugador.fichas.length === 4) {
              console.log('🔓 Todas en cárcel + dobles! Enviando SACAR_TODAS automáticamente...');
              // Pequeño delay para que el UI muestre los dados primero
              setTimeout(() => {
                send({ tipo: 'SACAR_TODAS' });
              }, 500);
            }
          }
        }
        break;
      }
      
      case 'TABLERO': {
        const msg = lastMessage as MensajeTablero;
        console.log('📋 TABLERO recibido - COMPLETO:', JSON.stringify(msg, null, 2));
        console.log('📋 TABLERO - Fichas por jugador:', {
          jugadores: msg.jugadores.map(j => ({
            nombre: j.nombre,
            color: j.color,
            bloqueadas: j.bloqueadas,
            en_juego: j.en_juego,
            en_meta: j.en_meta,
            fichas: j.fichas.map(f => ({ 
              id: f.id, 
              estado: f.estado, 
              posicion: f.posicion,
              posicion_meta: f.posicion_meta 
            }))
          }))
        });
        
        // Forzar una copia profunda para asegurar que React detecte el cambio
        const jugadoresActualizados = JSON.parse(JSON.stringify(msg.jugadores));
        setJugadores(jugadoresActualizados);
        setTurnoActual(msg.turno_actual);
        setDadosLanzados(msg.dados_lanzados);
        setDado1(msg.ultimo_dado1);
        setDado2(msg.ultimo_dado2);
        setSuma(msg.ultima_suma);
        setEsDoble(msg.ultimo_es_doble);
        setDoblesConsecutivos(msg.dobles_consecutivos);
        break;
      }
      
      case 'MOVIMIENTO_OK': {
        const msg = lastMessage as MensajeMovimientoOK;
        console.log('✅ MOVIMIENTO_OK recibido:', {
          nombre: msg.nombre,
          color: msg.color,
          desde: msg.desde,
          hasta: msg.hasta,
          accion: msg.accion
        });
        
        setUltimoMovimiento({ desde: msg.desde, hasta: msg.hasta });
        setFichaSeleccionada(null);
        
        // Registrar dados usados si fue un movimiento individual
        if (msg.accion !== 'liberar_ficha') {
          // El servidor debería indicar qué dado se usó
        }
        
        // Procesar capturas
        if (msg.capturas && msg.capturas.length > 0) {
          setUltimaCaptura(msg.capturas[0]);
        }
        break;
      }
      
      case 'CAPTURA': {
        const capturado = lastMessage.capturado;
        setUltimaCaptura(capturado);
        break;
      }
      
      case 'VICTORIA': {
        setJuegoTerminado(true);
        setGanador({ nombre: lastMessage.ganador, color: lastMessage.color });
        break;
      }
    }
  }, [lastMessage, miColor, esMiTurno, jugadores, send]);
  
  // Procesar cola de mensajes (para mensajes que llegaron muy rápido)
  useEffect(() => {
    if (messageQueue.length === 0) return;
    
    console.log(`📬 Procesando cola de mensajes: ${messageQueue.length} mensajes`);
    
    // Buscar específicamente mensajes TABLERO que no se procesaron
    const tableroMsgs = messageQueue.filter(m => m.tipo === 'TABLERO');
    if (tableroMsgs.length > 0) {
      // Usar el último mensaje TABLERO
      const ultimoTablero = tableroMsgs[tableroMsgs.length - 1];
      console.log('📋 Procesando TABLERO desde cola:', ultimoTablero);
      
      const jugadoresActualizados = JSON.parse(JSON.stringify(ultimoTablero.jugadores));
      setJugadores(jugadoresActualizados);
      setTurnoActual(ultimoTablero.turno_actual);
      setDadosLanzados(ultimoTablero.dados_lanzados);
      setDado1(ultimoTablero.ultimo_dado1);
      setDado2(ultimoTablero.ultimo_dado2);
      setSuma(ultimoTablero.ultima_suma);
      setEsDoble(ultimoTablero.ultimo_es_doble);
      setDoblesConsecutivos(ultimoTablero.dobles_consecutivos);
    }
    
    // Limpiar la cola después de procesar
    clearQueue();
  }, [messageQueue, clearQueue]);
  
  // Calcular fichas movibles
  const calcularFichasMovibles = useCallback((): Array<{ color: ColorJugador; id: number; posicion: number }> => {
    if (!esMiTurno || !dadosLanzados || !miColor) return [];
    
    const miJugador = jugadores.find(j => j.color === miColor);
    if (!miJugador) return [];
    
    const movibles: Array<{ color: ColorJugador; id: number; posicion: number }> = [];
    
    for (const ficha of miJugador.fichas) {
      if (ficha.estado === 'EN_JUEGO' || ficha.estado === 'CAMINO_META') {
        movibles.push({
          color: ficha.color,
          id: ficha.id,
          posicion: ficha.posicion
        });
      }
    }
    
    return movibles;
  }, [esMiTurno, dadosLanzados, miColor, jugadores]);
  
  // Calcular fichas en cárcel
  const calcularFichasEnCarcel = useCallback((): Array<{ color: ColorJugador; id: number }> => {
    if (!miColor) return [];
    
    const miJugador = jugadores.find(j => j.color === miColor);
    if (!miJugador) return [];
    
    return miJugador.fichas
      .filter(f => f.estado === 'BLOQUEADO')
      .map(f => ({ color: f.color, id: f.id }));
  }, [miColor, jugadores]);
  
  // Acciones
  const lanzarDados = useCallback(() => {
    if (!esMiTurno || dadosLanzados) return;
    send({ tipo: 'LANZAR_DADOS' });
  }, [esMiTurno, dadosLanzados, send]);
  
  const sacarDeCarcel = useCallback(() => {
    if (!esMiTurno || !esDoble) return;
    send({ tipo: 'SACAR_CARCEL' });
  }, [esMiTurno, esDoble, send]);
  
  const sacarTodasDeCarcel = useCallback(() => {
    if (!esMiTurno || !esDoble) return;
    send({ tipo: 'SACAR_TODAS' });
  }, [esMiTurno, esDoble, send]);
  
  const moverFicha = useCallback((fichaId: number, dadoElegido: 1 | 2 | 3) => {
    if (!esMiTurno || !dadosLanzados) return;
    
    // Verificar que el dado no haya sido usado
    if (dadoElegido !== 3 && dadosUsados.includes(dadoElegido)) {
      console.warn(`Dado ${dadoElegido} ya fue usado`);
      return;
    }
    
    send({ tipo: 'MOVER_FICHA', ficha_id: fichaId, dado_elegido: dadoElegido });
    
    // Registrar dado usado localmente
    if (dadoElegido !== 3) {
      setDadosUsados(prev => [...prev, dadoElegido]);
    }
    
    setFichaSeleccionada(null);
  }, [esMiTurno, dadosLanzados, dadosUsados, send]);
  
  const seleccionarFicha = useCallback((color: ColorJugador, id: number) => {
    if (!esMiTurno || color !== miColor) return;
    setFichaSeleccionada({ color, id });
  }, [esMiTurno, miColor]);
  
  const deseleccionarFicha = useCallback(() => {
    setFichaSeleccionada(null);
  }, []);
  
  // Calcular si puede tomar acción
  const puedeTomarAccion = esMiTurno && dadosLanzados;
  
  // Calcular fichas movibles y en cárcel
  const fichasMovibles = calcularFichasMovibles();
  const fichasEnCarcel = calcularFichasEnCarcel();
  
  return {
    state: {
      jugadores,
      miColor,
      miNombre,
      miId,
      turnoActual,
      esMiTurno,
      jugadorActual,
      dadosLanzados,
      dado1,
      dado2,
      suma,
      esDoble,
      doblesConsecutivos,
      dadosUsados,
      puedeTomarAccion,
      fichasMovibles,
      fichasEnCarcel,
      ultimaCaptura,
      ultimoMovimiento,
      juegoTerminado,
      ganador
    },
    actions: {
      lanzarDados,
      sacarDeCarcel,
      sacarTodasDeCarcel,
      moverFicha,
      seleccionarFicha,
      deseleccionarFicha
    },
    fichaSeleccionada
  };
};

export default useGameState;
