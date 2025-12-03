import { useState } from 'react';
import { queryRoom } from '../services/registry';
import { useSocket } from '../../contexts/SocketContext';
import { obtenerSesion } from '../../auth/services/authService';

export function useJoinRoom() {
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [roomInfo, setRoomInfo] = useState<any>(null);
  const [availableColors, setAvailableColors] = useState<string[]>(['rojo', 'azul', 'amarillo', 'verde']);
  const [loadingColors, setLoadingColors] = useState(false);
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

      // Construir URL del WebSocket usando la IP y puerto del servidor de la sala
      // Esto permite conexión en red local (LAN)
      const wsUrl = `ws://${response.lobby.ip}:${response.lobby.port}`;
      
      console.log('🔌 Conectando a:', wsUrl);
      console.log('👤 Jugador:', playerName, 'Color:', color);
      
      // Obtener usuario_id de la sesión
      const sesion = obtenerSesion();
      const usuarioId = sesion?.usuario_id;
      
      // Conectar usando el contexto global con la URL de la sala
      await connect(playerName, color, wsUrl, usuarioId);
      
      setStatus('Conectado al servidor');
      return { lobby: response.lobby };
    } catch (err) {
      console.error('Error al unirse:', err);
      setError('No se pudo conectar al servidor de juego');
      setStatus('');
      return null;
    }
  }

  async function fetchAvailableColors(code: string): Promise<string[]> {
    setLoadingColors(true);
    setError('');
    
    try {
      // Primero obtener info de la sala
      const response = await queryRoom(code);
      
      if (response.status !== 'success' || !response.lobby) {
        setError('Sala no encontrada');
        return [];
      }
      
      // Construir URL del WebSocket usando la IP y puerto del servidor de la sala
      const wsUrl = `ws://${response.lobby.ip}:${response.lobby.port}`;
      
      return new Promise((resolve) => {
        const tempWs = new WebSocket(wsUrl);
        let resolved = false;
        
        const timeout = setTimeout(() => {
          if (!resolved) {
            resolved = true;
            tempWs.close();
            console.log('⏱️ Timeout obteniendo colores, usando todos');
            resolve(['rojo', 'azul', 'amarillo', 'verde']);
          }
        }, 5000);
        
        tempWs.onopen = () => {
          console.log('🔌 Conectado temporalmente para obtener colores');
          tempWs.send(JSON.stringify({ tipo: 'SOLICITAR_COLORES' }));
        };
        
        tempWs.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data);
            console.log('📩 Respuesta de colores:', msg);
            
            if (msg.tipo === 'COLORES_DISPONIBLES') {
              clearTimeout(timeout);
              resolved = true;
              tempWs.close();
              const colores = msg.colores || [];
              setAvailableColors(colores);
              resolve(colores);
            }
          } catch (e) {
            console.error('Error parseando mensaje:', e);
          }
        };
        
        tempWs.onerror = () => {
          if (!resolved) {
            clearTimeout(timeout);
            resolved = true;
            tempWs.close();
            console.log('❌ Error obteniendo colores');
            resolve(['rojo', 'azul', 'amarillo', 'verde']);
          }
        };
      });
    } catch (err) {
      console.error('Error fetching colors:', err);
      return ['rojo', 'azul', 'amarillo', 'verde'];
    } finally {
      setLoadingColors(false);
    }
  }

  return { status, error, roomInfo, connected, handleJoin, availableColors, loadingColors, fetchAvailableColors };
}