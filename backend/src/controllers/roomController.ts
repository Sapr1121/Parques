import { Request, Response } from 'express';
import crypto from 'crypto';
import { launchPythonServers } from '../services/pythonService';
import { registerRoom } from '../services/registryService';

interface CreateRoomBody {
  playerName: string;
  color: string;
}

export const createRoom = async (
  req: Request<object, object, CreateRoomBody>,
  res: Response,
) => {
  const { playerName, color } = req.body;
  if (!playerName || !color) {
    return res.status(400).json({ error: 'Faltan campos' });
  }

  try {
    // 1. Lanzar servidores Python
    launchPythonServers();

    // 2. Generar código de sala
    const code = [...crypto.getRandomValues(new Uint8Array(4))]
      .map((b) => b.toString(16).toUpperCase().padStart(2, '0'))
      .join('');

    const port = Number.parseInt(process.env.PYTHON_SERVER_PORT || '8001', 10);

    // 3. Esperar un poco para que los servidores se inicien
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // 4. Registrar la sala en el servidor de registro
    try {
      await registerRoom(code, port, playerName, '127.0.0.1');
      console.log(`✅ Sala ${code} registrada exitosamente`);
    } catch (regErr) {
      console.error('⚠️ Error registrando sala:', regErr);
      // Continuar de todos modos
    }

    // 5. Responder con el código y puerto
    res.json({ code, port });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error interno' });
  }
};
