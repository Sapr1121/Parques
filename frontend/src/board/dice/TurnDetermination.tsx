import React, { useState, useEffect, useRef } from 'react';
import DiceRoller from './DiceRoller';
import type { Player } from './types';
import { useSocket } from '../../contexts/SocketContext';

interface TurnDeterminationProps {
  players: Player[];
  myId: number;
  onFinish: (order: Player[]) => void;
}

interface RollResult {
  nombre: string;
  color: string;
  dado1: number;
  dado2: number;
  suma: number;
}

const TurnDetermination: React.FC<TurnDeterminationProps> = ({ players, myId, onFinish }) => {
  const { send, lastMessage } = useSocket();
  
  // Estado de las tiradas - guardamos por color para identificar mejor
  const [rolls, setRolls] = useState<{ [color: string]: RollResult }>({});
  
  // Control de turno
  const [esMiTurno, setEsMiTurno] = useState(false);
  const [jugadorActual, setJugadorActual] = useState<string>('');
  const [yaLance, setYaLance] = useState(false);
  
  // Estado de empate
  const [hayEmpate, setHayEmpate] = useState(false);
  const [jugadoresEmpatados, setJugadoresEmpatados] = useState<any[]>([]);
  const [valorEmpate, setValorEmpate] = useState<number>(0);
  const [estoyEnDesempate, setEstoyEnDesempate] = useState(false);
  
  // Estado final
  const [finished, setFinished] = useState(false);
  const [ganador, setGanador] = useState<any>(null);
  const [ordenFinal, setOrdenFinal] = useState<any[]>([]);
  
  // Mi info
  const miColor = players.find(p => p.id === myId)?.color || '';
  const miNombre = players.find(p => p.id === myId)?.name || '';

  // Enviar tirada al backend
  const handleRoll = (value: number) => {
    if (yaLance && !estoyEnDesempate) return;
    
    // Generar segundo dado
    const dado2 = Math.floor(Math.random() * 6) + 1;
    
    console.log(`🎲 Enviando tirada: dado1=${value}, dado2=${dado2}`);
    send({ tipo: 'DETERMINACION_TIRADA', dado1: value, dado2: dado2 });
    setYaLance(true);
    setEsMiTurno(false);
  };

  // Escuchar mensajes del backend
  useEffect(() => {
    if (!lastMessage) return;
    
    console.log('🎲 TurnDetermination recibió:', lastMessage);
    
    if (lastMessage.tipo === 'DETERMINACION_RESULTADO') {
      const { nombre, color, dado1, dado2, suma, siguiente } = lastMessage;

      setRolls((prev) => ({
        ...prev,
        [color]: { nombre, color, dado1, dado2, suma },
      }));

      if (siguiente) {
        setJugadorActual(siguiente);
        setEsMiTurno(siguiente === miNombre);
        setYaLance(false); // Permitir tirar de nuevo
      }
    }

    if (lastMessage.tipo === 'DETERMINACION_EMPATE') {
      const { jugadores, valor } = lastMessage;

      setHayEmpate(true);
      setJugadoresEmpatados(jugadores);
      setValorEmpate(valor);

      const estoy = jugadores.some((j: { color: string }) => j.color === miColor);
      setEstoyEnDesempate(estoy);

      if (estoy) {
        setYaLance(false); // Permitir tirar de nuevo
        setEsMiTurno(true); // Los empatados pueden tirar
      }

      setRolls({}); // Limpiar tiradas anteriores
    }

    if (lastMessage.tipo === 'DETERMINACION_INICIO') {
      const jugadorActualMsg = lastMessage.jugador_actual || '';
      setJugadorActual(jugadorActualMsg);

      if (!jugadorActualMsg && myId === 0) {
        setEsMiTurno(true);
      } else {
        setEsMiTurno(jugadorActualMsg === miNombre);
      }

      setYaLance(false); // Asegurar que el jugador pueda tirar
      setHayEmpate(false);
      setEstoyEnDesempate(false);
    }

    if (lastMessage.tipo === 'DETERMINACION_GANADOR') {
      const { ganador: ganadorInfo, orden } = lastMessage;

      setFinished(true);
      setGanador(ganadorInfo);
      setOrdenFinal(orden);

      const ordenPlayers = orden.map((p: { nombre: string; color: string }, idx: number) => ({
        id: idx,
        name: p.nombre,
        color: p.color,
      }));

      setTimeout(() => {
        onFinish(ordenPlayers);
      }, 3000);
    }
  }, [lastMessage, miNombre, myId, miColor, onFinish]);

  // Obtener color de fondo según el color del jugador
  const getColorBg = (color: string) => {
    const colors: { [key: string]: string } = {
      rojo: 'bg-red-100 border-red-400',
      azul: 'bg-blue-100 border-blue-400',
      verde: 'bg-green-100 border-green-400',
      amarillo: 'bg-yellow-100 border-yellow-400',
    };
    return colors[color] || 'bg-gray-100 border-gray-400';
  };

  const getColorText = (color: string) => {
    const colors: { [key: string]: string } = {
      rojo: 'text-red-700',
      azul: 'text-blue-700',
      verde: 'text-green-700',
      amarillo: 'text-yellow-700',
    };
    return colors[color] || 'text-gray-700';
  };

  return (
    <div className="flex flex-col items-center gap-6 p-6 max-w-lg mx-auto">
      {/* Título */}
      <div className="text-center">
        <h2 className="text-3xl font-bold mb-2 text-purple-700">🎲 Determinación de Turnos</h2>
        <p className="text-gray-600">
          {hayEmpate 
            ? `¡Empate con ${valorEmpate} puntos! Los empatados deben tirar de nuevo.`
            : 'Cada jugador lanza los dados. El que saque más alto comienza.'}
        </p>
      </div>

      {/* Estado del turno */}
      {!finished && (
        <div className={`w-full p-4 rounded-xl text-center font-bold ${
          esMiTurno ? 'bg-green-100 border-2 border-green-400 text-green-700' : 'bg-gray-100 text-gray-600'
        }`}>
          {esMiTurno 
            ? '🎯 ¡ES TU TURNO PARA LANZAR!'
            : jugadorActual 
              ? `⏳ Esperando a ${jugadorActual}...`
              : '⏳ Esperando...'
          }
        </div>
      )}

      {/* Lista de jugadores y sus tiradas */}
      <div className="w-full space-y-3">
        {(hayEmpate ? jugadoresEmpatados : players).map((p: any) => {
          const color = p.color;
          const nombre = p.name || p.nombre;
          const roll = rolls[color];
          const esYo = color === miColor;
          
          return (
            <div 
              key={color} 
              className={`flex items-center justify-between p-4 rounded-xl border-2 ${getColorBg(color)} ${esYo ? 'ring-2 ring-purple-400' : ''}`}
            >
              <div className="flex items-center gap-3">
                {esYo && <span className="text-lg">👉</span>}
                <span className={`font-bold text-lg capitalize ${getColorText(color)}`}>
                  {nombre}
                </span>
                {esYo && <span className="text-xs bg-purple-200 text-purple-700 px-2 py-1 rounded">Tú</span>}
              </div>
              
              <div className="text-right">
                {roll ? (
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">🎲</span>
                    <span className="font-mono text-lg">[{roll.dado1}] [{roll.dado2}]</span>
                    <span className="text-xl font-extrabold text-purple-700">= {roll.suma}</span>
                  </div>
                ) : (
                  <span className="text-gray-400 italic">Esperando...</span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Botón de lanzar dados */}
      {!finished && esMiTurno && (!yaLance || estoyEnDesempate) && (
        <div className="mt-4">
          <DiceRoller onRoll={handleRoll} disabled={false} />
        </div>
      )}

      {/* Mensaje de espera después de lanzar */}
      {!finished && yaLance && !esMiTurno && !estoyEnDesempate && (
        <div className="text-center text-gray-500 italic">
          ✅ Ya lanzaste. Esperando a los demás jugadores...
        </div>
      )}

      {/* Resultado final */}
      {finished && ganador && (
        <div className="w-full mt-6 p-6 bg-gradient-to-br from-yellow-100 to-yellow-200 rounded-2xl border-4 border-yellow-400 text-center">
          <div className="text-4xl mb-2">🏆</div>
          <h3 className="text-2xl font-bold text-yellow-800 mb-4">¡Turnos Determinados!</h3>
          
          <p className="text-lg mb-4">
            <span className="font-bold">{ganador.nombre}</span> ({ganador.color}) comienza la partida
          </p>
          
          <div className="text-left bg-white/50 rounded-xl p-4">
            <p className="font-bold text-gray-700 mb-2">📋 Orden de turnos:</p>
            {ordenFinal.map((j: any, idx: number) => (
              <div key={j.color} className="flex items-center gap-2 py-1">
                <span className="font-bold text-purple-600">{idx + 1}.</span>
                <span className={`capitalize ${getColorText(j.color)}`}>{j.nombre}</span>
                {j.color === miColor && <span className="text-xs bg-purple-200 text-purple-700 px-2 py-0.5 rounded">Tú</span>}
              </div>
            ))}
          </div>
          
          <p className="mt-4 text-gray-600 animate-pulse">
            🎮 Iniciando partida en breve...
          </p>
        </div>
      )}
    </div>
  );
};

export default TurnDetermination;
