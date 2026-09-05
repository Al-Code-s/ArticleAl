import apiClient from './client';
import type { Topic, GenerateTopicDto } from '@types/topic';

export const topicApi = {
  // 生成题目
  generateTopics: (data: GenerateTopicDto) =>
    apiClient.post<{ data: { topics: Topic[] } }>('/topics/generate', data),

  // 从题目创建项目
  createProjectFromTopic: (topicId: string, wordCount?: number) =>
    apiClient.post('/topics/create-project', { topicId, wordCount }),

  // 获取我的题目列表
  getTopics: (unused?: boolean) =>
    apiClient.get<{ data: { topics: Topic[] } }>('/topics', { params: { unused } }),
};
