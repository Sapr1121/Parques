import { useState } from 'react';
import { queryRoom } from '../services/registry';
import  WebSocketService  from '../../network/services/WebSocketService';

export function useJoinRoom() {
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [roomInfo, setRoomInfo] = useState<any>(null);
  const [ws, setWs] = useState<WebSocketService | null>(null);

  async function handleJoin(code: string, playerName: string, color: string) {
    setStatus('Buscando sala...');
    setError('');
    const response = await queryRoom(code);

    if (response.status !== 'success' || !response.lobby) {
      setError('Sala no encontrada. Verifica el código.');
      setStatus('');
      return null;
    }

    setRoomInfo(response.lobby);
    setStatus(`Sala encontrada. Conectando...`);

    // Conexión WebSocket
    const wsUrl = `ws://${response.lobby.ip}:${response.lobby.port}`;
    const socket = new WebSocketService(wsUrl);

    try {
      await socket.connect();
      socket.send({ tipo: 'CONECTAR', nombre: playerName, color });
      setStatus('Conectado al servidor');
      setWs(socket);
      // Puedes manejar mensajes aquí o exponer socket para el resto de la app
      return { lobby: response.lobby, socket };
    } catch (err) {
      setError('No se pudo conectar al servidor de juego');
      setStatus('');
      return null;
    }
  }

  return { status, error, roomInfo, ws, handleJoin };
}