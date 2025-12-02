/**
 * Servicio de autenticación - Comunicación con el servidor de Python
 */

const WS_URL = 'ws://localhost:8001';

interface RegistroResponse {
  exito: boolean;
  mensaje: string;
}

interface LoginResponse {
  exito: boolean;
  mensaje: string;
  usuario_id: number | null;
}

interface Estadisticas {
  username: string;
  partidas_jugadas: number;
  partidas_ganadas: number;
  partidas_perdidas: number;
  tasa_victoria: number;
  fichas_totales_en_meta: number;
  ultimas_partidas: Array<{
    fecha: string;
    resultado: string;
    color_jugado: string;
    fichas_en_meta: number;
    turnos_jugados: number;
    tiempo_juego: number;
  }>;
}

interface EstadisticasResponse {
  exito: boolean;
  mensaje: string;
  estadisticas: Estadisticas | null;
}

/**
 * Envía un mensaje al servidor WebSocket y espera la respuesta
 */
async function enviarMensajeWS(mensaje: any): Promise<any> {
  return new Promise((resolve, reject) => {
    let ws: WebSocket | null = null;
    let timeoutId: NodeJS.Timeout | null = null;
    let resolved = false;
    
    const cleanup = () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
        timeoutId = null;
      }
      if (ws && ws.readyState !== WebSocket.CLOSED) {
        ws.close();
      }
    };
    
    try {
      ws = new WebSocket(WS_URL);
      
      ws.onopen = () => {
        console.log('[Auth] WebSocket conectado, enviando mensaje:', mensaje.tipo);
        ws?.send(JSON.stringify(mensaje));
      };
      
      ws.onmessage = (event) => {
        if (resolved) return;
        resolved = true;
        
        try {
          const respuesta = JSON.parse(event.data);
          console.log('[Auth] Respuesta recibida:', respuesta);
          cleanup();
          resolve(respuesta);
        } catch (e) {
          console.error('[Auth] Error parseando respuesta:', e);
          cleanup();
          reject(new Error('Respuesta inválida del servidor'));
        }
      };
      
      ws.onerror = (error) => {
        if (resolved) return;
        resolved = true;
        console.error('[Auth] Error WebSocket:', error);
        cleanup();
        reject(new Error('Error de conexión con el servidor'));
      };
      
      ws.onclose = (event) => {
        if (resolved) return;
        resolved = true;
        console.log('[Auth] WebSocket cerrado:', event.code, event.reason);
        cleanup();
        reject(new Error('Conexión cerrada antes de recibir respuesta'));
      };
      
      // Timeout de 10 segundos
      timeoutId = setTimeout(() => {
        if (resolved) return;
        resolved = true;
        console.error('[Auth] Timeout esperando respuesta');
        cleanup();
        reject(new Error('Timeout: El servidor no respondió'));
      }, 10000);
      
    } catch (error) {
      resolved = true;
      cleanup();
      reject(error);
    }
  });
}

/**
 * Registra un nuevo usuario en el sistema
 */
export async function registrarUsuario(
  username: string, 
  password: string, 
  email?: string
): Promise<RegistroResponse> {
  try {
    const mensaje = {
      tipo: 'REGISTRAR_USUARIO',
      username,
      password,
      email: email || null
    };
    
    const respuesta = await enviarMensajeWS(mensaje);
    
    return {
      exito: respuesta.exito,
      mensaje: respuesta.mensaje
    };
  } catch (error) {
    console.error('Error en registrarUsuario:', error);
    return {
      exito: false,
      mensaje: 'Error de conexión con el servidor'
    };
  }
}

/**
 * Inicia sesión con un usuario existente
 */
export async function loginUsuario(
  username: string, 
  password: string
): Promise<LoginResponse> {
  try {
    const mensaje = {
      tipo: 'LOGIN_USUARIO',
      username,
      password
    };
    
    const respuesta = await enviarMensajeWS(mensaje);
    
    return {
      exito: respuesta.exito,
      mensaje: respuesta.mensaje,
      usuario_id: respuesta.usuario_id
    };
  } catch (error) {
    console.error('Error en loginUsuario:', error);
    return {
      exito: false,
      mensaje: 'Error de conexión con el servidor',
      usuario_id: null
    };
  }
}

/**
 * Obtiene las estadísticas de un usuario
 */
export async function obtenerEstadisticas(usuario_id: number): Promise<EstadisticasResponse> {
  try {
    const mensaje = {
      tipo: 'OBTENER_ESTADISTICAS',
      usuario_id
    };
    
    const respuesta = await enviarMensajeWS(mensaje);
    
    return {
      exito: respuesta.exito,
      mensaje: respuesta.mensaje,
      estadisticas: respuesta.estadisticas
    };
  } catch (error) {
    console.error('Error en obtenerEstadisticas:', error);
    return {
      exito: false,
      mensaje: 'Error de conexión con el servidor',
      estadisticas: null
    };
  }
}

/**
 * Guarda la sesión del usuario en localStorage
 */
export function guardarSesion(username: string, usuario_id: number) {
  localStorage.setItem('usuario_username', username);
  localStorage.setItem('usuario_id', usuario_id.toString());
}

/**
 * Obtiene la sesión del usuario desde localStorage
 */
export function obtenerSesion(): { username: string; usuario_id: number } | null {
  const username = localStorage.getItem('usuario_username');
  const usuario_id = localStorage.getItem('usuario_id');
  
  if (username && usuario_id) {
    return {
      username,
      usuario_id: parseInt(usuario_id)
    };
  }
  
  return null;
}

/**
 * Cierra la sesión del usuario
 */
export function cerrarSesion() {
  localStorage.removeItem('usuario_username');
  localStorage.removeItem('usuario_id');
}

/**
 * Verifica si hay una sesión activa
 */
export function haySesionActiva(): boolean {
  return obtenerSesion() !== null;
}
