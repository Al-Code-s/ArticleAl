import apiClient from './client';
import type { Project, CreateProjectDto, UpdateProjectDto } from '../../types/project';

export const projectApi = {
  // 获取项目列表
  getProjects: (params?: { status?: string; page?: number; page_size?: number }) =>
    apiClient.get<{ items: Project[]; total: number; page: number; page_size: number }>('/projects', { params }),

  // 获取项目详情
  getProject: (id: string) =>
    apiClient.get<Project>(`/projects/${id}`),

  // 创建项目
  createProject: (data: CreateProjectDto) =>
    apiClient.post<Project>('/projects', data),

  // 更新项目
  updateProject: (id: string, data: UpdateProjectDto) =>
    apiClient.put<Project>(`/projects/${id}`, data),

  // 删除项目
  deleteProject: (id: string) =>
    apiClient.delete(`/projects/${id}`),

  // 获取大纲
  getOutline: (projectId: string) =>
    apiClient.get(`/outlines`, { params: { project_id: projectId, page: 1, page_size: 1 } }),

  // 生成大纲
  generateOutline: (projectId: string, title: string, style: 'liberal' | 'science') =>
    apiClient.post(`/outlines/generate`, { project_id: parseInt(projectId), topic_title: title, requirements: style }),

  // 更新大纲
  updateOutline: (outlineId: string, content: any) =>
    apiClient.put(`/outlines/${outlineId}`, { content }),

  // 获取参考文献
  getReferences: (projectId: string) =>
    apiClient.get(`/references`, { params: { project_id: projectId } }),

  // 搜索参考文献
  searchReferences: (keywords: string[], limit?: number) =>
    apiClient.post(`/references/search`, { keywords, limit: limit || 20 }),

  // 选择参考文献
  selectReference: (referenceId: string) =>
    apiClient.put(`/references/${referenceId}`, { is_selected: true }),

  // 删除参考文献
  deleteReference: (referenceId: string) =>
    apiClient.delete(`/references/${referenceId}`),
};
