"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.launchPythonServers = launchPythonServers;
exports.killPythonServers = killPythonServers;
const child_process_1 = require("child_process");
const path_1 = __importDefault(require("path"));
const fs_1 = __importDefault(require("fs"));
const PYTHON_ROOT = path_1.default.resolve(__dirname, '..', '..', process.env.PYTHON_ROOT || 'pythonserver');
// 🔧 Resolver PYTHON_CMD a ruta absoluta
function resolvePythonCmd() {
    const envCmd = process.env.PYTHON_CMD;
    if (envCmd) {
        // Si es ruta absoluta, usarla directamente
        if (path_1.default.isAbsolute(envCmd)) {
            return envCmd;
        }
        // Si es relativa, resolverla desde backend/
        const resolved = path_1.default.resolve(__dirname, '..', envCmd);
        if (fs_1.default.existsSync(resolved)) {
            console.log(`✅ Python encontrado en: ${resolved}`);
            return resolved;
        }
    }
    // Fallback: intentar venv local
    const venvPython = path_1.default.join(PYTHON_ROOT, 'venv', 'bin', 'python3');
    if (fs_1.default.existsSync(venvPython)) {
        console.log(`✅ Python encontrado en venv: ${venvPython}`);
        return venvPython;
    }
    console.warn('⚠️ No se encontró Python en venv, usando "python3" del sistema');
    return 'python3';
}
const PYTHON_CMD = resolvePythonCmd();
let serverProcess = null;
let registryProcess = null;
function launchPythonServers() {
    if (!serverProcess || serverProcess.killed) {
        console.log(`🐍 [PYTHON] Lanzando servidor de juego...`);
        console.log(`   - Comando: ${PYTHON_CMD}`);
        console.log(`   - Script: server/server.py`);
        console.log(`   - Directorio: ${PYTHON_ROOT}`);
        serverProcess = (0, child_process_1.spawn)(PYTHON_CMD, ['server/server.py'], {
            cwd: PYTHON_ROOT,
            stdio: ['ignore', 'pipe', 'pipe'],
        });
        serverProcess.stdout?.on('data', (data) => {
            console.log('[Python Server]', data.toString().trim());
        });
        serverProcess.stderr?.on('data', (data) => {
            console.error('[Python Server Error]', data.toString().trim());
        });
        serverProcess.on('error', (err) => {
            console.error('❌ [Python Server] Error al iniciar:', err.message);
            console.error(`💡 Comando intentado: ${PYTHON_CMD}`);
            console.error(`💡 ¿Existe? ${fs_1.default.existsSync(PYTHON_CMD)}`);
        });
        serverProcess.on('exit', (code) => {
            console.log(`🛑 [Python Server] Proceso terminado con código ${code}`);
            serverProcess = null;
        });
    }
    else {
        console.log(`ℹ️ [PYTHON] Servidor de juego ya está corriendo (PID: ${serverProcess.pid})`);
    }
    if (!registryProcess || registryProcess.killed) {
        console.log(`🐍 [PYTHON] Lanzando servidor de registro...`);
        console.log(`   - Comando: ${PYTHON_CMD}`);
        console.log(`   - Script: game/hybrid.py registry`);
        registryProcess = (0, child_process_1.spawn)(PYTHON_CMD, ['game/hybrid.py', 'registry'], {
            cwd: PYTHON_ROOT,
            stdio: ['ignore', 'pipe', 'pipe'],
        });
        registryProcess.stdout?.on('data', (data) => {
            console.log('[Registry]', data.toString().trim());
        });
        registryProcess.stderr?.on('data', (data) => {
            console.error('[Registry Error]', data.toString().trim());
        });
        registryProcess.on('error', (err) => {
            console.error('❌ [Registry] Error al iniciar:', err.message);
        });
        registryProcess.on('exit', (code) => {
            console.log(`🛑 [Registry] Proceso terminado con código ${code}`);
            registryProcess = null;
        });
    }
    else {
        console.log(`ℹ️ [PYTHON] Servidor de registro ya está corriendo (PID: ${registryProcess.pid})`);
    }
    return { server: serverProcess, registry: registryProcess };
}
function killPythonServers() {
    if (serverProcess && !serverProcess.killed) {
        console.log('🛑 Deteniendo servidor de juego...');
        serverProcess.kill();
    }
    if (registryProcess && !registryProcess.killed) {
        console.log('🛑 Deteniendo servidor de registro...');
        registryProcess.kill();
    }
    serverProcess = null;
    registryProcess = null;
}
