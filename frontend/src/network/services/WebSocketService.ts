import type { BaseMessage } from "../types/messages";

type EventCallback = (data: any) => void;

class WebSocketService {
  private socket: WebSocket | null = null;
  private url: string;
  private listeners: Record<string, EventCallback[]> = {};

  constructor(url: string) {
    this.url = url;
  }

  connect(playerName: string, playerColor?: string) {
    if (this.socket?.readyState === WebSocket.OPEN) return;

    this.socket = new WebSocket(this.url);

    this.socket.onopen = () => {
      const msg = {
        tipo: "CONECTAR",
        nombre: playerName,
        ...(playerColor && { color: playerColor }),
      };
      this.send(msg);
      this.emit("open", null);
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.emit("message", data);
      } catch (err) {
        this.emit("error", "Mensaje inválido del servidor");
      }
    };

    this.socket.onerror = (err) => {
      this.emit("error", "Error de conexión WebSocket");
    };

    this.socket.onclose = () => {
      this.emit("close", "Conexión cerrada");
    };
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
    this.socket?.close();
    this.socket = null;
  }
}

export default WebSocketService;