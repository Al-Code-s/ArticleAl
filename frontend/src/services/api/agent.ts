import apiClient from './client';
import type { AgentSession } from '@types/agent';

export const agentApi = {
  // 启动智能体
  startAgent: (projectId: string, aiConfigId?: string) =>
    apiClient.post<{ data: { session: AgentSession } }>(
      `/projects/${projectId}/agent/start`,
      { aiConfigId },
    ),

  // 停止智能体
  stopAgent: (projectId: string) =>
    apiClient.post<{ data: { success: boolean } }>(`/projects/${projectId}/agent/stop`),

  // 重启智能体
  restartAgent: (projectId: string, aiConfigId?: string) =>
    apiClient.post<{ data: { session: AgentSession } }>(
      `/projects/${projectId}/agent/restart`,
      { aiConfigId },
    ),

  // 获取智能体状态
  getAgentStatus: (projectId: string) =>
    apiClient.get(`/projects/${projectId}/agent/status`),

  // 获取对话历史
  getAgentHistory: (projectId: string, limit?: number, offset?: number) =>
    apiClient.get(`/projects/${projectId}/agent/history`, { params: { limit, offset } }),
};
