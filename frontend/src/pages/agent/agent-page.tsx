import { useEffect, useRef } from 'react';
import { Bot, RefreshCw } from 'lucide-react';
import { useAgentChat } from './hooks/useAgentChat';
import { ChatBubble } from './components/chat-bubble';
import { ChatInput } from './components/chat-input';

export const AgentPage = () => {
  const { messages, isLoading, sendMessage, clearSession } = useAgentChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex flex-col h-full bg-zinc-50 dark:bg-zinc-950">
      {/* Header */}
      <div className="bg-white/80 dark:bg-zinc-950/80 backdrop-blur-md border-b border-zinc-200 dark:border-zinc-800 px-8 py-6 sticky top-0 z-10 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="bg-linear-to-br from-blue-500 to-indigo-600 p-2 rounded-lg shadow-sm">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-zinc-900 dark:text-white">Agent Console</h1>
            <p className="text-sm text-zinc-500 dark:text-zinc-400 mt-0.5">Berkomunikasi dengan MiniMax M2.7 Orchestrator</p>
          </div>
        </div>
        <button
          onClick={clearSession}
          title="Mulai Sesi Baru"
          className="p-2.5 rounded-lg border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-600 dark:text-zinc-300 transition-colors flex items-center gap-2 text-sm font-medium shadow-sm"
        >
          <RefreshCw className="w-4 h-4" />
          <span className="hidden sm:inline">Sesi Baru</span>
        </button>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-2">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-zinc-400 dark:text-zinc-600 space-y-4">
            <Bot className="w-20 h-20 opacity-20" />
            <h2 className="text-xl font-medium">Agent Siap Membantu</h2>
            <p className="max-w-md text-center text-sm leading-relaxed">
              Saya adalah Agent AI dengan kemampuan scraping. Anda bisa menyuruh saya mengekstrak data dari website, membaca dokumen, atau mencari informasi dari database RAG.
            </p>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto pb-4">
            {messages.map((msg) => (
              <ChatBubble key={msg.id} message={msg} />
            ))}
            
            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex items-end justify-start gap-3 mb-6 animate-pulse">
                <div className="bg-indigo-500 text-white p-2 rounded-full shadow-sm">
                  <Bot className="w-5 h-5" />
                </div>
                <div className="px-5 py-4 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-2xl rounded-bl-sm shadow-sm flex gap-2 items-center">
                  <span className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  <span className="ml-2 text-sm text-zinc-500 font-medium">Agent sedang berpikir dan menjalankan alat...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="shrink-0 z-20 sticky bottom-0">
         <ChatInput onSendMessage={sendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
};

export default AgentPage;
