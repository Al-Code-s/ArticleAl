export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  type: 'message' | 'error' | 'done';
  content?: string;
  error?: string;
}

class ChatWebSocket {
  private ws: WebSocket | null = null;
  private messageHandlers: ((message: ChatResponse) => void)[] = [];
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  connect(token: string, projectId?: number) {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:3000';
    let url = `${wsUrl}/api/chat/ws?token=${token}`;

    if (projectId) {
      url += `&project_id=${projectId}`;
    }

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const data: ChatResponse = JSON.parse(event.data);
        this.messageHandlers.forEach((handler) => handler(data));
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.attemptReconnect(token, projectId);
    };
  }

  private attemptReconnect(token: string, projectId?: number) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

      setTimeout(() => {
        this.connect(token, projectId);
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  sendMessage(message: string, projectId?: number) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      // Backend expects the same envelope used by its WebSocket protocol.
      this.ws.send(JSON.stringify({ type: 'message', content: message, project_id: projectId, context: {} }));
    } else {
      console.error('WebSocket is not connected');
      throw new Error('WebSocket is not connected');
    }
  }

  onMessage(handler: (message: ChatResponse) => void) {
    this.messageHandlers.push(handler);
    return () => {
      this.messageHandlers = this.messageHandlers.filter((h) => h !== handler);
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.messageHandlers = [];
    this.reconnectAttempts = 0;
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

export const chatWebSocket = new ChatWebSocket();
