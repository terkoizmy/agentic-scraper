import { useState, useCallback, useEffect } from 'react';
import type { ChatMessage } from '../types/agent-types';
import { RoleType } from '../types/agent-types';
import { askAgent } from '../api/agent-api';

const SESSION_STORAGE_KEY = 'agentic_chat_session_id';
const MESSAGES_STORAGE_KEY = 'agentic_chat_messages';

export const useAgentChat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    const saved = localStorage.getItem(MESSAGES_STORAGE_KEY);
    return saved ? JSON.parse(saved) : [];
  });
  
  const [isLoading, setIsLoading] = useState<boolean>(false);
  
  const [sessionId, setSessionId] = useState<string | undefined>(() => {
    return localStorage.getItem(SESSION_STORAGE_KEY) || undefined;
  });

  // Sync to localStorage
  useEffect(() => {
    localStorage.setItem(MESSAGES_STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    if (sessionId) {
      localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
    }
  }, [sessionId]);

  const clearSession = useCallback(() => {
    setMessages([]);
    setSessionId(undefined);
    localStorage.removeItem(SESSION_STORAGE_KEY);
    localStorage.removeItem(MESSAGES_STORAGE_KEY);
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: RoleType.USER,
      content,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await askAgent({
        message: content,
        session_id: sessionId,
      });

      if (!sessionId) {
        setSessionId(response.session_id);
      }

      const agentMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: RoleType.AGENT,
        content: response.answer,
        toolCalls: response.tool_calls,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, agentMsg]);
    } catch (error) {
      const errorMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: RoleType.AGENT,
        content: 'Maaf, terjadi kesalahan saat menghubungi agent. Pastikan backend sudah menyala.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  return {
    messages,
    isLoading,
    sendMessage,
    clearSession,
  };
};
