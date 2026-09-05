import apiClient from './client';
import type { Project, CreateProjectDto, UpdateProjectDto } from '@types/project';

export const projectApi = {
  // 获取项目列表
  getProjects: (params?: { status?: string; page?: number; limit?: number }) =>
    apiClient.get<{ data: { projects: Project[]; total: number } }>('/projects', { params }),

  // 获取项目详情
  getProject: (id: string) =>
    apiClient.get<{ data: { project: Project } }>(`/projects/${id}`),

  // 创建项目
  createProject: (data: CreateProjectDto) =>
    apiClient.post<{ data: { project: Project } }>('/projects', data),

  // 更新项目
  updateProject: (id: string, data: UpdateProjectDto) =>
    apiClient.put<{ data: { project: Project } }>(`/projects/${id}`, data),

  // 删除项目
  deleteProject: (id: string) =>
    apiClient.delete<{ data: { success: boolean } }>(`/projects/${id}`),

  // 获取大纲
  getOutline: (projectId: string) =>
    apiClient.get(`/projects/${projectId}/outline`),

  // 生成大纲
  generateOutline: (projectId: string, method: 'ai' | 'agent') =>
    apiClient.post(`/projects/${projectId}/outline/generate`, { method }),

  // 更新大纲
  updateOutline: (projectId: string, content: any) =>
    apiClient.put(`/projects/${projectId}/outline`, { content }),

  // 获取参考文献
  getReferences: (projectId: string, selected?: boolean) =>
    apiClient.get(`/projects/${projectId}/references`, { params: { selected } }),

  // 搜索参考文献
  searchReferences: (projectId: string, keywords: string[], limit?: number) =>
    apiClient.post(`/projects/${projectId}/references/search`, { keywords, limit }),

  // 选择参考文献
  selectReferences: (projectId: string, referenceIds: string[]) =>
    apiClient.post(`/projects/${projectId}/references/select`, { referenceIds }),

  // 删除参考文献
  deleteReference: (projectId: string, referenceId: string) =>
    apiClient.delete(`/projects/${projectId}/references/${referenceId}`),
};
