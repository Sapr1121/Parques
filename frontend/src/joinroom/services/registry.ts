// frontend/src/joinroom/services/registry.ts
export async function queryRoom(code: string) {
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';
  const res = await fetch(`${API_URL}/api/query-room?code=${code}`);
  return await res.json();
}