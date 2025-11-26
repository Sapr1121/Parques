export async function queryRoom(code: string): Promise<any> {
  return new Promise((resolve, reject) => {
    const client = new net.Socket();
    let responseData = '';

    client.connect(REGISTRY_PORT, REGISTRY_HOST, () => {
      const queryMessageObj = { action: 'QUERY', hex_code: code };
      const queryMessage = JSON.stringify(queryMessageObj);
      console.log(`📤 [REGISTRY] Enviando QUERY JSON: ${queryMessage}`);
      client.write(queryMessage);
    });

    client.on('data', (data) => {
      responseData += data.toString();
      try {
        const parsed = JSON.parse(responseData);
        client.end();
        resolve(parsed);
      } catch {
        // esperar más datos
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
  console.log(
    `   - Sala: ${code} | IP: ${ip} | Puerto: ${port} | Jugador: ${hostName}`,
  );
  
  return new Promise((resolve, reject) => {
    const client = new net.Socket();
    let responseData = '';

    client.connect(REGISTRY_PORT, REGISTRY_HOST, () => {
      const registerMessageObj = {
        action: 'REGISTER',
        hex_code: code,
        game_port: port,
        host_name: hostName,
        ip_address: ip,
      };
      const registerMessage = JSON.stringify(registerMessageObj);
      console.log(`📤 [REGISTRY] Enviando JSON: ${registerMessage}`);
      client.write(registerMessage);
    });

    client.on('data', (data) => {
      responseData += data.toString();
      console.log(`📥 [REGISTRY] Respuesta cruda: ${responseData}`);
      // El servidor devuelve un JSON (sin newline obligatorio)
      try {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        const parsed = JSON.parse(responseData);
        client.end();
        // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
        if (parsed.status === 'success') {
          console.log(
            `✅ [REGISTRY] Registro exitoso: ${JSON.stringify(parsed)}`,
          );
          resolve({ success: true, message: JSON.stringify(parsed) });
        } else {
          console.log(
            `⚠️ [REGISTRY] Registro falló: ${JSON.stringify(parsed)}`,
          );
          resolve({ success: false, message: JSON.stringify(parsed) });
        }
      } catch {
        // aún no tenemos JSON completo; esperar más datos
        console.log(`ℹ️ [REGISTRY] Esperando más datos para formar JSON...`);
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
      const unregisterMessageObj = { action: 'UNREGISTER', hex_code: code };
      const unregisterMessage = JSON.stringify(unregisterMessageObj);
      console.log(
        `📤 [REGISTRY] Enviando UNREGISTER JSON: ${unregisterMessage}`,
      );
      client.write(unregisterMessage);
    });

    client.on('data', (data) => {
      responseData += data.toString();
      try {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        const parsed = JSON.parse(responseData);
        client.end();
        resolve({
          // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
          success: parsed.status === 'success',
          message: JSON.stringify(parsed),
        });
      } catch {
        // esperar más datos
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
