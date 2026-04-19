import { useEffect, useState } from 'react';
import { History, X, MessageSquare, ChevronRight } from 'lucide-react';
import { useSessionHistory } from '../hooks/useSessionHistory';
import type { SessionMessage } from '../api/agent-api';

interface SessionListProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectSession: (sessionId: string, messages: SessionMessage[]) => void;
}

export const SessionList = ({ isOpen, onClose, onSelectSession }: SessionListProps) => {
  const { sessions, isLoading, error, total, loadSessions, loadSessionHistory, clearError } = useSessionHistory();
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
  const [loadingHistory, setLoadingHistory] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadSessions(50, 0);
    }
  }, [isOpen, loadSessions]);

  const handleSelectSession = async (sessionId: string) => {
    setSelectedSessionId(sessionId);
    setLoadingHistory(true);
    try {
      const messages = await loadSessionHistory(sessionId);
      onSelectSession(sessionId, messages);
      onClose();
    } catch {
      clearError();
    } finally {
      setLoadingHistory(false);
      setSelectedSessionId(null);
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('id-ID', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const truncate = (text: string | null, maxLength = 60) => {
    if (!text) return 'Tidak ada pesan';
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
  };

  if (!isOpen) return null;

  return (
    <>
      <div
        className="fixed inset-0 bg-black/50 z-40"
        onClick={onClose}
      />
      <div className="fixed right-0 top-0 h-full w-full max-w-md bg-white dark:bg-zinc-950 shadow-xl z-50 flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-200 dark:border-zinc-800">
          <div className="flex items-center gap-3">
            <History className="w-5 h-5 text-zinc-500" />
            <h2 className="text-lg font-semibold text-zinc-900 dark:text-white">Riwayat Sesi</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-zinc-500" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="flex items-center justify-center h-40">
              <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : error ? (
            <div className="p-6 text-center">
              <p className="text-red-500 text-sm">{error}</p>
              <button
                onClick={() => loadSessions(50, 0)}
                className="mt-2 text-sm text-indigo-600 hover:underline"
              >
                Coba lagi
              </button>
            </div>
          ) : sessions.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-40 text-zinc-400">
              <MessageSquare className="w-10 h-10 mb-3 opacity-50" />
              <p className="text-sm">Belum ada riwayat sesi</p>
            </div>
          ) : (
            <div className="divide-y divide-zinc-100 dark:divide-zinc-800">
              {sessions.map((session) => (
                <button
                  key={session.session_id}
                  onClick={() => handleSelectSession(session.session_id)}
                  disabled={loadingHistory && selectedSessionId === session.session_id}
                  className="w-full px-6 py-4 text-left hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors disabled:opacity-50"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-zinc-900 dark:text-white truncate">
                        {truncate(session.last_message)}
                      </p>
                      <p className="text-xs text-zinc-400 mt-1">
                        {formatDate(session.created_at)}
                      </p>
                    </div>
                    {loadingHistory && selectedSessionId === session.session_id ? (
                      <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin shrink-0" />
                    ) : (
                      <ChevronRight className="w-5 h-5 text-zinc-300 dark:text-zinc-600 shrink-0" />
                    )}
                  </div>
                  {session.first_message && session.first_message !== session.last_message && (
                    <p className="text-xs text-zinc-400 mt-1 truncate">
                      Awal: {truncate(session.first_message, 40)}
                    </p>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>

        {total > 0 && (
          <div className="px-6 py-3 border-t border-zinc-200 dark:border-zinc-800 text-xs text-zinc-400 text-center">
            Total {total} sesi
          </div>
        )}
      </div>
    </>
  );
};