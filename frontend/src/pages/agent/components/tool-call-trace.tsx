import { useState } from 'react';
import { Code, Terminal, ChevronDown, ChevronUp } from 'lucide-react';
import type { ToolCall } from '../types/agent-types';

interface ToolCallTraceProps {
  toolCalls: ToolCall[];
}

export const ToolCallTrace = ({ toolCalls }: ToolCallTraceProps) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(false);

  if (!toolCalls || toolCalls.length === 0) {
    return null;
  }

  const toggleExpand = () => setIsExpanded((prev) => !prev);

  return (
    <div className="mt-3 bg-zinc-100 dark:bg-zinc-800 rounded-lg border border-zinc-200 dark:border-zinc-700 overflow-hidden text-sm">
      <button
        onClick={toggleExpand}
        className="w-full flex items-center justify-between px-4 py-2 hover:bg-zinc-200 dark:hover:bg-zinc-700 transition"
      >
        <div className="flex items-center gap-2 text-zinc-600 dark:text-zinc-300 font-medium">
          <Terminal className="w-4 h-4" />
          <span>Agent memanggil {toolCalls.length} fungsi (tools)</span>
        </div>
        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {isExpanded && (
        <div className="p-4 space-y-4 border-t border-zinc-200 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-900 overflow-x-auto">
          {toolCalls.map((call, idx) => (
            <div key={idx} className="space-y-2">
              <div className="flex items-center gap-2 font-mono text-xs text-blue-600 dark:text-blue-400">
                <Code className="w-3 h-3" />
                {call.tool}()
              </div>
              <div className="pl-5 space-y-1">
                <div className="text-zinc-500 text-xs">Arguments:</div>
                <pre className="bg-zinc-200 dark:bg-zinc-800 p-2 rounded text-xs text-zinc-800 dark:text-zinc-200 font-mono whitespace-pre-wrap">
                  {JSON.stringify(call.args, null, 2)}
                </pre>
                <div className="text-zinc-500 text-xs mt-2">Result:</div>
                <pre className="bg-zinc-200 dark:bg-zinc-800 p-2 rounded text-xs text-zinc-800 dark:text-zinc-200 font-mono whitespace-pre-wrap max-h-40 overflow-y-auto">
                  {JSON.stringify(call.result, null, 2)}
                </pre>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
