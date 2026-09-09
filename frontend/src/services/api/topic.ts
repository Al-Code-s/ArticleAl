import apiClient from './client';
import type { Topic, GenerateTopicDto } from '../../types/topic';

export const topicApi = {
  // 生成题目
  generateTopics: (data: GenerateTopicDto) =>
    apiClient.post<Topic[]>('/topics/generate', data),

  // 获取我的题目列表
  getTopics: (projectId?: number) =>
    apiClient.get<{ items: Topic[]; total: number }>('/topics', { params: { project_id: projectId } }),
};
