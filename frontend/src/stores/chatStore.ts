import { create } from 'zustand';
import { chatWebSocket, ChatMessage, ChatResponse } from '../services/websocket/chatSocket';

interface ChatState {
  messages: ChatMessage[];
  isConnected: boolean;
  isLoading: boolean;
  currentProjectId?: number;

  connect: (token: string, projectId?: number) => void;
  disconnect: () => void;
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isConnected: false,
  isLoading: false,
  currentProjectId: undefined,

  connect: (token: string, projectId?: number) => {
    chatWebSocket.connect(token, projectId);

    chatWebSocket.onMessage((response: ChatResponse) => {
      const { messages } = get();

      if (response.type === 'message' && response.content) {
        const newMessage: ChatMessage = {
          role: 'assistant',
          content: response.content,
          timestamp: new Date().toISOString(),
        };

        set({ messages: [...messages, newMessage], isLoading: false });
      } else if (response.type === 'error') {
        console.error('Chat error:', response.error);
        set({ isLoading: false });
      } else if (response.type === 'done') {
        set({ isLoading: false });
      }
    });

    set({ isConnected: true, currentProjectId: projectId });
  },

  disconnect: () => {
    chatWebSocket.disconnect();
    set({ isConnected: false, currentProjectId: undefined });
  },

  sendMessage: async (content: string) => {
    const { messages } = get();

    const userMessage: ChatMessage = {
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };

    set({ messages: [...messages, userMessage], isLoading: true });

    try {
      chatWebSocket.sendMessage(content, get().currentProjectId);
    } catch (error) {
      console.error('Failed to send message:', error);
      set({ isLoading: false });
      throw error;
    }
  },

  clearMessages: () => {
    set({ messages: [] });
  },
}));
