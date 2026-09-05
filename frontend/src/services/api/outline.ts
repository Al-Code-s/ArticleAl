import apiClient from './client';

export interface OutlineSection {
  level: number;
  title: string;
  content: string;
  order: number;
  subsections?: OutlineSection[];
}

export interface Outline {
  id: number;
  user_id: number;
  project_id: number;
  title: string;
  content: {
    title: string;
    sections: OutlineSection[];
  };
  version: number;
  created_at: string;
  updated_at: string;
}

export interface GenerateOutlineRequest {
  project_id: number;
  topic_title: string;
  requirements?: string;
}

export interface UpdateOutlineRequest {
  title?: string;
  content?: {
    title: string;
    sections: OutlineSection[];
  };
}

export interface OutlineListResponse {
  items: Outline[];
  total: number;
  page: number;
  page_size: number;
}

export const outlineApi = {
  generate: (data: GenerateOutlineRequest) =>
    apiClient.post<Outline>('/outlines/generate', data),

  list: (params: { project_id?: number; page?: number; page_size?: number }) =>
    apiClient.get<OutlineListResponse>('/outlines', { params }),

  get: (id: number) => apiClient.get<Outline>(`/outlines/${id}`),

  update: (id: number, data: UpdateOutlineRequest) =>
    apiClient.put<Outline>(`/outlines/${id}`, data),

  delete: (id: number) => apiClient.delete(`/outlines/${id}`),
};
