import axios from 'axios';
import type { AgentAskRequest, AgentAskResponse } from '../types/agent-types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const askAgent = async (request: AgentAskRequest): Promise<AgentAskResponse> => {
  try {
    const response = await axios.post<AgentAskResponse>(`${API_BASE_URL}/agent/ask`, request);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(`API Error: ${error.response.status}`);
    }
    throw new Error('Failed to ask agent due to network error');
  }
};

export const getAgentStatus = async (sessionId: string): Promise<string[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/agent/status/${sessionId}`);
    return response.data.tools as string[];
  } catch (error) {
    return [];
  }
};
