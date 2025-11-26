import { spawn, ChildProcess } from 'child_process';
import path from 'path';
import fs from 'fs';

const PYTHON_ROOT = path.resolve(
  __dirname,
  '..',
  '..',
  process.env.PYTHON_ROOT || 'pythonserver',
);

// 🔧 Resolver PYTHON_CMD a ruta absoluta
function resolvePythonCmd(): string {
  const envCmd = process.env.PYTHON_CMD;
  
  if (envCmd) {
    // Si es ruta absoluta, usarla directamente
    if (path.isAbsolute(envCmd)) {
      return envCmd;
    }
    // Si es relativa, resolverla desde backend/
    const resolved = path.resolve(__dirname, '..', envCmd);
    if (fs.existsSync(resolved)) {
      console.log(`✅ Python encontrado en: ${resolved}`);
      return resolved;
    }
  }
  
  // Fallback: intentar venv local
  const venvPython = path.join(PYTHON_ROOT, 'venv', 'bin', 'python3');
  if (fs.existsSync(venvPython)) {
    console.log(`✅ Python encontrado en venv: ${venvPython}`);
    return venvPython;
  }
  
  console.warn('⚠️ No se encontró Python en venv, usando "python3" del sistema');
  return 'python3';
}

const PYTHON_CMD = resolvePythonCmd();

let serverProcess: ChildProcess | null = null;
let registryProcess: ChildProcess | null = null;

export function launchPythonServers() {
  if (!serverProcess || serverProcess.killed) {
    console.log(`🐍 [PYTHON] Lanzando servidor de juego...`);
    console.log(`   - Comando: ${PYTHON_CMD}`);
    console.log(`   - Script: server/server.py`);
    console.log(`   - Directorio: ${PYTHON_ROOT}`);
    
    serverProcess = spawn(PYTHON_CMD, ['server/server.py'], {
      cwd: PYTHON_ROOT,
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    serverProcess.stdout?.on('data', (data: Buffer) => {
      console.log('[Python Server]', data.toString().trim());
    });
    
    serverProcess.stderr?.on('data', (data: Buffer) => {
      console.error('[Python Server Error]', data.toString().trim());
    });
    
    serverProcess.on('error', (err) => {
      console.error('❌ [Python Server] Error al iniciar:', err.message);
      console.error(`💡 Comando intentado: ${PYTHON_CMD}`);
      console.error(`💡 ¿Existe? ${fs.existsSync(PYTHON_CMD)}`);
    });
    
    serverProcess.on('exit', (code) => {
      console.log(`🛑 [Python Server] Proceso terminado con código ${code}`);
      serverProcess = null;
    });
  } else {
    console.log(`ℹ️ [PYTHON] Servidor de juego ya está corriendo (PID: ${serverProcess.pid})`);
  }

  if (!registryProcess || registryProcess.killed) {
    console.log(`🐍 [PYTHON] Lanzando servidor de registro...`);
    console.log(`   - Comando: ${PYTHON_CMD}`);
    console.log(`   - Script: game/hybrid.py registry`);
    
    registryProcess = spawn(PYTHON_CMD, ['game/hybrid.py', 'registry'], {
      cwd: PYTHON_ROOT,
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    registryProcess.stdout?.on('data', (data: Buffer) => {
      console.log('[Registry]', data.toString().trim());
    });
    
    registryProcess.stderr?.on('data', (data: Buffer) => {
      console.error('[Registry Error]', data.toString().trim());
    });
    
    registryProcess.on('error', (err) => {
      console.error('❌ [Registry] Error al iniciar:', err.message);
    });
    
    registryProcess.on('exit', (code) => {
      console.log(`🛑 [Registry] Proceso terminado con código ${code}`);
      registryProcess = null;
    });
  } else {
    console.log(`ℹ️ [PYTHON] Servidor de registro ya está corriendo (PID: ${registryProcess.pid})`);
  }

  return { server: serverProcess, registry: registryProcess };
}

export function killPythonServers() {
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