import { io, Socket } from 'socket.io-client';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:3000';

export class AgentSocketService {
  private socket: Socket | null = null;
  private projectId: string;

  constructor(projectId: string) {
    this.projectId = projectId;
  }

  connect() {
    const token = localStorage.getItem('token');

    this.socket = io(`${WS_URL}/ws/projects/${this.projectId}/agent`, {
      auth: {
        token,
      },
      transports: ['websocket'],
    });

    this.socket.on('connect', () => {
      console.log('Agent WebSocket connected');
    });

    this.socket.on('disconnect', () => {
      console.log('Agent WebSocket disconnected');
    });

    this.socket.on('error', (error) => {
      console.error('Agent WebSocket error:', error);
    });

    return this.socket;
  }

  sendMessage(content: string) {
    if (this.socket?.connected) {
      this.socket.emit('message', { type: 'message', content });
    } else {
      throw new Error('Socket not connected');
    }
  }

  onMessage(callback: (data: any) => void) {
    this.socket?.on('message', callback);
  }

  onStatus(callback: (data: any) => void) {
    this.socket?.on('status', callback);
  }

  onResult(callback: (data: any) => void) {
    this.socket?.on('result', callback);
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }
}

export const connectAgentSocket = (projectId: string) => {
  return new AgentSocketService(projectId);
};
