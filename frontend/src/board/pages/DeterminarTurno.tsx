import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import TurnDetermination from '../dice/TurnDetermination';
import type { Player } from '../dice/types';
import { useSocket } from '../../contexts/SocketContext';

const DeterminarTurno: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { lastMessage } = useSocket();
  // Recibe jugadores y miId desde el lobby por location.state
  const { players, myId } = location.state || {};
  const [ordenFinal, setOrdenFinal] = useState<Player[] | null>(null);

  useEffect(() => {
    if (ordenFinal) {
      // Navegar al tablero y pasar el orden de turnos
      navigate('/board', { state: { turnOrder: ordenFinal } });
    }
  }, [ordenFinal, navigate]);

  if (!players || myId === undefined) {
    return <div className="p-8 text-center text-red-600 font-bold">Error: No hay datos de jugadores.</div>;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-100 to-blue-100">
      <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-xl w-full">
        <TurnDetermination players={players} myId={myId} onFinish={setOrdenFinal} />
      </div>
    </div>
  );
};

export default DeterminarTurno;
