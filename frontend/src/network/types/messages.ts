export type MessageType = 
  | "CONECTAR" 
  | "MOVER" 
  | "CHAT" 
  | "ERROR" 
  | "LISTO"
  | "LANZAR_DADOS"
  | "SACAR_CARCEL"
  | "SACAR_TODAS"
  | "MOVER_FICHA"
  | "DETERMINACION_TIRADA"
  | "SOLICITAR_COLORES";

export interface BaseMessage {
  tipo: MessageType;
  [key: string]: any; // Permitir propiedades adicionales
}

export interface ConnectMessage extends BaseMessage {
  tipo: "CONECTAR";
  nombre: string;
  color?: string;
}