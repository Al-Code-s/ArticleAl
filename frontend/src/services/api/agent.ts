import apiClient from './client';

export const agentApi = {
  // 启动智能体
  startAgent: (projectId: string) =>
    apiClient.post(`/agents/${projectId}/start`),

  // 停止智能体
  stopAgent: (projectId: string) =>
    apiClient.post(`/agents/${projectId}/stop`),
};
