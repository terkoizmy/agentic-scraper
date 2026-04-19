import axios from 'axios';
import type { AgentAskRequest, AgentAskResponse } from '../types/agent-types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export interface SessionListItem {
  session_id: string;
  first_message: string | null;
  last_message: string | null;
  created_at: string | null;
}

export interface SessionListResponse {
  sessions: SessionListItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface SessionMessage {
  role: string;
  content: string;
  tool_calls: Record<string, unknown>[] | null;
  created_at: string | null;
}

export interface SessionHistoryResponse {
  session_id: string;
  messages: SessionMessage[];
}

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

export const listSessions = async (limit = 50, offset = 0): Promise<SessionListResponse> => {
  try {
    const response = await axios.get<SessionListResponse>(
      `${API_BASE_URL}/agent/sessions?limit=${limit}&offset=${offset}`,
    );
    return response.data;
  } catch (error) {
    throw new Error('Failed to fetch session list');
  }
};

export const getSessionHistory = async (sessionId: string): Promise<SessionHistoryResponse> => {
  try {
    const response = await axios.get<SessionHistoryResponse>(
      `${API_BASE_URL}/agent/sessions/${sessionId}`,
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      throw new Error('Session not found');
    }
    throw new Error('Failed to fetch session history');
  }
};
