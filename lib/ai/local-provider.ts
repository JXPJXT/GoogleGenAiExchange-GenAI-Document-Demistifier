// Local AI Provider for LegalLens AI
export const LOCAL_AI_BASE_URL = 'http://localhost:8000';

export class LocalAIProvider {
  private baseUrl: string;

  constructor(baseUrl: string = LOCAL_AI_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async chatCompletion(messages: any[], options: any = {}) {
    // Validate messages array
    if (!messages || !Array.isArray(messages) || messages.length === 0) {
      throw new Error('No messages provided or messages array is empty');
    }

    const lastMessage = messages[messages.length - 1];
    
    // Validate last message exists
    if (!lastMessage) {
      throw new Error('Last message is undefined or null');
    }
    
    // Handle different message formats (content vs parts)
    let question = '';
    
    // Helper function to extract text from nested structures
    const extractTextRecursively = (obj: any): string => {
      if (typeof obj === 'string') return obj;
      if (!obj) return '';
      
      // Check for direct text properties
      if (obj.text) return obj.text;
      if (obj.content && typeof obj.content === 'string') return obj.content;
      
      // Handle arrays
      if (Array.isArray(obj)) {
        for (const item of obj) {
          const text = extractTextRecursively(item);
          if (text && text.trim()) return text;
        }
        return '';
      }
      
      // Handle objects with parts
      if (obj.parts && Array.isArray(obj.parts)) {
        for (const part of obj.parts) {
          if (part.type === 'text' && part.text) return part.text;
        }
      }
      
      // Handle content arrays
      if (obj.content && Array.isArray(obj.content)) {
        for (const item of obj.content) {
          // Skip system messages, look for user content
          if (item.role === 'user') {
            const text = extractTextRecursively(item);
            if (text && text.trim()) return text;
          } else if (item.type === 'text' && item.text) {
            return item.text;
          }
        }
      }
      
      return '';
    };
    
    question = extractTextRecursively(lastMessage);
    
    console.log(`Extracted question from message: "${question}"`);

    // Ensure we have a question to send
    if (!question.trim()) {
      console.error('No question extracted from message:', JSON.stringify(lastMessage, null, 2));
      throw new Error('No valid text content found in message');
    }

    // Extract document context if available from previous messages
    let documentText = null;
    for (const message of messages) {
      const messageContent = message.content || (message.parts ? message.parts.find((p: any) => p.type === 'text')?.text : '');
      if (message.role === 'system' && messageContent && messageContent.includes('DOCUMENT:')) {
        documentText = messageContent;
        break;
      }
    }

    const response = await fetch(`${this.baseUrl}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        document_text: documentText,
      }),
    });

    if (!response.ok) {
      throw new Error(`Local AI request failed: ${response.status}`);
    }

    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error);
    }

    return {
      choices: [{
        message: {
          content: data.response,
          role: 'assistant',
        },
      }],
      usage: {
        prompt_tokens: 0,
        completion_tokens: 0,
        total_tokens: 0,
      },
    };
  }

  async uploadAndAnalyzePDF(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/upload-pdf`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`PDF upload failed: ${response.status}`);
    }

    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error);
    }

    return {
      analysis: data.analysis,
      riskScore: data.risk_score,
    };
  }

  async uploadAndAnalyzeText(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/upload-text`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Text upload failed: ${response.status}`);
    }

    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error);
    }

    return {
      analysis: data.analysis,
      riskScore: data.risk_score,
    };
  }

  async analyzeTextDirectly(text: string) {
    const response = await fetch(`${this.baseUrl}/analyze-text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error(`Text analysis failed: ${response.status}`);
    }

    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error);
    }

    return {
      analysis: data.analysis,
      riskScore: data.risk_score,
    };
  }

  async healthCheck() {
    try {
      const response = await fetch(`${this.baseUrl}/`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

export const localAIProvider = new LocalAIProvider();