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

      // 2. Esperar a que los servidores Python se inicien
      console.log('⏳ Esperando a que el servidor se inicie...');
      await new Promise((resolve) => setTimeout(resolve, 3000));

      // 3. Conectar WebSocket al servidor Python con reintentos
      let retries = 3;
      let isConnected = false;
      while (retries > 0 && !isConnected) {
        try {
          console.log(`🔌 Intentando conectar... (intentos restantes: ${retries})`);
          await connect(playerName, playerColor);
          isConnected = true;
          console.log('✅ Conectado al servidor');
        } catch {
          retries--;
          if (retries > 0) {
            console.log('⏳ Reintentando en 2 segundos...');
            await new Promise((resolve) => setTimeout(resolve, 2000));
          } else {
            throw new Error('No se pudo conectar al servidor después de varios intentos');
          }
        }
      }
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