import apiClient from './client';

export type ExportFormat = 'word' | 'pdf';

export interface ExportDocumentRequest {
  document_id: number;
  format: ExportFormat;
}

export interface ExportCustomRequest {
  title: string;
  content: string;
  format: ExportFormat;
}

export const exportApi = {
  exportDocument: async (documentId: number, format: ExportFormat = 'word') => {
    const response = await apiClient.get(`/export/document/${documentId}`, {
      params: { format },
      responseType: 'blob',
    });

    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response as any]));
    const link = document.createElement('a');
    link.href = url;

    const extension = format === 'word' ? 'docx' : 'pdf';
    link.setAttribute('download', `document_${documentId}.${extension}`);

    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  exportCustom: async (title: string, content: string, format: ExportFormat = 'word') => {
    const response = await apiClient.post(
      '/export/custom',
      { title, content, format },
      { responseType: 'blob' }
    );

    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response as any]));
    const link = document.createElement('a');
    link.href = url;

    const extension = format === 'word' ? 'docx' : 'pdf';
    link.setAttribute('download', `${title}.${extension}`);

    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};
