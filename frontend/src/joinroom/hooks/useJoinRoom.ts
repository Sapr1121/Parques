import { useState } from 'react';
import { queryRoom } from '../services/registry';
import { useSocket } from '../../contexts/SocketContext';

export function useJoinRoom() {
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [roomInfo, setRoomInfo] = useState<any>(null);
  const { connect, connected } = useSocket();

  async function handleJoin(code: string, color: string, playerName: string) {
    setStatus('Buscando sala...');
    setError('');
    
    try {
      const response = await queryRoom(code);

      if (response.status !== 'success' || !response.lobby) {
        setError('Sala no encontrada. Verifica el código.');
        setStatus('');
        return null;
      }

      setRoomInfo(response.lobby);
      setStatus(`Sala encontrada. Conectando...`);

      // URL del WebSocket del servidor de la sala
      const wsUrl = `ws://${response.lobby.ip}:${response.lobby.port}`;
      
      console.log('🔌 Conectando a:', wsUrl);
      console.log('👤 Jugador:', playerName, 'Color:', color);
      
      // Conectar usando el contexto global con la URL de la sala
      await connect(playerName, color, wsUrl);
      
      setStatus('Conectado al servidor');
      return { lobby: response.lobby };
    } catch (err) {
      console.error('Error al unirse:', err);
      setError('No se pudo conectar al servidor de juego');
      setStatus('');
      return null;
    }
  }

  return { status, error, roomInfo, connected, handleJoin };
}