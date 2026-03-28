import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export const ChatInput = ({ onSendMessage, isLoading }: ChatInputProps) => {
  const [inputText, setInputText] = useState('');

  const handleSend = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputText.trim() || isLoading) return;

    onSendMessage(inputText);
    setInputText('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-zinc-200 dark:border-zinc-800 p-4 bg-white/50 dark:bg-zinc-950/50 backdrop-blur pb-6">
      <form
        onSubmit={handleSend}
        className="max-w-4xl mx-auto flex items-end gap-3"
      >
        <textarea
          className="flex-1 max-h-40 min-h-[60px] p-4 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all resize-none shadow-inner"
          placeholder="Tanyakan sesuatu pada Agent (misal: 'Carikan info terbaru tentang framework React dari react.dev')..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={!inputText.trim() || isLoading}
          className="p-4 bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-300 dark:disabled:bg-zinc-700 disabled:cursor-not-allowed text-white rounded-xl shadow-md transition-all h-[60px] w-[60px] flex items-center justify-center shrink-0"
        >
          {isLoading ? <Loader2 className="w-6 h-6 animate-spin" /> : <Send className="w-6 h-6" />}
        </button>
      </form>
    </div>
  );
};
