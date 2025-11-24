import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';

interface CreateRoomResponse {
  code: string;
  port: number;
}

export async function createRoom(playerName: string, color: string): Promise<CreateRoomResponse> {
  const response = await axios.post(`${API_URL}/api/create-room`, {
    playerName,
    color,
  });
  return response.data;
}