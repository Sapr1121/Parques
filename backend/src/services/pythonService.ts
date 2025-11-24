import { spawn, ChildProcess } from 'child_process';
import path from 'path';

const PYTHON_ROOT = path.resolve(
  __dirname,
  '..',
  '..',
  process.env.PYTHON_ROOT || 'pythonserver',
);

// Resolver la ruta del comando Python (puede ser relativa al backend)
const PYTHON_CMD_RAW = process.env.PYTHON_CMD || '/usr/bin/python3';
const PYTHON_CMD = path.isAbsolute(PYTHON_CMD_RAW)
  ? PYTHON_CMD_RAW
  : path.resolve(__dirname, '..', '..', PYTHON_CMD_RAW);

// Mantener instancias únicas de los servidores
let serverProcess: ChildProcess | null = null;
let registryProcess: ChildProcess | null = null;

export function launchPythonServers() {
  // Solo lanzar si no están corriendo
  if (!serverProcess || serverProcess.killed) {
    console.log(`🐍 [PYTHON] Lanzando servidor de juego...`);
    console.log(`   - Comando: ${PYTHON_CMD}`);
    console.log(`   - Script: server/server.py`);
    console.log(`   - Directorio: ${PYTHON_ROOT}`);
    serverProcess = spawn(PYTHON_CMD, ['server/server.py'], {
      cwd: PYTHON_ROOT,
      env: { ...process.env },
    });

    serverProcess.stdout?.on('data', (data: Buffer) => {
      console.log('[Python Server]', data.toString().trim());
    });
    serverProcess.stderr?.on('data', (data: Buffer) => {
      console.error('[Python Server Error]', data.toString().trim());
    });
    serverProcess.on('exit', (code) => {
      console.log(`[Python Server] Proceso terminado con código ${code}`);
      serverProcess = null;
    });
  } else {
    console.log(`ℹ️ [PYTHON] Servidor de juego ya está corriendo (PID: ${serverProcess.pid})`);
  }

  if (!registryProcess || registryProcess.killed) {
    console.log(`🐍 [PYTHON] Lanzando servidor de registro...`);
    console.log(`   - Comando: ${PYTHON_CMD}`);
    console.log(`   - Script: game/hybrid.py registry`);
    console.log(`   - Directorio: ${PYTHON_ROOT}`);
    
    registryProcess = spawn(PYTHON_CMD, ['game/hybrid.py', 'registry'], {
      cwd: PYTHON_ROOT,
      env: { ...process.env },
    });

    registryProcess.stdout?.on('data', (data: Buffer) => {
      console.log('[Registry]', data.toString().trim());
    });
    registryProcess.stderr?.on('data', (data: Buffer) => {
      console.error('[Registry Error]', data.toString().trim());
    });
    registryProcess.on('exit', (code) => {
      console.log(`[Registry] Proceso terminado con código ${code}`);
      registryProcess = null;
    });
  } else {
    console.log(`ℹ️ [PYTHON] Servidor de registro ya está corriendo (PID: ${registryProcess.pid})`);
  }

  return { server: serverProcess, registry: registryProcess };
}

export function killPythonServers() {
  serverProcess?.kill();
  registryProcess?.kill();
  serverProcess = null;
  registryProcess = null;
}
