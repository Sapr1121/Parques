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
  return new Promise((resolve, reject) => {
    const client = new net.Socket();
    let responseData = '';

    client.connect(REGISTRY_PORT, REGISTRY_HOST, () => {
      const registerMessage = `REGISTER|${code}|${ip}|${port}|${hostName}\n`;
      client.write(registerMessage);
    });

    client.on('data', (data) => {
      responseData += data.toString();
      if (responseData.includes('\n')) {
        client.end();
        const response = responseData.trim();
        if (response.startsWith('OK')) {
          resolve({ success: true, message: response });
        } else {
          resolve({ success: false, message: response });
        }
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
