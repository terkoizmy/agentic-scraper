export const RoleType = {
  USER: 'user',
  AGENT: 'agent',
} as const;

export type RoleType = typeof RoleType[keyof typeof RoleType];

export interface ToolCall {
  tool: string;
  args: Record<string, unknown>;
  result: Record<string, unknown>;
}

export interface ChatMessage {
  id: string;
  role: RoleType;
  content: string;
  toolCalls?: ToolCall[];
  timestamp: string;
}

export interface AgentAskRequest {
  message: string;
  session_id?: string;
}

export interface AgentAskResponse {
  answer: string;
  session_id: string;
  tool_calls: ToolCall[];
}
