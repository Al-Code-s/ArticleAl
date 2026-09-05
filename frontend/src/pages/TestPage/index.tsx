import React, { useState } from 'react';
import { ChatPanel } from '../../components/ChatPanel';
import { ExportButton } from '../../components/ExportButton';
import { topicApi, outlineApi, referenceApi, documentApi } from '../../services/api';

export const TestPage: React.FC = () => {
  const [projectId, setProjectId] = useState<number>(1);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>({});

  const handleGenerateTopics = async () => {
    setLoading(true);
    try {
      const topics = await topicApi.generateTopics({
        project_id: projectId,
        major: '计算机科学',
        education_level: '本科',
        paper_type: '毕业论文',
        keywords: ['人工智能', '机器学习'],
        count: 3
      });
      setResults({ ...results, topics });
      alert(`成功生成 ${topics.length} 个选题`);
    } catch (error) {
      alert('生成失败: ' + error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateOutline = async () => {
    setLoading(true);
    try {
      const outline = await outlineApi.generateOutline({
        project_id: projectId,
        topic_title: '基于深度学习的图像识别研究',
        requirements: '需要包含实验部分'
      });
      setResults({ ...results, outline });
      alert('大纲生成成功');
    } catch (error) {
      alert('生成失败: ' + error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchReferences = async () => {
    setLoading(true);
    try {
      const references = await referenceApi.searchReferences({
        keyword: '深度学习',
        project_id: projectId,
        max_results: 10,
        save_to_project: true
      });
      setResults({ ...results, references });
      alert(`找到 ${references.length} 篇参考文献`);
    } catch (error) {
      alert('搜索失败: ' + error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateDocument = async () => {
    setLoading(true);
    try {
      const document = await documentApi.generateDocument({
        project_id: projectId,
        document_type: 'proposal',
        requirements: '需要详细的研究方法说明'
      });
      setResults({ ...results, document });
      alert('文档生成成功');
    } catch (error) {
      alert('生成失败: ' + error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '28px', fontWeight: 600, marginBottom: '24px' }}>
        ArticleAI 功能测试
      </h1>

      {/* Project ID Input */}
      <div style={{ marginBottom: '32px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
          项目 ID:
        </label>
        <input
          type="number"
          value={projectId}
          onChange={(e) => setProjectId(Number(e.target.value))}
          style={{
            padding: '8px 12px',
            border: '1px solid #e5e7eb',
            borderRadius: '6px',
            fontSize: '14px',
            width: '200px'
          }}
        />
      </div>

      {/* Action Buttons */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '16px',
        marginBottom: '32px'
      }}>
        <button
          onClick={handleGenerateTopics}
          disabled={loading}
          style={{
            padding: '16px',
            backgroundColor: '#3b82f6',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: 500,
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.5 : 1
          }}
        >
          🎯 生成选题
        </button>

        <button
          onClick={handleGenerateOutline}
          disabled={loading}
          style={{
            padding: '16px',
            backgroundColor: '#10b981',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: 500,
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.5 : 1
          }}
        >
          📝 生成大纲
        </button>

        <button
          onClick={handleSearchReferences}
          disabled={loading}
          style={{
            padding: '16px',
            backgroundColor: '#f59e0b',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: 500,
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.5 : 1
          }}
        >
          📚 搜索文献
        </button>

        <button
          onClick={handleGenerateDocument}
          disabled={loading}
          style={{
            padding: '16px',
            backgroundColor: '#8b5cf6',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: 500,
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.5 : 1
          }}
        >
          📄 生成文档
        </button>
      </div>

      {/* Results Display */}
      {Object.keys(results).length > 0 && (
        <div style={{
          marginBottom: '32px',
          padding: '16px',
          backgroundColor: '#f9fafb',
          borderRadius: '8px',
          border: '1px solid #e5e7eb'
        }}>
          <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>
            生成结果
          </h2>

          {results.topics && (
            <div style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 500, marginBottom: '8px' }}>
                选题 ({results.topics.length}):
              </h3>
              {results.topics.map((topic: any, index: number) => (
                <div key={index} style={{
                  padding: '12px',
                  backgroundColor: '#fff',
                  borderRadius: '6px',
                  marginBottom: '8px'
                }}>
                  <div style={{ fontWeight: 500 }}>{topic.title}</div>
                  <div style={{ fontSize: '14px', color: '#6b7280', marginTop: '4px' }}>
                    {topic.description}
                  </div>
                </div>
              ))}
            </div>
          )}

          {results.outline && (
            <div style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 500, marginBottom: '8px' }}>
                大纲: {results.outline.title}
              </h3>
              <div style={{
                padding: '12px',
                backgroundColor: '#fff',
                borderRadius: '6px'
              }}>
                版本: {results.outline.version} |
                章节数: {results.outline.content?.sections?.length || 0}
              </div>
            </div>
          )}

          {results.references && (
            <div style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 500, marginBottom: '8px' }}>
                参考文献 ({results.references.length}):
              </h3>
              {results.references.slice(0, 3).map((ref: any, index: number) => (
                <div key={index} style={{
                  padding: '12px',
                  backgroundColor: '#fff',
                  borderRadius: '6px',
                  marginBottom: '8px'
                }}>
                  <div style={{ fontWeight: 500 }}>{ref.title}</div>
                  <div style={{ fontSize: '14px', color: '#6b7280', marginTop: '4px' }}>
                    {ref.authors?.join(', ')} - {ref.publication} ({ref.year})
                  </div>
                </div>
              ))}
            </div>
          )}

          {results.document && (
            <div style={{ marginBottom: '16px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 500, marginBottom: '8px' }}>
                文档: {results.document.title}
              </h3>
              <div style={{
                padding: '12px',
                backgroundColor: '#fff',
                borderRadius: '6px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div>
                  类型: {results.document.type} |
                  字数: {results.document.word_count} |
                  状态: {results.document.status}
                </div>
                <ExportButton
                  documentId={results.document.id}
                  documentTitle={results.document.title}
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Chat Panel */}
      <div>
        <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>
          AI 智能助手（WebSocket 实时对话）
        </h2>
        <ChatPanel projectId={projectId} />
      </div>
    </div>
  );
};
