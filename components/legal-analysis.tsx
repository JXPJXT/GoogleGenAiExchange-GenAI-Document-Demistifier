'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Upload } from 'lucide-react';
import { toast } from 'sonner';

interface LegalAnalysisResult {
  success: boolean;
  analysis: string;
  risk_score: number;
  document_type: string;
  timestamp: string;
}

export function LegalAnalysis() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<LegalAnalysisResult | null>(null);
  const [textInput, setTextInput] = useState('');

  const analyzeText = async () => {
    if (!textInput.trim()) {
      toast.error('Please enter text to analyze');
      return;
    }

    setIsAnalyzing(true);
    try {
      const response = await fetch('/api/legal', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: textInput }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze text');
      }

      const result = await response.json();
      setAnalysisResult(result);
      toast.success('Text analysis completed');
    } catch (error) {
      console.error('Analysis error:', error);
      toast.error('Failed to analyze text');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const analyzeFile = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf') && !file.name.toLowerCase().endsWith('.txt')) {
      toast.error('Please upload a PDF or TXT file');
      return;
    }

    setIsAnalyzing(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/legal', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to analyze document');
      }

      const result = await response.json();
      setAnalysisResult(result);
      toast.success('Document analysis completed');
    } catch (error) {
      console.error('Analysis error:', error);
      toast.error('Failed to analyze document');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 7) return 'text-red-600 bg-red-50';
    if (score >= 4) return 'text-yellow-600 bg-yellow-50';
    return 'text-green-600 bg-green-50';
  };

  const getRiskLabel = (score: number) => {
    if (score >= 7) return 'High Risk';
    if (score >= 4) return 'Medium Risk';
    return 'Low Risk';
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            ⚖️ Legal Document Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Text Analysis */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Analyze Legal Text
            </label>
            <Textarea
              placeholder="Paste your legal document text here..."
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              rows={6}
              className="w-full"
            />
            <Button 
              onClick={analyzeText}
              disabled={isAnalyzing}
              className="mt-2"
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze Text'}
            </Button>
          </div>

          {/* File Upload */}
          <div className="border-t pt-4">
            <label className="block text-sm font-medium mb-2">
              Upload Legal Document
            </label>
            <div className="flex items-center gap-2">
              <input
                type="file"
                accept=".pdf,.txt"
                onChange={analyzeFile}
                disabled={isAnalyzing}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                <Upload className="h-4 w-4" />
                {isAnalyzing ? 'Processing...' : 'Upload PDF/TXT'}
              </label>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysisResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-between gap-2">
              Analysis Results
              <span className={`px-2 py-1 rounded text-xs font-medium ${getRiskColor(analysisResult.risk_score)}`}>
                {getRiskLabel(analysisResult.risk_score)} ({analysisResult.risk_score}/10)
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="prose max-w-none">
              <div className="whitespace-pre-wrap text-sm">
                {analysisResult.analysis}
              </div>
              <div className="mt-4 text-xs text-gray-500">
                Analyzed on {new Date(analysisResult.timestamp).toLocaleString()}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}