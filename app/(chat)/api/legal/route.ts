import { auth } from '@/app/(auth)/auth';
import { ChatSDKError } from '@/lib/errors';
import { NextRequest } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const session = await auth();
    
    if (!session?.user) {
      return new ChatSDKError('unauthorized:api').toResponse();
    }

    const contentType = request.headers.get('content-type');
    
    // Handle file upload
    if (contentType?.includes('multipart/form-data')) {
      const formData = await request.formData();
      const file = formData.get('file') as File;
      
      if (!file) {
        return new ChatSDKError(
          'bad_request:api',
          'No file provided for legal analysis'
        ).toResponse();
      }

      // Forward the file to the legal analysis backend
      const backendFormData = new FormData();
      backendFormData.append('file', file);

      const response = await fetch(`${BACKEND_URL}/analyze:file`, {
        method: 'POST',
        body: backendFormData,
      });

      if (!response.ok) {
        throw new Error(`Backend analysis failed: ${response.statusText}`);
      }

      const analysisResult = await response.json();
      
      return Response.json({
        success: true,
        analysis: analysisResult.analysis,
        risk_score: analysisResult.risk_score,
        document_type: 'legal_document',
        timestamp: new Date().toISOString(),
      });
    }

    // Handle text analysis
    const { text } = await request.json();
    
    if (!text) {
      return new ChatSDKError(
        'bad_request:api',
        'No text provided for legal analysis'
      ).toResponse();
    }

    const response = await fetch(`${BACKEND_URL}/analyze:text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error(`Backend analysis failed: ${response.statusText}`);
    }

    const analysisResult = await response.json();
    
    return Response.json({
      success: true,
      analysis: analysisResult.analysis,
      risk_score: analysisResult.risk_score,
      document_type: 'legal_text',
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error('Legal analysis error:', error);
    return new ChatSDKError(
      'bad_request:api',
      'Failed to perform legal analysis'
    ).toResponse();
  }
}

// Legal document chat endpoint
export async function PUT(request: NextRequest) {
  try {
    const session = await auth();
    
    if (!session?.user) {
      return new ChatSDKError('unauthorized:api').toResponse();
    }

    const { document_text, question } = await request.json();
    
    if (!document_text || !question) {
      return new ChatSDKError(
        'bad_request:api',
        'Both document_text and question are required for legal chat'
      ).toResponse();
    }

    const response = await fetch(`${BACKEND_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ document_text, question }),
    });

    if (!response.ok) {
      throw new Error(`Backend chat failed: ${response.statusText}`);
    }

    const chatResult = await response.json();
    
    return Response.json({
      success: true,
      answer: chatResult.answer,
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error('Legal chat error:', error);
    return new ChatSDKError(
      'bad_request:api',
      'Failed to process legal chat question'
    ).toResponse();
  }
}