export interface AgentSession {
  id: string;
  project_id: string;
  session_name?: string;
  status: 'active' | 'stopped' | 'error';
  ai_config_id?: string;
  context: Record<string, any>;
  total_tokens_used: number;
  message_count: number;
  created_at: string;
  ended_at?: string;
  error_message?: string;
}

export interface AgentMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  metadata: Record<string, any>;
  tokens_used: number;
  created_at: string;
}

export interface AgentStatus {
  status: 'idle' | 'running' | 'stopped' | 'error';
  sessionId?: string;
  messageCount: number;
}
