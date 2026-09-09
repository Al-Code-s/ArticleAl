import { create } from 'zustand';
import type { AgentMessage, AgentStatus } from '../types/agent';

interface AgentState {
  messages: Record<string, AgentMessage[]>; // projectId -> messages
  statuses: Record<string, AgentStatus>; // projectId -> status

  addMessage: (projectId: string, message: AgentMessage) => void;
  setMessages: (projectId: string, messages: AgentMessage[]) => void;
  clearMessages: (projectId: string) => void;

  setStatus: (projectId: string, status: AgentStatus) => void;
  getStatus: (projectId: string) => AgentStatus | null;
}

export const useAgentStore = create<AgentState>((set, get) => ({
  messages: {},
  statuses: {},

  addMessage: (projectId, message) =>
    set((state) => ({
      messages: {
        ...state.messages,
        [projectId]: [...(state.messages[projectId] || []), message],
      },
    })),

  setMessages: (projectId, messages) =>
    set((state) => ({
      messages: {
        ...state.messages,
        [projectId]: messages,
      },
    })),

  clearMessages: (projectId) =>
    set((state) => {
      const newMessages = { ...state.messages };
      delete newMessages[projectId];
      return { messages: newMessages };
    }),

  setStatus: (projectId, status) =>
    set((state) => ({
      statuses: {
        ...state.statuses,
        [projectId]: status,
      },
    })),

  getStatus: (projectId) => {
    return get().statuses[projectId] || null;
  },
}));
