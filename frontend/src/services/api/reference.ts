import apiClient from './client';

export interface Reference {
  id: number;
  user_id: number;
  project_id?: number;
  title: string;
  authors: string[];
  publication: string;
  year: number;
  volume?: string;
  issue?: string;
  pages?: string;
  doi?: string;
  url?: string;
  abstract?: string;
  keywords: string[];
  citation_format: string;
  created_at: string;
  updated_at: string;
}

export interface SearchReferenceRequest {
  keyword: string;
  project_id?: number;
  max_results?: number;
  auto_save?: boolean;
}

export interface UpdateReferenceRequest {
  title?: string;
  authors?: string[];
  publication?: string;
  year?: number;
  volume?: string;
  issue?: string;
  pages?: string;
  doi?: string;
  url?: string;
  abstract?: string;
  keywords?: string[];
  citation_format?: string;
}

export interface ReferenceListResponse {
  items: Reference[];
  total: number;
  page: number;
  page_size: number;
}

export const referenceApi = {
  search: (data: SearchReferenceRequest) =>
    apiClient.post<Reference[]>('/references/search', data),

  list: (params: { project_id?: number; page?: number; page_size?: number }) =>
    apiClient.get<ReferenceListResponse>('/references', { params }),

  get: (id: number) => apiClient.get<Reference>(`/references/${id}`),

  update: (id: number, data: UpdateReferenceRequest) =>
    apiClient.put<Reference>(`/references/${id}`, data),

  delete: (id: number) => apiClient.delete(`/references/${id}`),
};
