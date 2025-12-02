import React, { useState } from "react";
import { useWebSocket } from "../hooks/useWebSocket";

export const NetworkTest: React.FC = () => {
  const wsUrl = import.meta.env.VITE_WS_URL || "ws://localhost:8001";
  const { connected, lastMessage, error, connect, send } = useWebSocket(wsUrl);
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