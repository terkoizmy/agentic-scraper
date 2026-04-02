import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(`API Error: ${error.response.status}`);
    }
    throw new Error('Network error');
  }
);

export const getAgentSettings = async () => {
  const response = await apiClient.get('/settings/agent');
  return response.data;
};

export const patchAgentSettings = async (patch: Partial<{ thinking_enabled: boolean; thinking_max_tokens: number }>) => {
  const response = await apiClient.patch('/settings/agent', patch);
  return response.data;
};