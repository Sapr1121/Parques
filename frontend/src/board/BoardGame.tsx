import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import CenterImg from '../assets/Finish.jpeg';
import BlueJeil from '../assets/BlueJeil.jpeg';
import GreenJeil from '../assets/GreenJeil.jpeg';
import RedJeil from '../assets/RedJeil.jpeg';
import YellowJeil from '../assets/YellowJeil.jpeg';

import Ficha, { GrupoFichas } from './components/Ficha';
import DadosPanel from './components/DadosPanel';
import MiniMenuDados from './components/MiniMenuDados';
import SacadasHUD from './components/SacadasHUD';
import VictoryPopup from './components/VictoryPopup';
import PremioPopup from './components/PremioPopup';
import { useGameState } from './hooks/useGameState';
import { useSocket } from '../contexts/SocketContext';
import { obtenerPosicionVisual } from './utils/posiciones';
import type { ColorJugador, JugadorTablero, FichaEstado } from './types/gameTypes';

const colors = {
  rojo: '#E00000',
  azul: '#0058E1',
  verde: '#1EC61F',
  amarillo: '#E8E300'
};

interface CasillaProps {
  num: number;
  bgColor?: string;
  safe?: boolean;
  corner?: string;
  fichas?: Array<{ id: number; color: ColorJugador; estado: FichaEstado }>;
  fichaSeleccionada?: { color: ColorJugador; id: number } | null;
  fichasSeleccionables?: Array<{ color: ColorJugador; id: number }>;
  onFichaClick?: (color: ColorJugador, id: number, event?: React.MouseEvent) => void;
}

const Casilla: React.FC<CasillaProps> = ({ 
  num, 
  bgColor = 'white', 
  safe = false, 
  corner = '',
  fichas = [],
  fichaSeleccionada,
  fichasSeleccionables = [],
  onFichaClick
}) => {
  const getClipPath = () => {
    switch(corner) {
      case 'top-left': return 'polygon(50% 0, 100% 0, 100% 100%, 0 100%, 0 50%)';
      case 'top-right': return 'polygon(0 0, 50% 0, 100% 50%, 100% 100%, 0 100%)';
      case 'bottom-left': return 'polygon(0 0, 100% 0, 100% 100%, 50% 100%, 0 50%)';
      case 'bottom-right': return 'polygon(0 0, 100% 0, 100% 50%, 50% 100%, 0 100%)';
      default: return 'none';
    }
  };

  return (
    <div 
      className="w-full h-full border-2 border-gray-800 flex items-center justify-center font-bold relative"
      style={{ 
        backgroundColor: bgColor,
        clipPath: getClipPath(),
        fontSize: '20px'
      }}
    >
      <span className="absolute top-1 left-1 text-xs text-gray-500">{num}</span>
      
      {/* Indicador de casilla segura */}
      {safe && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="border-2 border-gray-700 rounded-full bg-transparent" style={{ width: '60px', height: '60px' }}></div>
        </div>
      )}
      
      {/* Fichas en esta casilla */}
      {fichas.length > 0 && (
        <GrupoFichas
          fichas={fichas}
          fichaSeleccionada={fichaSeleccionada}
          fichasSeleccionables={fichasSeleccionables}
          onFichaClick={onFichaClick}
        />
      )}
    </div>
  );
};

interface MetaProps {
  color: string;
  fichas?: Array<{ id: number; color: ColorJugador; estado: FichaEstado }>;
  fichaSeleccionada?: { color: ColorJugador; id: number } | null;
  fichasSeleccionables?: Array<{ color: ColorJugador; id: number }>;
  onFichaClick?: (color: ColorJugador, id: number, event?: React.MouseEvent) => void;
}

const Meta: React.FC<MetaProps> = ({ color, fichas = [], fichaSeleccionada, fichasSeleccionables = [], onFichaClick }) => (
  <div 
    className="w-full h-full border-2 border-gray-800 relative"
    style={{ 
      backgroundColor: color
    }}
  >
    {fichas.length > 0 && (
      <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <GrupoFichas
          fichas={fichas}
          fichaSeleccionada={fichaSeleccionada}
          fichasSeleccionables={fichasSeleccionables}
          onFichaClick={onFichaClick}
        />
      </div>
    )}
  </div>
);

interface CarcelProps {
  img: string;
  color: ColorJugador;
  fichas: Array<{ id: number; color: ColorJugador; estado: FichaEstado }>;
  fichaSeleccionada?: { color: ColorJugador; id: number } | null;
  fichasSeleccionables?: Array<{ color: ColorJugador; id: number }>;
  onFichaClick?: (color: ColorJugador, id: number, event?: React.MouseEvent) => void;
}

const Carcel: React.FC<CarcelProps> = ({ 
  img, 
  color, 
  fichas,
  fichaSeleccionada,
  fichasSeleccionables = [],
  onFichaClick
}) => {
  // Posiciones relativas para las 4 fichas en la cárcel
  const posiciones = [
    { top: '25%', left: '25%' },
    { top: '25%', left: '55%' },
    { top: '55%', left: '25%' },
    { top: '55%', left: '55%' }
  ];

  return (
    <div className="w-full h-full relative">
      <img src={img} alt={`Cárcel ${color}`} className="w-full h-full object-cover" />
      
      {/* Fichas en la cárcel */}
      {fichas.map((ficha, idx) => {
        const pos = posiciones[idx % 4];
        const esSeleccionable = fichasSeleccionables.some(
          f => f.color === ficha.color && f.id === ficha.id
        );
        const esSeleccionada = fichaSeleccionada?.color === ficha.color && 
                               fichaSeleccionada?.id === ficha.id;
        
        return (
          <div
            key={`${ficha.color}-${ficha.id}`}
            style={{
              position: 'absolute',
              top: pos.top,
              left: pos.left,
              transform: 'translate(-50%, -50%)',
              zIndex: esSeleccionada ? 10 : 1
            }}
          >
            <Ficha
              id={ficha.id}
              color={ficha.color}
              estado="BLOQUEADO"
              seleccionada={esSeleccionada}
              seleccionable={esSeleccionable}
              onClick={(e) => onFichaClick?.(ficha.color, ficha.id, e)}
              size="large"
            />
          </div>
        );
      })}
    </div>
  );
};

const Centro = () => (
  <div className="w-full h-full flex items-center justify-center p-1">
    <img src={CenterImg} alt="Centro" className="w-full h-full object-cover" />
  </div>
);

// Panel de información del jugador
interface InfoPanelProps {
  jugadores: JugadorTablero[];
  jugadorActual: { nombre: string; color: ColorJugador } | null;
  miColor: ColorJugador | null;
}

const InfoPanel: React.FC<InfoPanelProps> = ({ jugadores, jugadorActual, miColor }) => {
  return (
    <div className="bg-white rounded-2xl shadow-xl p-4 w-64">
      <h3 className="text-lg font-bold text-gray-800 mb-3 border-b pb-2">👥 Jugadores</h3>
      <div className="space-y-2">
        {jugadores.map(j => {
          const esTurno = jugadorActual?.color === j.color;
          const esMio = j.color === miColor;
          
          return (
            <div 
              key={j.color}
              className={`p-2 rounded-lg flex items-center gap-2 ${
                esTurno ? 'bg-purple-100 border-2 border-purple-400' : 'bg-gray-50'
              }`}
            >
              <div 
                className="w-4 h-4 rounded-full"
                style={{ backgroundColor: colors[j.color] }}
              />
              <span className={`flex-1 font-medium ${esMio ? 'text-purple-700' : 'text-gray-700'}`}>
                {j.nombre} {esMio && '(Tú)'}
              </span>
              {esTurno && <span className="text-purple-600">🎯</span>}
              <span className="text-xs text-gray-500">
                🏁{j.en_meta}/4
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const Board: React.FC = () => {
  const location = useLocation();
  
  // Obtener info del jugador desde navegación
  const playerInfo = location.state?.playerInfo || {};
  const miColor = playerInfo.color as ColorJugador || null;
  const miNombre = playerInfo.nombre || '';
  const miId = playerInfo.id || 0;
  
  // Hook de estado del juego
  const { state, actions, fichaSeleccionada } = useGameState(miColor, miNombre, miId);
  
  // ⭐ NUEVO: Hook para enviar mensajes al servidor
  const { send } = useSocket();
  
  // ⭐ NUEVO: Función para manejar selección de ficha en premio de 3 dobles
  const handleSeleccionarFichaPremio = (fichaId: number) => {
    console.log('🏆 Enviando selección de ficha para premio:', fichaId);
    send({
      tipo: 'ELEGIR_FICHA_PREMIO',
      ficha_id: fichaId
    });
    // El servidor responderá y cambiará el estado
  };

  // Local state for victory popup
  const [victoryVisible, setVictoryVisible] = React.useState(false);
  const [victoryNombre, setVictoryNombre] = React.useState('');
  const prevEnMetaRef = React.useRef<Record<string, number>>({});

  // Detectar cuando algún jugador llega a 4 en_meta
  React.useEffect(() => {
    for (const j of state.jugadores) {
      const prev = prevEnMetaRef.current[j.color] ?? 0;
      if (j.en_meta >= 4 && prev < 4) {
        // Nuevo ganador detectado
        setVictoryNombre(j.nombre);
        setVictoryVisible(true);
      }
      prevEnMetaRef.current[j.color] = j.en_meta;
    }
  }, [state.jugadores]);
  
  // Estado para el mini menú
  const [menuVisible, setMenuVisible] = useState(false);
  const [menuPosition, setMenuPosition] = useState({ x: 0, y: 0 });
  const [fichaParaMenu, setFichaParaMenu] = useState<{ color: ColorJugador; id: number } | null>(null);
  
  // Obtener fichas en cárcel por color
  const getFichasEnCarcel = (color: ColorJugador) => {
    const jugador = state.jugadores.find(j => j.color === color);
    if (!jugador) return [];
    return jugador.fichas
      .filter(f => f.estado === 'BLOQUEADO')
      .map(f => ({ id: f.id, color: f.color, estado: f.estado }));
  };

  // Obtener fichas que estén visualmente en una celda determinada (gridRow/gridColumn)
  const getFichasEnVisual = (gridRow: string, gridColumn: string) => {
    const fichas: Array<{ id: number; color: ColorJugador; estado: FichaEstado }> = [];

    for (const jugador of state.jugadores) {
      for (const ficha of jugador.fichas) {
        const posVis = obtenerPosicionVisual(ficha.estado, ficha.posicion, ficha.posicion_meta, jugador.color, ficha.id);
        if (posVis && posVis.gridRow === gridRow && posVis.gridColumn === gridColumn) {
          fichas.push({ id: ficha.id, color: jugador.color, estado: ficha.estado });
        }
      }
    }

    return fichas;
  };
  
  // Obtener fichas en una casilla específica
  const getFichasEnCasilla = (posicion: number) => {
    const fichas: Array<{ id: number; color: ColorJugador; estado: FichaEstado }> = [];
    for (const jugador of state.jugadores) {
      for (const ficha of jugador.fichas) {
        if (ficha.estado === 'EN_JUEGO' && ficha.posicion === posicion) {
          fichas.push({ id: ficha.id, color: ficha.color, estado: ficha.estado });
        }
      }
    }
    
    // Log para debugging (solo para casilla 55 - salida verde)
    if (posicion === 55 && fichas.length > 0) {
      console.log(`📍 getFichasEnCasilla(${posicion}):`, fichas);
    }
    
    return fichas;
  };
  
  // Handler para click en ficha - ahora abre el mini menú
  const handleFichaClick = (color: ColorJugador, id: number, event?: React.MouseEvent) => {
    console.log(`🖱️ Click en ficha: color=${color}, id=${id}, miColor=${miColor}, esMiTurno=${state.esMiTurno}, dadosLanzados=${state.dadosLanzados}`);
    
    // Solo procesar si es mi turno, es mi ficha y los dados están lanzados
    if (color !== miColor || !state.esMiTurno || !state.dadosLanzados) {
      console.log('❌ Click rechazado: no cumple condiciones básicas');
      return;
    }
    
    // Verificar que la ficha pueda moverse (no en cárcel, o en cárcel con dobles)
    const miJugador = state.jugadores.find(j => j.color === miColor);
    if (!miJugador) {
      console.log('❌ No se encontró jugador');
      return;
    }
    
    const ficha = miJugador.fichas.find(f => f.id === id);
    if (!ficha) {
      console.log('❌ No se encontró ficha');
      return;
    }
    
    console.log(`📍 Ficha encontrada: estado=${ficha.estado}, posicion=${ficha.posicion}`);
    
    // Si la ficha está en cárcel, no puede moverse (necesita dobles para salir)
    if (ficha.estado === 'BLOQUEADO') {
      console.log('❌ Ficha bloqueada en cárcel');
      return;
    }
    
    // Calcular posición del menú
    if (event) {
      setMenuPosition({ x: event.clientX, y: event.clientY });
      console.log(`✅ Abriendo menú en (${event.clientX}, ${event.clientY})`);
    }
    
    setFichaParaMenu({ color, id });
    setMenuVisible(true);
  };
  
  // Handler para seleccionar dado desde el mini menú
  const handleSeleccionarDado = (dado: 1 | 2 | 3) => {
    if (fichaParaMenu) {
      actions.moverFicha(fichaParaMenu.id, dado);
      setMenuVisible(false);
      setFichaParaMenu(null);
    }
  };
  
  // Cerrar el mini menú
  const cerrarMenu = () => {
    setMenuVisible(false);
    setFichaParaMenu(null);
  };
  
  // Handler para mover ficha con dado (del panel lateral - por compatibilidad)
  const handleMoverFicha = (dadoElegido: 1 | 2 | 3) => {
    if (fichaSeleccionada) {
      actions.moverFicha(fichaSeleccionada.id, dadoElegido);
    }
  };
  
  // Fichas que pueden ser seleccionadas (mis fichas que pueden moverse)
  // Incluir TODAS las fichas EN_JUEGO y CAMINO_META para poder clickearlas
  const fichasSeleccionables: Array<{ color: ColorJugador; id: number }> = [];
  if (state.esMiTurno && state.dadosLanzados && miColor) {
    const miJugador = state.jugadores.find(j => j.color === miColor);
    if (miJugador) {
      console.log(`🎮 Calculando fichas seleccionables para ${miColor}:`, miJugador.fichas.map(f => ({
        id: f.id,
        estado: f.estado,
        posicion: f.posicion
      })));
      
      for (const ficha of miJugador.fichas) {
        if (ficha.estado === 'EN_JUEGO' || ficha.estado === 'CAMINO_META') {
          fichasSeleccionables.push({ color: ficha.color, id: ficha.id });
        }
      }
      
      console.log(`✅ Fichas seleccionables:`, fichasSeleccionables);
    }
  }

  return (
    <div className="flex items-start justify-center min-h-screen bg-gradient-to-br from-purple-100 to-indigo-100 p-4 gap-6">
      {/* Victory popup (global) */}
      <VictoryPopup visible={victoryVisible} nombre={victoryNombre} onClose={() => setVictoryVisible(false)} />
      
      {/* ⭐ NUEVO: Popup de premio por 3 dobles */}
      <PremioPopup
        visible={state.premioTresDoblesActivo}
        fichasElegibles={state.fichasElegiblesPremio}
        onSeleccionarFicha={handleSeleccionarFichaPremio}
      />
      
      {/* Panel izquierdo - Info de jugadores */}
      <div className="hidden lg:block">
        <InfoPanel 
          jugadores={state.jugadores}
          jugadorActual={state.jugadorActual}
          miColor={miColor}
        />
      </div>
      
      {/* Tablero */}
      <div className="bg-white p-2 sm:p-4 rounded-xl shadow-2xl overflow-auto max-h-[95vh]">
        <div
          className="grid gap-0"
          style={{
            gridTemplateColumns: 'repeat(19, 40px)',
            gridTemplateRows: 'repeat(19, 40px)',
            minWidth: '760px',
            minHeight: '760px'
          }}
        >
          
          {/* ========== CARCEL ROJA (8x8) ========== */}
          <div style={{gridRow: '1/9', gridColumn: '1/9'}}>
            <Carcel 
              img={RedJeil} 
              color="rojo"
              fichas={getFichasEnCarcel('rojo')}
              fichaSeleccionada={fichaSeleccionada}
              onFichaClick={handleFichaClick}
            />
          </div>
          
          {/* ========== BRAZO SUPERIOR (ROJO) ========== */}
          <div style={{gridRow: '1', gridColumn: '9'}}><Casilla num={35} fichas={getFichasEnCasilla(34)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '1', gridColumn: '10'}}><Casilla num={34} safe fichas={getFichasEnCasilla(33)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '1', gridColumn: '11'}}><Casilla num={33} fichas={getFichasEnCasilla(32)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          
          <div style={{gridRow: '2', gridColumn: '9'}}><Casilla num={36} fichas={getFichasEnCasilla(35)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '2', gridColumn: '10'}}><Meta color={colors.rojo} fichas={getFichasEnVisual('2','10')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '2', gridColumn: '11'}}><Casilla num={32} fichas={getFichasEnCasilla(31)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          
          <div style={{gridRow: '3', gridColumn: '9'}}><Casilla num={37} fichas={getFichasEnCasilla(36)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '3', gridColumn: '10'}}><Meta color={colors.rojo} fichas={getFichasEnVisual('3','10')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '3', gridColumn: '11'}}><Casilla num={31} fichas={getFichasEnCasilla(30)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          
          <div style={{gridRow: '4', gridColumn: '9'}}><Casilla num={38} fichas={getFichasEnCasilla(37)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '4', gridColumn: '10'}}><Meta color={colors.rojo} fichas={getFichasEnVisual('4','10')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '4', gridColumn: '11'}}><Casilla num={30} fichas={getFichasEnCasilla(29)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          
          <div style={{gridRow: '5', gridColumn: '9'}}><Casilla num={39} bgColor={colors.rojo} fichas={getFichasEnCasilla(38)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '5', gridColumn: '10'}}><Meta color={colors.rojo} fichas={getFichasEnVisual('5','10')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '5', gridColumn: '11'}}><Casilla num={29} bgColor={colors.rojo} safe fichas={getFichasEnCasilla(28)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          
          <div style={{gridRow: '6', gridColumn: '9'}}><Casilla num={40} fichas={getFichasEnCasilla(39)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '6', gridColumn: '10'}}><Meta color={colors.rojo} fichas={getFichasEnVisual('6','10')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '6', gridColumn: '11'}}><Casilla num={28} fichas={getFichasEnCasilla(27)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          
          <div style={{gridRow: '7', gridColumn: '9'}}><Casilla num={41} fichas={getFichasEnCasilla(40)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '7', gridColumn: '10'}}><Meta color={colors.rojo} fichas={getFichasEnVisual('7','10')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '7', gridColumn: '11'}}><Casilla num={27} fichas={getFichasEnCasilla(26)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          
          <div style={{gridRow: '8', gridColumn: '9'}}><Casilla num={42} fichas={getFichasEnCasilla(41)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '8', gridColumn: '10'}}><Meta color={colors.rojo} fichas={getFichasEnVisual('8','10')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '8', gridColumn: '11'}}><Casilla num={26} fichas={getFichasEnCasilla(25)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          
          {/* ========== CARCEL AZUL (8x8) ========== */}
          <div style={{gridRow: '1/9', gridColumn: '12/20'}}>
            <Carcel 
              img={BlueJeil} 
              color="azul"
              fichas={getFichasEnCarcel('azul')}
              fichaSeleccionada={fichaSeleccionada}
              onFichaClick={handleFichaClick}
            />
          </div>
          
          {/* ========== BRAZO IZQUIERDO (VERDE) ========== */}
          <div style={{gridRow: '9', gridColumn: '8'}}><Casilla num={43} fichas={getFichasEnCasilla(42)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '9', gridColumn: '7'}}><Casilla num={44} fichas={getFichasEnCasilla(43)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '9', gridColumn: '6'}}><Casilla num={45} fichas={getFichasEnCasilla(44)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '9', gridColumn: '5'}}><Casilla num={46} bgColor={colors.verde} safe fichas={getFichasEnCasilla(45)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '9', gridColumn: '4'}}><Casilla num={47} fichas={getFichasEnCasilla(46)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '9', gridColumn: '3'}}><Casilla num={48} fichas={getFichasEnCasilla(47)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '9', gridColumn: '2'}}><Casilla num={49} fichas={getFichasEnCasilla(48)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '9', gridColumn: '1'}}><Casilla num={50} fichas={getFichasEnCasilla(49)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>

          {/* Metas verdes */}
          <div style={{gridRow: '10', gridColumn: '8'}}><Meta color={colors.verde} fichas={getFichasEnVisual('10','8')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '10', gridColumn: '7'}}><Meta color={colors.verde} fichas={getFichasEnVisual('10','7')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '10', gridColumn: '6'}}><Meta color={colors.verde} fichas={getFichasEnVisual('10','6')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '10', gridColumn: '5'}}><Meta color={colors.verde} fichas={getFichasEnVisual('10','5')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '10', gridColumn: '4'}}><Meta color={colors.verde} fichas={getFichasEnVisual('10','4')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '10', gridColumn: '3'}}><Meta color={colors.verde} fichas={getFichasEnVisual('10','3')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '10', gridColumn: '2'}}><Meta color={colors.verde} fichas={getFichasEnVisual('10','2')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '10', gridColumn: '1'}}><Casilla num={51} safe fichas={getFichasEnCasilla(50)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          
          {/* Columna inferior verde */}
          <div style={{gridRow: '11', gridColumn: '8'}}><Casilla num={59} fichas={getFichasEnCasilla(58)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '11', gridColumn: '7'}}><Casilla num={58} fichas={getFichasEnCasilla(57)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '11', gridColumn: '6'}}><Casilla num={57} fichas={getFichasEnCasilla(56)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '11', gridColumn: '5'}}><Casilla num={56} bgColor={colors.verde} fichas={getFichasEnCasilla(55)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '11', gridColumn: '4'}}><Casilla num={55} fichas={getFichasEnCasilla(54)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '11', gridColumn: '3'}}><Casilla num={54} fichas={getFichasEnCasilla(53)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '11', gridColumn: '2'}}><Casilla num={53} fichas={getFichasEnCasilla(52)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '11', gridColumn: '1'}}><Casilla num={52} fichas={getFichasEnCasilla(51)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          
          {/* ========== CENTRO (3x3) ========== */}
          <div style={{gridRow: '9/12', gridColumn: '9/12'}}><Centro /></div>
          
          {/* ========== BRAZO DERECHO (AZUL) ========== */}
          <div style={{gridRow: '9', gridColumn: '12'}}><Casilla num={25} fichas={getFichasEnCasilla(24)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '9', gridColumn: '13'}}><Casilla num={24} fichas={getFichasEnCasilla(23)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '9', gridColumn: '14'}}><Casilla num={23} fichas={getFichasEnCasilla(22)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '9', gridColumn: '15'}}><Casilla num={22} bgColor={colors.azul} fichas={getFichasEnCasilla(21)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '9', gridColumn: '16'}}><Casilla num={21} fichas={getFichasEnCasilla(20)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '9', gridColumn: '17'}}><Casilla num={20} fichas={getFichasEnCasilla(19)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '9', gridColumn: '18'}}><Casilla num={19} fichas={getFichasEnCasilla(18)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '9', gridColumn: '19'}}><Casilla num={18} fichas={getFichasEnCasilla(17)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>

          {/* Metas azules */}
          <div style={{gridRow: '10', gridColumn: '12'}}><Meta color={colors.azul} fichas={getFichasEnVisual('10','12')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '10', gridColumn: '13'}}><Meta color={colors.azul} fichas={getFichasEnVisual('10','13')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '10', gridColumn: '14'}}><Meta color={colors.azul} fichas={getFichasEnVisual('10','14')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '10', gridColumn: '15'}}><Meta color={colors.azul} fichas={getFichasEnVisual('10','15')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '10', gridColumn: '16'}}><Meta color={colors.azul} fichas={getFichasEnVisual('10','16')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '10', gridColumn: '17'}}><Meta color={colors.azul} fichas={getFichasEnVisual('10','17')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '10', gridColumn: '18'}}><Meta color={colors.azul} fichas={getFichasEnVisual('10','18')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '10', gridColumn: '19'}}><Casilla num={17} safe fichas={getFichasEnCasilla(16)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>

          {/* Columna inferior azul */}
          <div style={{gridRow: '11', gridColumn: '12'}}><Casilla num={9} fichas={getFichasEnCasilla(8)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '11', gridColumn: '13'}}><Casilla num={10} fichas={getFichasEnCasilla(9)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '11', gridColumn: '14'}}><Casilla num={11} fichas={getFichasEnCasilla(10)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '11', gridColumn: '15'}}><Casilla num={12} bgColor={colors.azul} safe fichas={getFichasEnCasilla(11)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '11', gridColumn: '16'}}><Casilla num={13} fichas={getFichasEnCasilla(12)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '11', gridColumn: '17'}}><Casilla num={14} fichas={getFichasEnCasilla(13)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '11', gridColumn: '18'}}><Casilla num={15} fichas={getFichasEnCasilla(14)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '11', gridColumn: '19'}}><Casilla num={16} fichas={getFichasEnCasilla(15)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>

          {/* ========== CARCEL VERDE (8x8) ========== */}
          <div style={{gridRow: '12/20', gridColumn: '1/9'}}>
            <Carcel 
              img={GreenJeil} 
              color="verde"
              fichas={getFichasEnCarcel('verde')}
              fichaSeleccionada={fichaSeleccionada}
              onFichaClick={handleFichaClick}
            />
          </div>
          
          {/* ========== BRAZO INFERIOR (AMARILLO) ========== */}
          <div style={{gridRow: '12', gridColumn: '9'}}><Casilla num={60} fichas={getFichasEnCasilla(59)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '12', gridColumn: '10'}}><Meta color={colors.amarillo} fichas={getFichasEnVisual('12','10')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '12', gridColumn: '11'}}><Casilla num={8} fichas={getFichasEnCasilla(7)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>

          <div style={{gridRow: '13', gridColumn: '9'}}><Casilla num={61} fichas={getFichasEnCasilla(60)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '13', gridColumn: '10'}}><Meta color={colors.amarillo} fichas={getFichasEnVisual('13','10')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '13', gridColumn: '11'}}><Casilla num={7} fichas={getFichasEnCasilla(6)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>

          <div style={{gridRow: '14', gridColumn: '9'}}><Casilla num={62} fichas={getFichasEnCasilla(61)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '14', gridColumn: '10'}}><Meta color={colors.amarillo} fichas={getFichasEnVisual('14','10')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '14', gridColumn: '11'}}><Casilla num={6} fichas={getFichasEnCasilla(5)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>

          <div style={{gridRow: '15', gridColumn: '9'}}><Casilla num={63} bgColor={colors.amarillo} safe fichas={getFichasEnCasilla(62)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '15', gridColumn: '10'}}><Meta color={colors.amarillo} fichas={getFichasEnVisual('15','10')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '15', gridColumn: '11'}}><Casilla num={5} bgColor={colors.amarillo} fichas={getFichasEnCasilla(4)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>

          <div style={{gridRow: '16', gridColumn: '9'}}><Casilla num={64} fichas={getFichasEnCasilla(63)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '16', gridColumn: '10'}}><Meta color={colors.amarillo} fichas={getFichasEnVisual('16','10')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '16', gridColumn: '11'}}><Casilla num={4} fichas={getFichasEnCasilla(3)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>

          <div style={{gridRow: '17', gridColumn: '9'}}><Casilla num={65} fichas={getFichasEnCasilla(64)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '17', gridColumn: '10'}}><Meta color={colors.amarillo} fichas={getFichasEnVisual('17','10')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '17', gridColumn: '11'}}><Casilla num={3} fichas={getFichasEnCasilla(2)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>

          <div style={{gridRow: '18', gridColumn: '9'}}><Casilla num={66} fichas={getFichasEnCasilla(65)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '18', gridColumn: '10'}}><Meta color={colors.amarillo} fichas={getFichasEnVisual('18','10')} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '18', gridColumn: '11'}}><Casilla num={2} fichas={getFichasEnCasilla(1)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>

          <div style={{gridRow: '19', gridColumn: '9'}}><Casilla num={67} fichas={getFichasEnCasilla(66)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '19', gridColumn: '10'}}><Casilla num={68} safe fichas={getFichasEnCasilla(67)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>
          <div style={{gridRow: '19', gridColumn: '11'}}><Casilla num={1} fichas={getFichasEnCasilla(0)} fichaSeleccionada={fichaSeleccionada} fichasSeleccionables={fichasSeleccionables} onFichaClick={handleFichaClick} /></div>

          {/* ========== CARCEL AMARILLA (8x8) ========== */}
          <div style={{gridRow: '12/20', gridColumn: '12/20'}}>
            <Carcel 
              img={YellowJeil} 
              color="amarillo"
              fichas={getFichasEnCarcel('amarillo')}
              fichaSeleccionada={fichaSeleccionada}
              onFichaClick={handleFichaClick}
            />
          </div>
          
        </div>
      </div>
      
      {/* Panel derecho - Dados y controles */}
      <div>
        {/* HUD de fichas sacadas para el jugador */}
        <SacadasHUD
          count={state.jugadores.find(j => j.color === miColor)?.en_meta ?? 0}
          playerName={miNombre}
          color={miColor ?? 'gray'}
        />

        <DadosPanel
          dado1={state.dado1}
          dado2={state.dado2}
          suma={state.suma}
          esDoble={state.esDoble}
          dadosLanzados={state.dadosLanzados}
          dadosUsados={state.dadosUsados}
          esMiTurno={state.esMiTurno}
          puedeTomarAccion={state.puedeTomarAccion}
          puedeRelanzar={state.puedeRelanzar}
          fichasEnCarcel={state.fichasEnCarcel.length}
          fichaSeleccionada={fichaSeleccionada}
          onLanzarDados={actions.lanzarDados}
          onSacarDeCarcel={actions.sacarDeCarcel}
          onSacarTodasDeCarcel={actions.sacarTodasDeCarcel}
          onMoverFicha={handleMoverFicha}
          miColor={miColor}
        />
        
        {/* Notificaciones */}
        {state.ultimaCaptura && (
          <div className="mt-4 p-3 bg-red-100 border-2 border-red-400 rounded-xl text-center animate-bounce">
            <span className="text-red-700 font-bold">
              ⚠️ ¡{state.ultimaCaptura.nombre} fue capturado!
            </span>
          </div>
        )}
        
        {state.juegoTerminado && state.ganador && (
          <div className="mt-4 p-4 bg-gradient-to-r from-yellow-200 to-yellow-300 border-4 border-yellow-500 rounded-xl text-center">
            <div className="text-4xl mb-2">🏆</div>
            <span className="text-yellow-800 font-bold text-xl">
              ¡{state.ganador.nombre} ganó!
            </span>
          </div>
        )}
      </div>
      
      {/* Mini menú para selección de dados */}
      <MiniMenuDados
        visible={menuVisible}
        position={menuPosition}
        dado1={state.dado1}
        dado2={state.dado2}
        suma={state.suma}
        dado1Usado={state.dadosUsados.includes(1)}
        dado2Usado={state.dadosUsados.includes(2)}
        fichaColor={fichaParaMenu?.color || 'rojo'}
        fichaId={fichaParaMenu?.id || 0}
        fichaEstado={
          fichaParaMenu
            ? (state.jugadores.find(j => j.color === fichaParaMenu.color)?.fichas.find(f => f.id === fichaParaMenu.id)?.estado)
            : undefined
        }
        posicionMeta={
          fichaParaMenu
            ? (state.jugadores.find(j => j.color === fichaParaMenu.color)?.fichas.find(f => f.id === fichaParaMenu.id)?.posicion_meta)
            : undefined
        }
        fichaPosicion={
          fichaParaMenu
            ? (state.jugadores.find(j => j.color === fichaParaMenu.color)?.fichas.find(f => f.id === fichaParaMenu.id)?.posicion)
            : undefined
        }
        onSeleccionarDado={handleSeleccionarDado}
        onCerrar={cerrarMenu}
      />
    </div>
  );
};

export default Board;
