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
        className="w-full flex items-center justify-between px-4 py-2.5 hover:bg-zinc-200 dark:hover:bg-zinc-700/80 transition-colors"
      >
        <div className="flex items-center gap-2 text-zinc-700 dark:text-zinc-300 font-medium">
          <Terminal className="w-4 h-4 text-zinc-500" />
          <span>Melihat proses berpikir dan {toolCalls.length} eksekusi tool</span>
        </div>
        {isExpanded ? <ChevronUp className="w-4 h-4 text-zinc-500" /> : <ChevronDown className="w-4 h-4 text-zinc-500" />}
      </button>

      {isExpanded && (
        <div className="p-4 space-y-4 border-t border-zinc-200 dark:border-zinc-700 bg-zinc-50/50 dark:bg-zinc-900/50">
          {toolCalls.map((call, idx) => {
            let label = call.tool;
            let argSummary = "";
            if (call.tool === "rag_query") {
              label = "Mencari konteks di Vector DB";
              argSummary = `Kueri: "${call.args?.q || ''}" (Top K: ${call.args?.top_k || 5})`;
            } else if (call.tool === "web_search") {
              label = "Menelusuri internet (DuckDuckGo)";
              argSummary = `Pencarian: "${call.args?.query || ''}"`;
            } else if (call.tool === "deep_research") {
              label = "Proses Deep Research / Auto-Crawl";
              argSummary = `Pencarian: "${call.args?.query || ''}"`;
            } else if (call.tool === "scrape_page") {
              label = "Merayapi halaman web (Scrape)";
              argSummary = `URL: ${call.args?.url || ''}`;
            }

            return (
              <div key={idx} className="space-y-2 border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 p-3 rounded-xl shadow-sm">
                <div className="flex flex-col gap-1">
                  <div className="flex items-center gap-2 font-medium text-sm text-indigo-600 dark:text-indigo-400">
                    <Code className="w-4 h-4" />
                    {label}
                  </div>
                  {argSummary && (
                    <div className="text-xs text-zinc-500 font-mono ml-6 bg-zinc-100 dark:bg-zinc-900 px-2 py-1 rounded inline-block w-fit">
                      {argSummary}
                    </div>
                  )}
                </div>
                
                <div className="pl-6 space-y-1.5 mt-2">
                  <div className="text-zinc-500 text-[11px] uppercase tracking-wider font-semibold">Hasil (JSON Payload):</div>
                  <pre className="bg-zinc-100 dark:bg-zinc-900 p-2.5 rounded-lg text-xs text-zinc-700 dark:text-zinc-300 font-mono whitespace-pre-wrap max-h-40 overflow-y-auto border border-zinc-200 dark:border-zinc-800">
                    {JSON.stringify(call.result, null, 2)}
                  </pre>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
