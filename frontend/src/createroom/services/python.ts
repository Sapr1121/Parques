import axios from 'axios';

// Detectar dinámicamente la URL del backend basándose en el host actual
// Esto permite que funcione en LAN sin configuración manual
function getApiUrl(): string {
  // Si hay una variable de entorno definida (y no es localhost), usarla
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl && !envUrl.includes('localhost')) {
    return envUrl;
  }
  
  // Si estamos en localhost, usar localhost
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:3001';
  }
  
  // Si estamos accediendo desde otra IP (LAN), usar esa misma IP para el backend
  return `http://${window.location.hostname}:3001`;
}

const API_URL = getApiUrl();

interface CreateRoomResponse {
  code: string;
  port: number;
}

export async function createRoom(playerName: string, color: string): Promise<CreateRoomResponse> {
  const response = await axios.post(`${API_URL}/api/create-room`, {
    playerName,
    color,
  });
  return response.data;
}