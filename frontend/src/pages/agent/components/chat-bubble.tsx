import { Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import type { ChatMessage } from '../types/agent-types';
import { RoleType } from '../types/agent-types';
import { ToolCallTrace } from './tool-call-trace';

interface ChatBubbleProps {
  message: ChatMessage;
}

export const ChatBubble = ({ message }: ChatBubbleProps) => {
  const isUser = message.role === RoleType.USER;

  const bubbleContainerClasses = isUser
    ? 'flex items-end justify-end gap-3 mb-6'
    : 'flex items-end justify-start gap-3 mb-6';

  const avatarClasses = isUser
    ? 'bg-blue-600 text-white p-2 rounded-full shadow-sm'
    : 'bg-indigo-500 text-white p-2 rounded-full shadow-sm';

  const messageClasses = isUser
    ? 'relative px-5 py-3.5 bg-blue-600 text-white max-w-[80%] lg:max-w-[70%] rounded-2xl rounded-br-sm shadow-md transition-all'
    : 'relative px-5 py-3.5 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 max-w-[80%] lg:max-w-[70%] border border-zinc-200 dark:border-zinc-700 shadow-sm rounded-2xl rounded-bl-sm transition-all';

  return (
    <div className={bubbleContainerClasses}>
      {!isUser && (
        <div className={avatarClasses}>
          <Bot className="w-5 h-5" />
        </div>
      )}

      <div className={messageClasses}>
        <div className="leading-relaxed text-[15px] font-medium [word-break:break-word]">
          {isUser ? (
            <span className="whitespace-pre-wrap">{message.content}</span>
          ) : (
            <ReactMarkdown
              remarkPlugins={[remarkGfm, remarkMath]}
              rehypePlugins={[rehypeKatex]}
              components={{
                p: ({node, ...props}: any) => <p className="mb-3 last:mb-0" {...props} />,
                ul: ({node, ...props}: any) => <ul className="list-disc pl-5 mb-3" {...props} />,
                ol: ({node, ...props}: any) => <ol className="list-decimal pl-5 mb-3" {...props} />,
                li: ({node, ...props}: any) => <li className="mb-1" {...props} />,
                h1: ({node, ...props}: any) => <h1 className="text-xl font-bold mb-3 mt-4" {...props} />,
                h2: ({node, ...props}: any) => <h2 className="text-lg font-bold mb-2 mt-4" {...props} />,
                h3: ({node, ...props}: any) => <h3 className="text-base font-bold mb-2 mt-3" {...props} />,
                a: ({node, ...props}: any) => <a className="text-blue-600 dark:text-blue-400 hover:underline" target="_blank" rel="noreferrer" {...props} />,
                code: ({node, className, children, ...props}: any) => {
                  const isInline = !className;
                  return isInline 
                    ? <code className="bg-zinc-100 dark:bg-zinc-700 px-1.5 py-0.5 rounded text-sm text-pink-600 dark:text-pink-400 font-mono" {...props}>{children}</code>
                    : <pre className="bg-zinc-900 border border-zinc-200 dark:border-zinc-700 p-3 rounded-lg overflow-x-auto mb-3 mt-2"><code className="text-zinc-100 text-sm font-mono" {...props}>{children}</code></pre>;
                },
                blockquote: ({node, ...props}: any) => <blockquote className="border-l-4 border-zinc-300 dark:border-zinc-600 pl-4 py-1 italic mb-3 text-zinc-600 dark:text-zinc-400 bg-zinc-50 dark:bg-zinc-800/50" {...props} />,
                table: ({node, ...props}: any) => <div className="overflow-x-auto mb-3"><table className="w-full text-sm text-left" {...props} /></div>,
                th: ({node, ...props}: any) => <th className="px-3 py-2 bg-zinc-100 dark:bg-zinc-800 border dark:border-zinc-700 font-semibold" {...props} />,
                td: ({node, ...props}: any) => <td className="px-3 py-2 border dark:border-zinc-700" {...props} />
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}
        </div>
        
        {message.toolCalls && message.toolCalls.length > 0 && (
          <ToolCallTrace toolCalls={message.toolCalls} />
        )}
        
        <div className={`text-[10px] mt-2 text-right ${isUser ? 'text-blue-200' : 'text-zinc-400'}`}>
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>

      {isUser && (
        <div className={avatarClasses}>
          <User className="w-5 h-5" />
        </div>
      )}
    </div>
  );
};
