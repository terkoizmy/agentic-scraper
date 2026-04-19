import { useState, useCallback } from 'react';
import { listSessions, getSessionHistory } from '../api/agent-api';
import type { SessionListItem, SessionMessage } from '../api/agent-api';

interface UseSessionHistoryReturn {
  sessions: SessionListItem[];
  isLoading: boolean;
  error: string | null;
  total: number;
  loadSessions: (limit?: number, offset?: number) => Promise<void>;
  loadSessionHistory: (sessionId: string) => Promise<SessionMessage[]>;
  clearError: () => void;
}

export const useSessionHistory = (): UseSessionHistoryReturn => {
  const [sessions, setSessions] = useState<SessionListItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  const loadSessions = useCallback(async (limit = 50, offset = 0) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await listSessions(limit, offset);
      setSessions(response.sessions);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sessions');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadSessionHistory = useCallback(async (sessionId: string): Promise<SessionMessage[]> => {
    setError(null);
    try {
      const response = await getSessionHistory(sessionId);
      return response.messages;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load session history';
      setError(message);
      throw err;
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    sessions,
    isLoading,
    error,
    total,
    loadSessions,
    loadSessionHistory,
    clearError,
  };
};