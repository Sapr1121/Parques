import { useState } from 'react';
import { createRoom } from '../services/python';
import { useSocket } from '../../contexts/SocketContext';

export const useCreateRoom = () => {
  const { connect, connected } = useSocket();
  const [roomCode, setRoomCode] = useState<string>('');
  const [roomPort, setRoomPort] = useState<number>(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const create = async (playerName: string, playerColor: string) => {
    setLoading(true);
    setError(null);
    try {
      // 1. Llamar a la API del backend para crear la sala
      const response = await createRoom(playerName, playerColor);
      setRoomCode(response.code);
      setRoomPort(response.port);

      // 2. Conectar WebSocket al servidor Python
      await connect(playerName, playerColor);

    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : 'Error creando sala';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const cleanup = () => {
    setRoomCode('');
    setRoomPort(0);
  };

  return { create, roomCode, roomPort, loading, error, connected, cleanup };
};