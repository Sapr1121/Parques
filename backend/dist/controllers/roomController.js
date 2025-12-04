"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createRoom = exports.queryRoomController = void 0;
const registryService_1 = require("../services/registryService");
// GET /api/query-room?code=HEXCODE
const queryRoomController = async (req, res) => {
    const code = (req.query.code || '').toUpperCase();
    if (!code || code.length !== 8) {
        return res.status(400).json({ status: 'error', message: 'Código inválido' });
    }
    try {
        const result = await (0, registryService_1.queryRoom)(code);
        res.json(result);
    }
    catch (err) {
        console.error('[QUERY-ROOM] Error:', err);
        res.status(500).json({ status: 'error', message: 'Error consultando registro' });
    }
};
exports.queryRoomController = queryRoomController;
const crypto_1 = __importDefault(require("crypto"));
const os_1 = __importDefault(require("os"));
const pythonService_1 = require("../services/pythonService");
const registryService_2 = require("../services/registryService");
/**
 * Obtiene la IP de red local (no loopback) para que otros equipos puedan conectarse
 */
function getLocalNetworkIP() {
    const interfaces = os_1.default.networkInterfaces();
    for (const name of Object.keys(interfaces)) {
        const iface = interfaces[name];
        if (!iface)
            continue;
        for (const alias of iface) {
            // Buscar IPv4, no interna (no 127.x.x.x), y que esté activa
            if (alias.family === 'IPv4' && !alias.internal) {
                console.log(`🌐 [NETWORK] IP de red local detectada: ${alias.address} (${name})`);
                return alias.address;
            }
        }
    }
    console.warn(`⚠️ [NETWORK] No se encontró IP de red, usando 127.0.0.1 (solo local)`);
    return '127.0.0.1';
}
const createRoom = (req, res) => {
    const { playerName, color } = req.body;
    console.log(`🎮 [CREATE-ROOM] Nueva solicitud: ${playerName} (${color})`);
    if (!playerName || !color) {
        console.log(`❌ [CREATE-ROOM] Campos faltantes`);
        return res.status(400).json({ error: 'Faltan campos' });
    }
    try {
        // 1. Lanzar servidores Python (si no están corriendo)
        console.log(`🚀 [CREATE-ROOM] Lanzando servidores Python...`);
        (0, pythonService_1.launchPythonServers)();
        // 2. Generar código de sala (4 bytes -> 8 hex chars)
        const code = crypto_1.default.randomBytes(4).toString('hex').toUpperCase();
        const port = Number.parseInt(process.env.PYTHON_SERVER_PORT || '8001', 10);
        console.log(`🎫 [CREATE-ROOM] Código generado: ${code} | Puerto: ${port}`);
        // 3. Responder inmediatamente al cliente
        res.json({ code, port });
        console.log(`📤 [CREATE-ROOM] Respuesta enviada al cliente`);
        // 4. Registrar la sala en segundo plano (después de responder)
        console.log(`⏰ [CREATE-ROOM] Programando registro de sala en 2 segundos...`);
        setTimeout(() => {
            console.log(`🔄 [CREATE-ROOM] Iniciando registro de sala...`);
            const localIP = getLocalNetworkIP();
            (0, registryService_2.registerRoom)(code, port, playerName, localIP)
                .then(() => {
                console.log(`✅ [CREATE-ROOM] Sala ${code} registrada exitosamente`);
            })
                .catch((regErr) => {
                console.error(`⚠️ [CREATE-ROOM] Error registrando sala:`, regErr);
            });
        }, 2000);
    }
    catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Error interno' });
    }
};
exports.createRoom = createRoom;
