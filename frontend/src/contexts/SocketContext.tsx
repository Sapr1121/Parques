import { createContext, useContext, useState, useRef } from 'react';
import WebSocketService from "../network/services/WebSocketService";
import type { BaseMessage } from '../network/types/messages';

/* --------------  TIPOS  -------------- */
interface SocketCtx {
  connected: boolean;
  lastMessage: any;
  error: string | null;
  connect: (name: string, color?: string, wsUrl?: string) => Promise<void>;
  send: (msg: BaseMessage) => void;
  disconnect: () => void;
}

/* --------------  CONTEXT  -------------- */
const SocketContext = createContext<SocketCtx | undefined>(undefined);

/* --------------  PROVIDER  -------------- */
export const SocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // una única instancia para toda la app
  const service = useRef<WebSocketService | null>(null);
  const currentUrl = useRef<string>('');

  const connect = async (name: string, color?: string, wsUrl?: string) => {
    const url = wsUrl || import.meta.env.VITE_WS_URL || 'ws://localhost:8001';
    
    // Si ya hay una conexión a una URL diferente, desconectar primero
    if (service.current && currentUrl.current !== url) {
      console.log('🔄 Cambiando de servidor:', currentUrl.current, '->', url);
      service.current.disconnect();
      service.current = null;
    }
    
    // Crear el servicio si no existe
    if (!service.current) {
      console.log('🔌 Creando conexión WebSocket a:', url);
      currentUrl.current = url;
      service.current = new WebSocketService(url);
      
      service.current.on('open', () => {
        console.log('✅ WebSocket conectado');
        setConnected(true);
      });
      service.current.on('close', () => {
        console.log('❌ WebSocket desconectado');
        setConnected(false);
      });
      service.current.on('message', (m) => {
        console.log('📩 Mensaje recibido:', m);
        setLastMessage(m);
      });
      service.current.on('error', (e) => setError(e));
    }
    
    await service.current.connect(name, color);
  };
  
  const send = (msg: BaseMessage) => service.current?.send(msg);
  
  const disconnect = () => {
    service.current?.disconnect();
    service.current = null;
    currentUrl.current = '';
    setConnected(false);
  };

  // NO usar useEffect para cleanup automático
  // El socket debe mantenerse vivo durante toda la sesión de juego

  return (
    <SocketContext.Provider value={{ connected, lastMessage, error, connect, send, disconnect }}>
      {children}
    </SocketContext.Provider>
  );
};


export const useSocket = () => {
  const ctx = useContext(SocketContext);
  if (!ctx) throw new Error('useSocket debe usarse dentro de SocketProvider');
  return ctx;
};