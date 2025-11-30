export interface SourceChunk {
  id: string;
  bookTitle: string;
  chapter?: string | number;
  verse?: string | number;
  pageNumber?: number; // Keep for backward compatibility
  content: string;
  score: number;
}

export interface AgentStep {
  type: 'thought' | 'action' | 'observation';
  content: string;
}

export interface Message {
  id?: string;
  role: 'user' | 'model';
  parts: { text: string }[];
  timestamp?: number;
  relatedChunkIds?: string[];
  isThinking?: boolean;
  agentSteps?: AgentStep[];
}

export interface Conversation {
  id: string;
  title: string;
  createdAt: string;
  messages: Message[];
}

export interface ConversationHeader {
  id: string;
  title: string;
  createdAt: string;
}

export interface AppSettings {
  apiKey: string;
  backendUrl: string;
  useMockData: boolean;
  model: string;
  language: string;
}

export type CitationClickHandler = (chunkId: string) => void;
