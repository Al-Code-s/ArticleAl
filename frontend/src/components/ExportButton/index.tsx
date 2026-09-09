import React, { useState } from 'react';
import { exportApi, ExportFormat } from '../../services/api/export';

interface ExportButtonProps {
  documentId: number;
  documentTitle?: string;
}

export const ExportButton: React.FC<ExportButtonProps> = ({ documentId }) => {
  const [isExporting, setIsExporting] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  const handleExport = async (format: ExportFormat) => {
    setIsExporting(true);
    setShowMenu(false);

    try {
      await exportApi.exportDocument(documentId, format);
      alert(`导出成功！文件已下载为 ${format.toUpperCase()} 格式`);
    } catch (error) {
      console.error('Export failed:', error);
      alert('导出失败，请稍后重试');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      <button
        onClick={() => setShowMenu(!showMenu)}
        disabled={isExporting}
        style={{
          padding: '8px 16px',
          backgroundColor: '#3b82f6',
          color: '#fff',
          border: 'none',
          borderRadius: '6px',
          fontSize: '14px',
          fontWeight: 500,
          cursor: isExporting ? 'not-allowed' : 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}
      >
        {isExporting ? '导出中...' : '导出文档'}
        {!isExporting && <span style={{ fontSize: '12px' }}>▼</span>}
      </button>

      {showMenu && !isExporting && (
        <div style={{
          position: 'absolute',
          top: '100%',
          right: 0,
          marginTop: '4px',
          backgroundColor: '#fff',
          border: '1px solid #e5e7eb',
          borderRadius: '6px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
          zIndex: 10,
          minWidth: '150px'
        }}>
          <button
            onClick={() => handleExport('word')}
            style={{
              width: '100%',
              padding: '12px 16px',
              textAlign: 'left',
              border: 'none',
              backgroundColor: 'transparent',
              cursor: 'pointer',
              fontSize: '14px',
              borderBottom: '1px solid #e5e7eb'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f3f4f6'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            导出为 Word (.docx)
          </button>

          <button
            onClick={() => handleExport('pdf')}
            style={{
              width: '100%',
              padding: '12px 16px',
              textAlign: 'left',
              border: 'none',
              backgroundColor: 'transparent',
              cursor: 'pointer',
              fontSize: '14px'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f3f4f6'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            导出为 PDF
          </button>
        </div>
      )}
    </div>
  );
};

interface ExportCustomButtonProps {
  title: string;
  content: string;
}

export const ExportCustomButton: React.FC<ExportCustomButtonProps> = ({ title, content }) => {
  const [isExporting, setIsExporting] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  const handleExport = async (format: ExportFormat) => {
    if (!title.trim() || !content.trim()) {
      alert('标题和内容不能为空');
      return;
    }

    setIsExporting(true);
    setShowMenu(false);

    try {
      await exportApi.exportCustom(title, content, format);
      alert(`导出成功！文件已下载为 ${format.toUpperCase()} 格式`);
    } catch (error) {
      console.error('Export failed:', error);
      alert('导出失败，请稍后重试');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      <button
        onClick={() => setShowMenu(!showMenu)}
        disabled={isExporting}
        style={{
          padding: '8px 16px',
          backgroundColor: '#10b981',
          color: '#fff',
          border: 'none',
          borderRadius: '6px',
          fontSize: '14px',
          fontWeight: 500,
          cursor: isExporting ? 'not-allowed' : 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}
      >
        {isExporting ? '导出中...' : '导出'}
        {!isExporting && <span style={{ fontSize: '12px' }}>▼</span>}
      </button>

      {showMenu && !isExporting && (
        <div style={{
          position: 'absolute',
          top: '100%',
          right: 0,
          marginTop: '4px',
          backgroundColor: '#fff',
          border: '1px solid #e5e7eb',
          borderRadius: '6px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
          zIndex: 10,
          minWidth: '150px'
        }}>
          <button
            onClick={() => handleExport('word')}
            style={{
              width: '100%',
              padding: '12px 16px',
              textAlign: 'left',
              border: 'none',
              backgroundColor: 'transparent',
              cursor: 'pointer',
              fontSize: '14px',
              borderBottom: '1px solid #e5e7eb'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f3f4f6'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            导出为 Word (.docx)
          </button>

          <button
            onClick={() => handleExport('pdf')}
            style={{
              width: '100%',
              padding: '12px 16px',
              textAlign: 'left',
              border: 'none',
              backgroundColor: 'transparent',
              cursor: 'pointer',
              fontSize: '14px'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f3f4f6'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
          >
            导出为 PDF
          </button>
        </div>
      )}
    </div>
  );
};
