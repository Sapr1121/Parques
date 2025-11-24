import net from 'net';

const REGISTRY_HOST = process.env.REGISTRY_HOST || '127.0.0.1';
const REGISTRY_PORT = Number.parseInt(process.env.REGISTRY_PORT || '9000', 10);

interface RegistryResponse {
  success: boolean;
  message?: string;
}

export async function registerRoom(
  code: string,
  port: number,
  hostName: string,
  ip: string = '127.0.0.1',
): Promise<RegistryResponse> {
  console.log(`📝 [REGISTRY] Intentando registrar sala: ${code}`);
  console.log(`   - Host: ${REGISTRY_HOST}:${REGISTRY_PORT}`);
  console.log(`   - Sala: ${code} | IP: ${ip} | Puerto: ${port} | Jugador: ${hostName}`);
  
  return new Promise((resolve, reject) => {
    const client = new net.Socket();
    let responseData = '';

    client.connect(REGISTRY_PORT, REGISTRY_HOST, () => {
      const registerMessage = `REGISTER|${code}|${ip}|${port}|${hostName}\n`;
      console.log(`📤 [REGISTRY] Enviando: ${registerMessage.trim()}`);
      client.write(registerMessage);
    });

    client.on('data', (data) => {
      responseData += data.toString();
      console.log(`📥 [REGISTRY] Respuesta recibida: ${responseData}`);
      if (responseData.includes('\n')) {
        client.end();
        const response = responseData.trim();
        if (response.startsWith('OK')) {
          console.log(`✅ [REGISTRY] Registro exitoso: ${response}`);
          resolve({ success: true, message: response });
        } else {
          console.log(`⚠️ [REGISTRY] Registro falló: ${response}`);
          resolve({ success: false, message: response });
        }
      }
    });

    client.on('error', (err) => {
      console.error(`❌ [REGISTRY] Error de conexión: ${err.message}`);
      reject(new Error(`Error conectando al registro: ${err.message}`));
    });

    client.on('timeout', () => {
      console.error(`⏱️ [REGISTRY] Timeout esperando respuesta`);
      client.destroy();
      reject(new Error('Timeout conectando al registro'));
    });

    client.setTimeout(5000);
  });
}

export async function unregisterRoom(code: string): Promise<RegistryResponse> {
  return new Promise((resolve, reject) => {
    const client = new net.Socket();
    let responseData = '';

    client.connect(REGISTRY_PORT, REGISTRY_HOST, () => {
      const unregisterMessage = `UNREGISTER|${code}\n`;
      client.write(unregisterMessage);
    });

    client.on('data', (data) => {
      responseData += data.toString();
      if (responseData.includes('\n')) {
        client.end();
        resolve({ success: true, message: responseData.trim() });
      }
    });

    client.on('error', (err) => {
      reject(new Error(`Error conectando al registro: ${err.message}`));
    });

    client.on('timeout', () => {
      client.destroy();
      reject(new Error('Timeout conectando al registro'));
    });

    client.setTimeout(5000);
  });
}
