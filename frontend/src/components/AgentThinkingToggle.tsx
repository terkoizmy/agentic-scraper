import { Brain, Loader2 } from 'lucide-react';
import { useAgentSettings } from '@/hooks/useAgentSettings';

export function AgentThinkingToggle() {
  const { settings, loading, updateSettings } = useAgentSettings();

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-zinc-500">
        <Loader2 className="w-4 h-4 animate-spin" />
        <span className="text-sm">Loading...</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-2">
        <Brain className="w-4 h-4 text-zinc-600 dark:text-zinc-400" />
        <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">AI Thinking</span>
      </div>
      <button
        onClick={() => updateSettings({ thinkingEnabled: !settings.thinkingEnabled })}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
          settings.thinkingEnabled
            ? 'bg-indigo-600'
            : 'bg-zinc-300 dark:bg-zinc-600'
        }`}
        aria-label={`AI Thinking ${settings.thinkingEnabled ? 'enabled' : 'disabled'}`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition-transform duration-200 ${
            settings.thinkingEnabled ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
      <span className="text-xs text-zinc-500 dark:text-zinc-400">
        {settings.thinkingEnabled ? 'On' : 'Off'}
      </span>
    </div>
  );
}