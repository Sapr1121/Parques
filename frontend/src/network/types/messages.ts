export type MessageType = "CONECTAR" | "MOVER" | "CHAT" | "ERROR" | "LISTO";

export interface BaseMessage {
  tipo: MessageType;
}

export interface ConnectMessage extends BaseMessage {
  tipo: "CONECTAR";
  nombre: string;
  color?: string;
}