import type { BaseMessage } from "../types/messages";

type EventCallback = (data: any) => void;

class WebSocketService {
  private socket: WebSocket | null = null;
  private url: string;
  private listeners: Record<string, EventCallback[]> = {};

  constructor(url: string) {
    this.url = url;
  }

  connect(playerName: string, playerColor?: string, usuarioId?: number): Promise<void> {
    return new Promise((resolve, reject) => {
      console.log('🔄 connect() llamado, estado actual:', this.socket?.readyState);
      
      if (this.socket?.readyState === WebSocket.OPEN) {
        console.log('✅ Ya conectado, no reconectar');
        resolve();
        return;
      }

      console.log('🔌 Creando nueva conexión WebSocket a:', this.url);
      this.socket = new WebSocket(this.url);

      this.socket.onopen = () => {
        const msg = {
          tipo: "CONECTAR",
          nombre: playerName,
          ...(playerColor && { color: playerColor }),
          ...(usuarioId && { usuario_id: usuarioId }),
        };
        this.send(msg);
        this.emit("open", null);
        resolve();
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.emit("message", data);
        } catch (err) {
          this.emit("error", "Mensaje inválido del servidor");
        }
      };

      this.socket.onerror = () => {
        this.emit("error", "Error de conexión WebSocket");
        reject(new Error("Error de conexión WebSocket"));
      };

      this.socket.onclose = (event) => {
        console.log('🔌 WebSocket cerrado:', event.code, event.reason);
        this.emit("close", "Conexión cerrada");
      };
    });
  }

  send(msg: BaseMessage) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(msg));
    } else {
      console.warn("WebSocket no está abierto");
    }
  }

  on(event: string, callback: EventCallback) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(callback);
  }

  off(event: string, callback: EventCallback) {
    this.listeners[event] = this.listeners[event]?.filter(cb => cb !== callback) || [];
  }

  private emit(event: string, data: any) {
    this.listeners[event]?.forEach(cb => cb(data));
  }

  disconnect() {
    console.log('🛑 Desconectando WebSocket...');
    this.socket?.close();
    this.socket = null;
  }
}

export default WebSocketService;