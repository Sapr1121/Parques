// frontend/src/joinroom/services/registry.ts

// Detectar dinámicamente la URL del backend basándose en el host actual
function getApiUrl(): string {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl && !envUrl.includes('localhost')) {
    return envUrl;
  }
  
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:3001';
  }
  
  // Si estamos accediendo desde otra IP (LAN), usar esa misma IP para el backend
  return `http://${window.location.hostname}:3001`;
}

export async function queryRoom(code: string) {
  const API_URL = getApiUrl();
  const res = await fetch(`${API_URL}/api/query-room?code=${code}`);
  return await res.json();
}