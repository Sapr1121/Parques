import axios from 'axios';

const REGISTRY_URL = import.meta.env.VITE_REGISTRY_URL || 'http://localhost:9000';

export const registerRoom = async (hexCode: string, gamePort: number, hostName: string, ipAddress: string) => {
  const res = await axios.post(REGISTRY_URL, {
    action: 'REGISTER',
    hex_code: hexCode,
    game_port: gamePort,
    host_name: hostName,
    ip_address: ipAddress,
  });
  return res.data;
};

export const unregisterRoom = async (hexCode: string) => {
  await axios.post(REGISTRY_URL, {
    action: 'UNREGISTER',
    hex_code: hexCode,
  });
};

export const pingRegistry = async () => {
  try {
    const res = await axios.post(REGISTRY_URL, { action: 'PING' });
    return res.data.status === 'success';
  } catch {
    return false;
  }
};