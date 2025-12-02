import { useState, useEffect, useCallback, useRef } from 'react';
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
  puedeRelanzar: boolean;
  
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
  
  // ⭐ NUEVO: Premio de 3 dobles
  premioTresDoblesActivo: boolean;
  fichasElegiblesPremio: Array<{ id: number; color: ColorJugador; posicion: number }>;
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
  // Indica que el jugador consumió una tirada doble y tiene permiso para relanzar
  const [puedeRelanzar, setPuedeRelanzar] = useState(false);
  // Ref para leer el estado más reciente de dadosUsados dentro de closures
  const dadosUsadosRef = useRef<number[]>([]);
  // Ref para evitar enviar SACAR_TODAS múltiples veces
  const sacarTodasEnviadoRef = useRef(false);
  
  // Ficha seleccionada
  const [fichaSeleccionada, setFichaSeleccionada] = useState<{ color: ColorJugador; id: number } | null>(null);
  
  // Eventos
  const [ultimaCaptura, setUltimaCaptura] = useState<CapturaInfo | null>(null);
  const [ultimoMovimiento, setUltimoMovimiento] = useState<{ desde: number; hasta: number } | null>(null);
  
  // Juego terminado
  const [juegoTerminado, setJuegoTerminado] = useState(false);
  const [ganador, setGanador] = useState<{ nombre: string; color: ColorJugador } | null>(null);
  
  // ⭐ NUEVO: Premio de 3 dobles
  const [premioTresDoblesActivo, setPremioTresDoblesActivo] = useState(false);
  const [fichasElegiblesPremio, setFichasElegiblesPremio] = useState<Array<{ id: number; color: ColorJugador; posicion: number }>>([]);
  
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
          setDadosUsados(() => {
            dadosUsadosRef.current = [];
            return [];
          });
          setPuedeRelanzar(false);
          setFichaSeleccionada(null);
          sacarTodasEnviadoRef.current = false; // Resetear para nuevo turno
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
        setDadosUsados(() => {
          dadosUsadosRef.current = [];
          return [];
        });
        // Nueva tirada: cancelar cualquier permiso previo de relanzar
        setPuedeRelanzar(false);
        
        // AUTOMATICO: Si es mi turno, son dobles, y TODAS las fichas están en cárcel
        // enviar SACAR_TODAS automáticamente (como el cliente Python)
        // Usar ref para evitar enviar múltiples veces
        if (esMiTurno && msg.es_doble && miColor && !sacarTodasEnviadoRef.current) {
          const miJugador = jugadores.find(j => j.color === miColor);
          if (miJugador) {
            const todasEnCarcel = miJugador.fichas.every(f => f.estado === 'BLOQUEADO');
            if (todasEnCarcel && miJugador.fichas.length === 4) {
              console.log('🔓 Todas en cárcel + dobles! Enviando SACAR_TODAS automáticamente...');
              sacarTodasEnviadoRef.current = true; // Marcar que ya se envió
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
        console.log('📋 TABLERO recibido - actualizando estado...');
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
        
        // ⭐ Si el popup de premio estaba activo, cerrarlo ahora
        // (el servidor procesó la selección y envió el tablero actualizado)
        if (premioTresDoblesActivo) {
          console.log('🏆 Cerrando popup de premio - selección procesada');
          setPremioTresDoblesActivo(false);
          setFichasElegiblesPremio([]);
        }
        
        // Forzar una copia profunda para asegurar que React detecte el cambio
        const jugadoresActualizados = JSON.parse(JSON.stringify(msg.jugadores));
        console.log('📋 TABLERO - Seteando jugadores:', jugadoresActualizados.length, 'jugadores');
        console.log('📋 TABLERO - Mi color es:', miColor);
        const miJugadorNuevo = jugadoresActualizados.find((j: JugadorTablero) => j.color === miColor);
        if (miJugadorNuevo) {
          console.log('📋 TABLERO - Mis fichas ahora:', miJugadorNuevo.fichas.map((f: any) => ({id: f.id, estado: f.estado, pos: f.posicion})));
        }
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
        
        // ⭐ Si el popup de premio estaba activo, cerrarlo
        if (premioTresDoblesActivo) {
          console.log('🏆 Cerrando popup de premio - movimiento confirmado');
          setPremioTresDoblesActivo(false);
          setFichasElegiblesPremio([]);
        }
        
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
      
      case 'PREMIO_TRES_DOBLES': {
        // ⭐ El jugador sacó 3 dobles y debe elegir una ficha para enviar a META
        console.log('🏆 Premio de 3 dobles activado!', lastMessage);
        const fichasElegibles = lastMessage.fichas_elegibles || [];
        setFichasElegiblesPremio(fichasElegibles.map((f: any) => ({
          id: f.id,
          color: f.color,
          posicion: f.posicion
        })));
        setPremioTresDoblesActivo(true);
        // Deseleccionar cualquier ficha seleccionada
        setFichaSeleccionada(null);
        break;
      }
      
      case 'VICTORIA': {
        setJuegoTerminado(true);
        setGanador({ nombre: lastMessage.ganador, color: lastMessage.color });
        break;
      }
      
      case 'INFO': {
        // ⭐ Si recibimos un INFO mientras el premio está activo, probablemente 
        // es la confirmación del servidor (ej: "X envió su ficha a META con el premio")
        if (premioTresDoblesActivo) {
          console.log('🏆 Cerrando popup de premio - INFO recibido del servidor');
          setPremioTresDoblesActivo(false);
          setFichasElegiblesPremio([]);
        }
        break;
      }
    }
    
    // Nota: no reseteamos los dados aquí de forma global. El servidor
    // controla cuándo termina el turno (via mensajes `TURNO`/`TABLERO`).
    // El cliente sólo actualizará `dadosLanzados` cuando reciba mensajes
    // explícitos del servidor o cuando se consuman ambos dados localmente.
  }, [lastMessage, miColor, esMiTurno, jugadores, send, turnoActual, miId]);
  
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
    // Permitir calcular fichas movibles si es mi turno y hay dados lanzados
    // o si tengo permiso para relanzar tras haber consumido dobles.
    if (!esMiTurno || (!dadosLanzados && !puedeRelanzar) || !miColor) return [];
    
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
  }, [esMiTurno, dadosLanzados, miColor, jugadores, puedeRelanzar]);
  
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
    // Permite lanzar si es mi turno y no hay dados activos,
    // o si estoy en estado de relanzar por haber consumido dobles
    if (!esMiTurno || (dadosLanzados && !puedeRelanzar)) return;

    // Si venimos de un relanzar por dobles, limpiar estado local antes de lanzar
    if (puedeRelanzar) {
      // Preparamos para la nueva tirada: ocultar/invalidar dados actuales y limpiar usados
      setDadosLanzados(false);
      setDadosUsados(() => {
        dadosUsadosRef.current = [];
        return [];
      });
      setPuedeRelanzar(false);
    }

    send({ tipo: 'LANZAR_DADOS' });
  }, [esMiTurno, dadosLanzados, puedeRelanzar, send]);
  
  const sacarDeCarcel = useCallback(() => {
    if (!esMiTurno || !esDoble) return;
    send({ tipo: 'SACAR_CARCEL' });
  }, [esMiTurno, esDoble, send]);
  
  const sacarTodasDeCarcel = useCallback(() => {
    if (!esMiTurno || !esDoble) return;
    send({ tipo: 'SACAR_TODAS' });
  }, [esMiTurno, esDoble, send]);
  
  const moverFicha = useCallback((fichaId: number, dadoElegido: 1 | 2 | 3) => {
    if (!esMiTurno || !dadosLanzados) {
      console.warn('Movimiento no permitido: no es tu turno o no hay dados lanzados');
      return;
    }

    // Verificar que el dado no haya sido usado (si no es la suma)
    if (dadoElegido !== 3 && dadosUsados.includes(dadoElegido)) {
      console.warn(`Dado ${dadoElegido} ya fue usado`);
      return;
    }

    console.log(`Enviando movimiento: fichaId=${fichaId}, dado=${dadoElegido}`);
    send({ tipo: 'MOVER_FICHA', ficha_id: fichaId, dado_elegido: dadoElegido });

    // Registrar dado usado localmente
    if (dadoElegido === 3) {
      // Usar la suma consume ambos dados
      setDadosUsados(() => {
        const next = [1, 2];
        dadosUsadosRef.current = next;
        return next;
      });
    } else {
      setDadosUsados(prev => {
        const next = Array.from(new Set([...prev, dadoElegido]));
        dadosUsadosRef.current = next;
        return next;
      });
    }

    // Si ambos dados ya fueron usados, decidir comportamiento local:
    // - Si fueron dobles, permitir relanzar (limpiar estado de dados para que pueda lanzar otra vez)
    // - Si no fueron dobles, marcar que no hay más acciones locales (el servidor dará el siguiente turno)
    setTimeout(() => {
      const usados = dadoElegido === 3 ? [1, 2] : Array.from(new Set([...dadosUsadosRef.current, dadoElegido]));
      const ambosUsados = usados.includes(1) && usados.includes(2);

      if (ambosUsados) {
        if (esDoble) {
          console.log('Dobles consumidos: habilitando relanzar.');
          // Mantener los dados visibles (dadosLanzados = true) pero marcar que
          // ambos ya fueron usados. El permiso de relanzar permitirá al jugador
          // lanzar de nuevo cuando lo desee.
          setDadosUsados(() => {
            const next: number[] = [1, 2];
            dadosUsadosRef.current = next;
            return next;
          });
          setPuedeRelanzar(true);
          // mantener esMiTurno true
          setEsMiTurno(true);
        } else {
          console.log('Ambos dados usados, esperando actualización del servidor.');
          setDadosLanzados(false);
          setPuedeRelanzar(false);
        }
      }
    }, 20);

    setFichaSeleccionada(null);
  }, [esMiTurno, dadosLanzados, dadosUsados, send, esDoble]);
  
  const seleccionarFicha = useCallback((color: ColorJugador, id: number) => {
    if (!esMiTurno || color !== miColor) return;
    setFichaSeleccionada({ color, id });
  }, [esMiTurno, miColor]);
  
  const deseleccionarFicha = useCallback(() => {
    setFichaSeleccionada(null);
  }, []);
  
  // Calcular si puede tomar acción: hay dados disponibles o permiso para relanzar
  const puedeTomarAccion = esMiTurno && (dadosLanzados || puedeRelanzar);
  
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
      puedeRelanzar,
      fichasMovibles,
      fichasEnCarcel,
      ultimaCaptura,
      ultimoMovimiento,
      juegoTerminado,
      ganador,
      premioTresDoblesActivo,
      fichasElegiblesPremio
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
