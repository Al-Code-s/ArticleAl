import React, { useState, useEffect, useRef } from 'react';
import { useChatStore } from '../../stores/chatStore';

interface ChatPanelProps {
  projectId?: number;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ projectId }) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { messages, isConnected, isLoading, connect, disconnect, sendMessage } = useChatStore();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      connect(token, projectId);
    }

    return () => {
      disconnect();
    };
  }, [projectId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    try {
      await sendMessage(input);
      setInput('');
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-panel" style={{
      display: 'flex',
      flexDirection: 'column',
      height: '600px',
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      backgroundColor: '#fff'
    }}>
      {/* Header */}
      <div style={{
        padding: '16px',
        borderBottom: '1px solid #e5e7eb',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600 }}>AI 助手</h3>
        <div style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          backgroundColor: isConnected ? '#10b981' : '#ef4444'
        }} />
      </div>

      {/* Messages */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px'
      }}>
        {messages.length === 0 && (
          <div style={{
            textAlign: 'center',
            color: '#9ca3af',
            marginTop: '100px'
          }}>
            开始对话，我可以帮助你生成选题、大纲、文献综述等内容
          </div>
        )}

        {messages.map((msg, index) => (
          <div
            key={index}
            style={{
              alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '70%'
            }}
          >
            <div style={{
              padding: '12px 16px',
              borderRadius: '12px',
              backgroundColor: msg.role === 'user' ? '#3b82f6' : '#f3f4f6',
              color: msg.role === 'user' ? '#fff' : '#111827',
              wordWrap: 'break-word'
            }}>
              {msg.content}
            </div>
            <div style={{
              fontSize: '12px',
              color: '#9ca3af',
              marginTop: '4px',
              textAlign: msg.role === 'user' ? 'right' : 'left'
            }}>
              {new Date(msg.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}

        {isLoading && (
          <div style={{ alignSelf: 'flex-start' }}>
            <div style={{
              padding: '12px 16px',
              borderRadius: '12px',
              backgroundColor: '#f3f4f6',
              color: '#9ca3af'
            }}>
              正在思考...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={{
        padding: '16px',
        borderTop: '1px solid #e5e7eb',
        display: 'flex',
        gap: '8px'
      }}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="输入消息..."
          disabled={!isConnected || isLoading}
          style={{
            flex: 1,
            padding: '12px',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            fontSize: '14px',
            resize: 'none',
            minHeight: '48px',
            maxHeight: '120px',
            fontFamily: 'inherit'
          }}
        />
        <button
          onClick={handleSend}
          disabled={!isConnected || isLoading || !input.trim()}
          style={{
            padding: '12px 24px',
            backgroundColor: isConnected && !isLoading && input.trim() ? '#3b82f6' : '#d1d5db',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: 500,
            cursor: isConnected && !isLoading && input.trim() ? 'pointer' : 'not-allowed'
          }}
        >
          发送
        </button>
      </div>
    </div>
  );
};
