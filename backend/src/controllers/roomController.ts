import { queryRoom } from '../services/registryService';
// GET /api/query-room?code=HEXCODE
export const queryRoomController = async (req: Request, res: Response) => {
  const code = (req.query.code as string || '').toUpperCase();
  if (!code || code.length !== 8) {
    return res.status(400).json({ status: 'error', message: 'Código inválido' });
  }
  try {
    const result = await queryRoom(code);
    res.json(result);
  } catch (err) {
    console.error('[QUERY-ROOM] Error:', err);
    res.status(500).json({ status: 'error', message: 'Error consultando registro' });
  }
};
import { Request, Response } from 'express';
import crypto from 'crypto';
import os from 'os';
import { launchPythonServers } from '../services/pythonService';
import { registerRoom } from '../services/registryService';

interface CreateRoomBody {
  playerName: string;
  color: string;
}

/**
 * Obtiene la IP de red local (no loopback) para que otros equipos puedan conectarse
 */
function getLocalNetworkIP(): string {
  const interfaces = os.networkInterfaces();
  
  for (const name of Object.keys(interfaces)) {
    const iface = interfaces[name];
    if (!iface) continue;
    
    for (const alias of iface) {
      // Buscar IPv4, no interna (no 127.x.x.x), y que esté activa
      if (alias.family === 'IPv4' && !alias.internal) {
        console.log(
          `🌐 [NETWORK] IP de red local detectada: ${alias.address} (${name})`,
        );
        return alias.address;
      }
    }
  }
  
  console.warn(
    `⚠️ [NETWORK] No se encontró IP de red, usando 127.0.0.1 (solo local)`,
  );
  return '127.0.0.1';
}

export const createRoom = (
  req: Request<object, object, CreateRoomBody>,
  res: Response,
) => {
  const { playerName, color } = req.body;
  console.log(`🎮 [CREATE-ROOM] Nueva solicitud: ${playerName} (${color})`);
  
  if (!playerName || !color) {
    console.log(`❌ [CREATE-ROOM] Campos faltantes`);
    return res.status(400).json({ error: 'Faltan campos' });
  }

  try {
    // 1. Lanzar servidores Python (si no están corriendo)
    console.log(`🚀 [CREATE-ROOM] Lanzando servidores Python...`);
    launchPythonServers();

    // 2. Generar código de sala (4 bytes -> 8 hex chars)
    const code = crypto.randomBytes(4).toString('hex').toUpperCase();

    const port = Number.parseInt(process.env.PYTHON_SERVER_PORT || '8001', 10);
    console.log(`🎫 [CREATE-ROOM] Código generado: ${code} | Puerto: ${port}`);

    // 3. Responder inmediatamente al cliente
    res.json({ code, port });
    console.log(`📤 [CREATE-ROOM] Respuesta enviada al cliente`);

    // 4. Registrar la sala en segundo plano (después de responder)
    console.log(
      `⏰ [CREATE-ROOM] Programando registro de sala en 2 segundos...`,
    );
    setTimeout(() => {
      console.log(`🔄 [CREATE-ROOM] Iniciando registro de sala...`);
      const localIP = getLocalNetworkIP();
      registerRoom(code, port, playerName, localIP)
        .then(() => {
          console.log(`✅ [CREATE-ROOM] Sala ${code} registrada exitosamente`);
        })
        .catch((regErr) => {
          console.error(`⚠️ [CREATE-ROOM] Error registrando sala:`, regErr);
        });
    }, 2000);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error interno' });
  }
};
