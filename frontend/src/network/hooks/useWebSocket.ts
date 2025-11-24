import { useEffect, useRef, useState } from "react";
import WebSocketService from "../services/WebSocketService";

export const useWebSocket = (url: string) => {
  const ws = useRef<WebSocketService | null>(null);
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    ws.current = new WebSocketService(url);

    ws.current.on("open", () => setConnected(true));
    ws.current.on("close", () => setConnected(false));
    ws.current.on("message", (msg) => setLastMessage(msg));
    ws.current.on("error", (err) => setError(err));

    return () => {
      ws.current?.disconnect();
    };
  }, [url]);

  const connect = (name: string, color?: string) => {
    ws.current?.connect(name, color);
  };

  const send = (msg: any) => {
    ws.current?.send(msg);
  };

  return { connected, lastMessage, error, connect, send };
};