import {
  convertToModelMessages,
  createUIMessageStream,
  JsonToSseTransformStream,
  smoothStream,
  stepCountIs,
  streamText,
} from 'ai';
import { auth, type UserType } from '@/app/(auth)/auth';
import { type RequestHints, systemPrompt } from '@/lib/ai/prompts';
import {
  createStreamId,
  deleteChatById,
  getChatById,
  getMessageCountByUserId,
  getMessagesByChatId,
  saveChat,
  saveMessages,
} from '@/lib/db/queries';
import { updateChatLastContextById } from '@/lib/db/queries';
import { convertToUIMessages, generateUUID } from '@/lib/utils';
import { generateTitleFromUserMessage } from '../../actions';
import { createDocument } from '@/lib/ai/tools/create-document';
import { updateDocument } from '@/lib/ai/tools/update-document';
import { requestSuggestions } from '@/lib/ai/tools/request-suggestions';
import { getWeather } from '@/lib/ai/tools/get-weather';
import { readFile } from 'fs/promises';
import { join } from 'path';
import { isProductionEnvironment } from '@/lib/constants';
import { myProvider } from '@/lib/ai/providers';
import { localAIProvider } from '@/lib/ai/local-provider';
import { entitlementsByUserType } from '@/lib/ai/entitlements';
import { postRequestBodySchema, type PostRequestBody } from './schema';
import { geolocation } from '@vercel/functions';
import {
  createResumableStreamContext,
  type ResumableStreamContext,
} from 'resumable-stream';
import { after } from 'next/server';
import { ChatSDKError } from '@/lib/errors';
import type { ChatMessage } from '@/lib/types';
import type { ChatModel } from '@/lib/ai/models';
import type { VisibilityType } from '@/components/visibility-selector';
import { unstable_cache as cache } from 'next/cache';
import { fetchModels } from 'tokenlens/fetch';
import { getUsage } from 'tokenlens/helpers';
import type { ModelCatalog } from 'tokenlens/core';
import type { AppUsage } from '@/lib/usage';

export const maxDuration = 60;

let globalStreamContext: ResumableStreamContext | null = null;

// Helper function to convert file parts to base64 for Local AI processing
async function processFilePartsForAI(messages: any[]) {
  const processedMessages = [];
  
  for (const message of messages) {
    const processedMessage = { ...message };
    
    if (message.parts && Array.isArray(message.parts)) {
      const processedParts = [];
      
      for (const part of message.parts) {
        if (part.type === 'file' && part.url && part.url.startsWith('/uploads/')) {
          try {
            // Read the file from the public directory
            const filePath = join(process.cwd(), 'public', part.url);
            console.log(`Reading file from: ${filePath}`);
            const fileBuffer = await readFile(filePath);
            
            // For PDF files, extract text content and add it as context
            if (part.mediaType === 'application/pdf') {
              try {
                // Try to extract text from PDF using local AI server
                const fileBlob = new File([new Uint8Array(fileBuffer)], part.name, { type: 'application/pdf' });
                const analysis = await localAIProvider.uploadAndAnalyzePDF(fileBlob);
                
                // Add the analysis as a system message context
                processedParts.push({
                  type: 'text',
                  text: `[DOCUMENT ANALYSIS]\nDocument: ${part.name}\nAnalysis: ${analysis.analysis}`
                });
              } catch (pdfError) {
                console.error('PDF text extraction failed:', pdfError);
                // Fallback to base64 data if text extraction fails
                const base64Data = fileBuffer.toString('base64');
                processedParts.push({
                  type: 'file',
                  mediaType: part.mediaType,
                  data: base64Data
                });
              }
            } else if (part.mediaType === 'text/plain') {
              // For text files, include the content directly
              const textContent = fileBuffer.toString('utf-8');
              processedParts.push({
                type: 'text',
                text: `[DOCUMENT CONTENT]\nDocument: ${part.name}\nContent: ${textContent}`
              });
            } else {
              // For images and other files, use base64 data
              const base64Data = fileBuffer.toString('base64');
              processedParts.push({
                type: 'file',
                mediaType: part.mediaType,
                data: base64Data
              });
            }
          } catch (error) {
            console.error(`Failed to read file ${part.url}:`, error);
            // If we can't read the file, skip this part
            continue;
          }
        } else {
          // Keep non-file parts as is
          processedParts.push(part);
        }
      }
      
      processedMessage.parts = processedParts;
    }
    
    processedMessages.push(processedMessage);
  }
  
  return processedMessages;
}

const getTokenlensCatalog = cache(
  async (): Promise<ModelCatalog | undefined> => {
    try {
      return await fetchModels();
    } catch (err) {
      console.warn(
        'TokenLens: catalog fetch failed, using default catalog',
        err,
      );
      return undefined; // tokenlens helpers will fall back to defaultCatalog
    }
  },
  ['tokenlens-catalog'],
  { revalidate: 24 * 60 * 60 }, // 24 hours
);

export function getStreamContext() {
  if (!globalStreamContext) {
    try {
      // Check if Redis URL is properly configured
      if (!process.env.REDIS_URL || process.env.REDIS_URL === '****' || process.env.REDIS_URL.trim() === '') {
        console.log(' > Resumable streams are disabled - REDIS_URL not configured for development');
        return null;
      }
      
      globalStreamContext = createResumableStreamContext({
        waitUntil: after,
      });
    } catch (error: any) {
      if (error.message.includes('REDIS_URL') || error.message.includes('Invalid URL')) {
        console.log(
          ' > Resumable streams are disabled due to invalid REDIS_URL configuration',
        );
      } else {
        console.error('Stream context error:', error);
      }
      return null;
    }
  }

  return globalStreamContext;
}

export async function POST(request: Request) {
  let requestBody: PostRequestBody;

  try {
    const json = await request.json();
    console.log('Received request body:', JSON.stringify(json, null, 2));
    requestBody = postRequestBodySchema.parse(json);
    console.log('Request body validation passed');
  } catch (error) {
    console.error('Request validation failed:', error);
    console.error('Error details:', error instanceof Error ? error.message : 'Unknown validation error');
    return new ChatSDKError('bad_request:api').toResponse();
  }

  try {
    const {
      id,
      message,
      selectedChatModel,
      selectedVisibilityType,
    }: {
      id: string;
      message: ChatMessage;
      selectedChatModel: ChatModel['id'];
      selectedVisibilityType: VisibilityType;
    } = requestBody;

    const session = await auth();

    if (!session?.user) {
      return new ChatSDKError('unauthorized:chat').toResponse();
    }

    const userType: UserType = session.user.type;

    const messageCount = await getMessageCountByUserId({
      id: session.user.id,
      differenceInHours: 24,
    });

    if (messageCount > entitlementsByUserType[userType].maxMessagesPerDay) {
      return new ChatSDKError('rate_limit:chat').toResponse();
    }

    const chat = await getChatById({ id });

    if (!chat) {
      const title = await generateTitleFromUserMessage({
        message,
      });

      await saveChat({
        id,
        userId: session.user.id,
        title,
        visibility: selectedVisibilityType,
      });
    } else {
      if (chat.userId !== session.user.id) {
        return new ChatSDKError('forbidden:chat').toResponse();
      }
    }

    const messagesFromDb = await getMessagesByChatId({ id });
    const uiMessages = [...convertToUIMessages(messagesFromDb), message];

    const { longitude, latitude, city, country } = geolocation(request);

    const requestHints: RequestHints = {
      longitude,
      latitude,
      city,
      country,
    };

    await saveMessages({
      messages: [
        {
          chatId: id,
          id: message.id,
          role: 'user',
          parts: message.parts,
          attachments: [],
          createdAt: new Date(),
        },
      ],
    });

    const streamId = generateUUID();
    await createStreamId({ streamId, chatId: id });

    // Process file parts to base64 before sending to AI model
    const processedUIMessages = await processFilePartsForAI(uiMessages);
    console.log('Original UI Messages:', JSON.stringify(uiMessages, null, 2));
    console.log('Processed messages for AI:', JSON.stringify(processedUIMessages, null, 2));
    
    // Try to convert and see what happens
    try {
      const modelMessages = convertToModelMessages(processedUIMessages);
      console.log('Successfully converted to ModelMessages:', JSON.stringify(modelMessages, null, 2));
    } catch (conversionError) {
      console.error('convertToModelMessages failed:', conversionError);
      console.error('Processed messages structure:', JSON.stringify(processedUIMessages.map(m => ({
        role: m.role,
        parts: Array.isArray(m.parts) ? m.parts.map((p: any) => ({ type: p.type, hasData: !!p.data })) : 'no parts'
      })), null, 2));
      throw conversionError;
    }

    let finalMergedUsage: AppUsage | undefined;

    const stream = createUIMessageStream({
      execute: ({ writer: dataStream }) => {
        const result = streamText({
          model: myProvider.languageModel(selectedChatModel),
          system: systemPrompt({ selectedChatModel, requestHints }),
          messages: convertToModelMessages(processedUIMessages),
          stopWhen: stepCountIs(5),
          experimental_activeTools:
            selectedChatModel === 'chat-model-reasoning'
              ? []
              : [
                  'getWeather',
                  'createDocument',
                  'updateDocument',
                  'requestSuggestions',
                ],
          experimental_transform: smoothStream({ chunking: 'word' }),
          tools: {
            getWeather,
            createDocument: createDocument({ session, dataStream }),
            updateDocument: updateDocument({ session, dataStream }),
            requestSuggestions: requestSuggestions({
              session,
              dataStream,
            }),
          },
          experimental_telemetry: {
            isEnabled: isProductionEnvironment,
            functionId: 'stream-text',
          },
          onFinish: async ({ usage }) => {
            try {
              const providers = await getTokenlensCatalog();
              const modelId =
                myProvider.languageModel(selectedChatModel).modelId;
              if (!modelId) {
                finalMergedUsage = usage;
                dataStream.write({ type: 'data-usage', data: finalMergedUsage });
                return;
              }

              if (!providers) {
                finalMergedUsage = usage;
                dataStream.write({ type: 'data-usage', data: finalMergedUsage });
                return;
              }

              const summary = getUsage({ modelId, usage, providers });
              finalMergedUsage = { ...usage, ...summary, modelId } as AppUsage;
              dataStream.write({ type: 'data-usage', data: finalMergedUsage });
            } catch (err) {
              console.warn('TokenLens enrichment failed', err);
              finalMergedUsage = usage;
              dataStream.write({ type: 'data-usage', data: finalMergedUsage });
            }
          },
        });

        result.consumeStream();

        dataStream.merge(
          result.toUIMessageStream({
            sendReasoning: true,
          }),
        );
      },
      generateId: generateUUID,
      onFinish: async ({ messages }) => {
        await saveMessages({
          messages: messages.map((message) => ({
            id: message.id,
            role: message.role,
            parts: message.parts,
            createdAt: new Date(),
            attachments: [],
            chatId: id,
          })),
        });

        if (finalMergedUsage) {
          try {
            await updateChatLastContextById({
              chatId: id,
              context: finalMergedUsage,
            });
          } catch (err) {
            console.warn('Unable to persist last usage for chat', id, err);
          }
        }
      },
      onError: () => {
        return 'Oops, an error occurred!';
      },
    });

    const streamContext = getStreamContext();

    if (streamContext) {
      return new Response(
        await streamContext.resumableStream(streamId, () =>
          stream.pipeThrough(new JsonToSseTransformStream()),
        ),
      );
    } else {
      return new Response(stream.pipeThrough(new JsonToSseTransformStream()));
    }
  } catch (error) {
    if (error instanceof ChatSDKError) {
      return error.toResponse();
    }

    // Check for Vercel AI Gateway credit card error
    if (
      error instanceof Error &&
      error.message?.includes(
        'AI Gateway requires a valid credit card on file to service requests',
      )
    ) {
      return new ChatSDKError('bad_request:activate_gateway').toResponse();
    }

    console.error('Unhandled error in chat API:', error);
    return new ChatSDKError('offline:chat').toResponse();
  }
}

export async function DELETE(request: Request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get('id');

  if (!id) {
    return new ChatSDKError('bad_request:api').toResponse();
  }

  const session = await auth();

  if (!session?.user) {
    return new ChatSDKError('unauthorized:chat').toResponse();
  }

  const chat = await getChatById({ id });

  if (chat?.userId !== session.user.id) {
    return new ChatSDKError('forbidden:chat').toResponse();
  }

  const deletedChat = await deleteChatById({ id });

  return Response.json(deletedChat, { status: 200 });
}
