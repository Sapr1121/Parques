import React, { createContext, useContext, useEffect, useState, useRef } from 'react';
import WebSocketService from "../network/services/WebSocketService";
import type { BaseMessage } from '../network/types/messages';

/* --------------  TIPOS  -------------- */
interface SocketCtx {
  connected: boolean;
  lastMessage: any;
  error: string | null;
  connect: (name: string, color?: string) => void;
  send: (msg: BaseMessage) => void;
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

  useEffect(() => {
    service.current = new WebSocketService(import.meta.env.VITE_WS_URL || 'ws://localhost:8001');

    service.current.on('open',    () => setConnected(true));
    service.current.on('close',   () => setConnected(false));
    service.current.on('message', (m) => setLastMessage(m));
    service.current.on('error',   (e) => setError(e));

    return () => service.current?.disconnect();
  }, []);

  const connect = (name: string, color?: string) => service.current?.connect(name, color);
  const send    = (msg: BaseMessage) => service.current?.send(msg);

  return (
    <SocketContext.Provider value={{ connected, lastMessage, error, connect, send }}>
      {children}
    </SocketContext.Provider>
  );
};


export const useSocket = () => {
  const ctx = useContext(SocketContext);
  if (!ctx) throw new Error('useSocket debe usarse dentro de SocketProvider');
  return ctx;
};