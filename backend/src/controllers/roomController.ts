import { Request, Response } from 'express';
import crypto from 'crypto';
import { launchPythonServers } from '../services/pythonService';
import { registerRoom } from '../services/registryService';

interface CreateRoomBody {
  playerName: string;
  color: string;
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

    // 2. Generar código de sala
    const code = [...crypto.getRandomValues(new Uint8Array(4))]
      .map((b) => b.toString(16).toUpperCase().padStart(2, '0'))
      .join('');

    const port = Number.parseInt(process.env.PYTHON_SERVER_PORT || '8001', 10);
    console.log(`🎫 [CREATE-ROOM] Código generado: ${code} | Puerto: ${port}`);

    // 3. Responder inmediatamente al cliente
    res.json({ code, port });
    console.log(`📤 [CREATE-ROOM] Respuesta enviada al cliente`);

    // 4. Registrar la sala en segundo plano (después de responder)
    console.log(`⏰ [CREATE-ROOM] Programando registro de sala en 2 segundos...`);
    setTimeout(() => {
      console.log(`🔄 [CREATE-ROOM] Iniciando registro de sala...`);
      registerRoom(code, port, playerName, '127.0.0.1')
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
