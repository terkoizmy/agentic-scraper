import { Bot, User } from 'lucide-react';
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
        <div className="whitespace-pre-wrap leading-relaxed text-[15px] font-medium">
          {message.content}
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
