import {
  customProvider,
  extractReasoningMiddleware,
  wrapLanguageModel,
  LanguageModel,
} from 'ai';
import { isTestEnvironment } from '../constants';
import { localAIProvider } from './local-provider';

// Custom language model that uses our local AI server
const createLocalLanguageModel = (modelId: string): LanguageModel => {
  const model = {
    specificationVersion: 'v2',
    provider: 'local-ai',
    modelId,
    defaultObjectGenerationMode: 'tool',
    supportedUrls: {},
    supportsImageUrls: true,
    supportsStructuredOutputs: false,
    
    doGenerate: async (options: any) => {
      const { prompt, messages } = options;
      
      try {
        // Debug logging
        console.log('doGenerate called with options:', { prompt: prompt ? 'present' : 'not present', messagesCount: messages?.length || 0 });
        
        let messagesToSend = messages || [];
        
        // If we have a prompt but no messages, convert prompt to message format
        if (prompt && (!messages || messages.length === 0)) {
          messagesToSend = [{ role: 'user', content: prompt }];
          console.log('Converted prompt to messages format');
        }
        
        // Convert AI SDK format to our local AI format
        const response = await localAIProvider.chatCompletion(messagesToSend, options);
        
        return {
          rawCall: { rawPrompt: null, rawSettings: {} },
          finishReason: 'stop',
          usage: {
            inputTokens: response.usage?.prompt_tokens || 0,
            outputTokens: response.usage?.completion_tokens || 0,
            totalTokens: response.usage?.total_tokens || 0,
          },
          content: [{ type: 'text', text: response.choices[0].message.content }],
          warnings: [],
        };
      } catch (error) {
        console.error('Local AI generation error:', error);
        throw error;
      }
    },

    doStream: async (options: any) => {
      try {
        const { prompt, messages } = options;
        
        let messagesToSend = messages || [];
        
        // If we have a prompt but no messages, convert prompt to message format
        if (prompt && (!messages || messages.length === 0)) {
          messagesToSend = [{ role: 'user', content: prompt }];
        }
        
        // Get the response directly from local AI
        const response = await localAIProvider.chatCompletion(messagesToSend, options);
        const content = response.choices[0].message.content;
        
        return {
          stream: new ReadableStream({
            start(controller) {
              // Send the complete response as a single chunk
              controller.enqueue({
                type: 'text-delta',
                textDelta: content,
              });
              
              // Send finish event
              controller.enqueue({
                type: 'finish',
                finishReason: 'stop',
                usage: {
                  inputTokens: response.usage?.prompt_tokens || 0,
                  outputTokens: response.usage?.completion_tokens || 0,
                  totalTokens: response.usage?.total_tokens || 0,
                },
              });
              
              // Close the stream
              controller.close();
            },
          }),
          rawCall: { rawPrompt: null, rawSettings: {} },
        };
      } catch (error) {
        console.error('Local AI streaming error:', error);
        // Return an error stream
        return {
          stream: new ReadableStream({
            start(controller) {
              controller.enqueue({
                type: 'error',
                error: error instanceof Error ? error.message : 'Unknown error occurred',
              });
              controller.close();
            },
          }),
          rawCall: { rawPrompt: null, rawSettings: {} },
        };
      }
    },
  };
  
  return model as unknown as LanguageModel;
};

export const myProvider = isTestEnvironment
  ? (() => {
      const {
        artifactModel,
        chatModel,
        reasoningModel,
        titleModel,
      } = require('./models.mock');
      return customProvider({
        languageModels: {
          'chat-model': chatModel,
          'chat-model-reasoning': reasoningModel,
          'title-model': titleModel,
          'artifact-model': artifactModel,
        },
      });
    })()
  : customProvider({
      languageModels: {
        'chat-model': createLocalLanguageModel('legal-chat') as any,
        'chat-model-reasoning': createLocalLanguageModel('legal-chat-reasoning') as any,
        'title-model': createLocalLanguageModel('legal-title') as any,
        'artifact-model': createLocalLanguageModel('legal-artifact') as any,
      },
    });
