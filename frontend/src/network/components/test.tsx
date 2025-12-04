import React, { useState } from "react";
import { useWebSocket } from "../hooks/useWebSocket";

// URL dinámica para soportar múltiples computadores en red
const getWsUrl = () => {
  if (import.meta.env.VITE_WS_URL) return import.meta.env.VITE_WS_URL;
  const hostname = window.location.hostname || 'localhost';
  return `ws://${hostname}:8001`;
};

export const NetworkTest: React.FC = () => {
  const { connected, lastMessage, error, connect, send } = useWebSocket(getWsUrl());
  const [name, setName] = useState("");
  const [color, setColor] = useState("");

  return (
    <div>
      <h2>Parques WebSocket</h2>
      {!connected ? (
        <>
          <input placeholder="Nombre" value={name} onChange={e => setName(e.target.value)} />
          <input placeholder="Color" value={color} onChange={e => setColor(e.target.value)} />
          <button onClick={() => connect(name, color)}>Conectar</button>
        </>
      ) : (
        <>
          <p>✅ Conectado</p>
          <button onClick={() => send({ tipo: "CHAT", texto: "Hola desde React" })}>Enviar mensaje</button>
        </>
      )}
      {error && <p style={{ color: "red" }}>Error: {error}</p>}
      {lastMessage && <p>Último mensaje: {JSON.stringify(lastMessage)}</p>}
    </div>
  );
};