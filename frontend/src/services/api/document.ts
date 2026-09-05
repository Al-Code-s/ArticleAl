import apiClient from './client';

export type DocumentType = 'assignment' | 'proposal' | 'literature_review' | 'thesis';
export type DocumentStatus = 'draft' | 'completed' | 'reviewed';

export interface Document {
  id: number;
  user_id: number;
  project_id: number;
  type: DocumentType;
  title: string;
  content: string;
  status: DocumentStatus;
  word_count: number;
  created_at: string;
  updated_at: string;
}

export interface GenerateDocumentRequest {
  project_id: number;
  document_type: DocumentType;
  topic_title?: string;
  outline_id?: number;
  requirements?: string;
}

export interface UpdateDocumentRequest {
  title?: string;
  content?: string;
  status?: DocumentStatus;
}

export interface DocumentListResponse {
  items: Document[];
  total: number;
  page: number;
  page_size: number;
}

export const documentApi = {
  generate: (data: GenerateDocumentRequest) =>
    apiClient.post<Document>('/documents/generate', data),

  list: (params: {
    project_id?: number;
    document_type?: DocumentType;
    page?: number;
    page_size?: number;
  }) => apiClient.get<DocumentListResponse>('/documents', { params }),

  get: (id: number) => apiClient.get<Document>(`/documents/${id}`),

  update: (id: number, data: UpdateDocumentRequest) =>
    apiClient.put<Document>(`/documents/${id}`, data),

  delete: (id: number) => apiClient.delete(`/documents/${id}`),
};
