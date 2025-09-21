import React, { useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { localAIProvider } from '@/lib/ai/local-provider';

interface FileUploadProps {
  onFileAnalyzed: (analysis: string, riskScore: number, fileName: string) => void;
  disabled?: boolean;
}

export function FileUpload({ onFileAnalyzed, disabled }: FileUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Check file type
    const allowedTypes = ['application/pdf', 'text/plain'];
    if (!allowedTypes.includes(file.type)) {
      alert('Please upload a PDF or text file.');
      return;
    }

    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB.');
      return;
    }

    setUploading(true);

    try {
      let result;
      
      if (file.type === 'application/pdf') {
        result = await localAIProvider.uploadAndAnalyzePDF(file);
      } else {
        result = await localAIProvider.uploadAndAnalyzeText(file);
      }

      onFileAnalyzed(result.analysis, result.riskScore, file.name);
    } catch (error) {
      console.error('File upload error:', error);
      alert(`Failed to analyze file: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setUploading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  return (
    <>
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.txt"
        onChange={handleFileSelect}
        style={{ display: 'none' }}
      />
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={triggerFileSelect}
        disabled={disabled || uploading}
        className="flex items-center gap-2"
      >
        📎
        {uploading ? 'Analyzing...' : 'Upload Document'}
      </Button>
    </>
  );
}