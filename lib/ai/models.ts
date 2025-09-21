export const DEFAULT_CHAT_MODEL: string = 'chat-model';

export interface ChatModel {
  id: string;
  name: string;
  description: string;
}

export const chatModels: Array<ChatModel> = [
  {
    id: 'chat-model',
    name: 'LegalLens AI',
    description: 'Specialized local AI model for legal document analysis and chat',
  },
  {
    id: 'chat-model-reasoning',
    name: 'LegalLens Reasoning',
    description: 'Advanced local AI with enhanced reasoning for complex legal matters',
  },
];
