import { NextResponse } from 'next/server';
import { z } from 'zod';
import { writeFile, mkdir } from 'fs/promises';
import { join } from 'path';
import { auth } from '@/app/(auth)/auth';
import { localAIProvider } from '@/lib/ai/local-provider';

// Use Blob instead of File since File is not available in Node.js environment
const FileSchema = z.object({
  file: z
    .instanceof(Blob)
    .refine((file) => file.size <= 10 * 1024 * 1024, {
      message: 'File size should be less than 10MB',
    })
    // Support images, PDFs, and text files
    .refine((file) => [
      'image/jpeg', 
      'image/png', 
      'image/gif', 
      'image/webp',
      'application/pdf',
      'text/plain'
    ].includes(file.type), {
      message: 'File type should be JPEG, PNG, GIF, WebP, PDF, or TXT',
    }),
});

export async function POST(request: Request) {
  const session = await auth();

  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  if (request.body === null) {
    return new Response('Request body is empty', { status: 400 });
  }

  try {
    const formData = await request.formData();
    const file = formData.get('file') as Blob;

    if (!file) {
      return NextResponse.json({ error: 'No file uploaded' }, { status: 400 });
    }

    const validatedFile = FileSchema.safeParse({ file });

    if (!validatedFile.success) {
      const errorMessage = validatedFile.error.errors
        .map((error) => error.message)
        .join(', ');

      return NextResponse.json({ error: errorMessage }, { status: 400 });
    }

    // Get filename from formData since Blob doesn't have name property
    const originalFilename = (formData.get('file') as File).name;
    const timestamp = Date.now();
    const filename = `${timestamp}-${originalFilename}`;
    const fileBuffer = await file.arrayBuffer();

    try {
      // Create uploads directory if it doesn't exist
      const uploadsDir = join(process.cwd(), 'public', 'uploads');
      await mkdir(uploadsDir, { recursive: true });

      // Save file to public/uploads directory
      const filePath = join(uploadsDir, filename);
      await writeFile(filePath, Buffer.from(fileBuffer));

      // Return the public URL that can be accessed from the frontend
      const publicUrl = `/uploads/${filename}`;
      
      let analysis = null;
      let riskScore = null;
      
      // If it's a PDF or text file, analyze it with local AI
      if (file.type === 'application/pdf' || file.type === 'text/plain') {
        try {
          const fileBlob = new File([fileBuffer], originalFilename, { type: file.type });
          let result;
          
          if (file.type === 'application/pdf') {
            result = await localAIProvider.uploadAndAnalyzePDF(fileBlob);
          } else {
            result = await localAIProvider.uploadAndAnalyzeText(fileBlob);
          }
          
          analysis = result.analysis;
          riskScore = result.riskScore;
        } catch (analysisError) {
          console.error('AI analysis failed:', analysisError);
          // Continue without analysis if it fails
        }
      }
      
      return NextResponse.json({
        url: publicUrl,
        pathname: publicUrl,
        contentType: file.type,
        contentDisposition: `inline; filename="${originalFilename}"`,
        size: file.size,
        analysis,
        riskScore
      });
    } catch (error) {
      console.error('Upload failed:', error);
      return NextResponse.json({ error: 'Upload failed' }, { status: 500 });
    }
  } catch (error) {
    console.error('Failed to process request:', error);
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 },
    );
  }
}
