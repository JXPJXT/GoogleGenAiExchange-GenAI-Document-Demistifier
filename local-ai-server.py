from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import PyPDF2
from io import BytesIO
import google.generativeai as genai
import re
from typing import Optional
import uvicorn

# Load environment variables
load_dotenv()

app = FastAPI(title="LegalLens AI Server", version="1.0.0")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str
    document_text: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    error: Optional[str] = None

class AnalysisResponse(BaseModel):
    analysis: str
    risk_score: int
    error: Optional[str] = None

class LegalAI:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key and api_key != 'your_gemini_api_key_here':
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            self.model = None

    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF bytes."""
        try:
            reader = PyPDF2.PdfReader(BytesIO(file_content))
            return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading PDF: {e}")

    def extract_text_from_txt(self, file_content: bytes) -> str:
        """Extract text from TXT bytes."""
        try:
            return file_content.decode('utf-8')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading text file: {e}")

    def analyze_document(self, text: str) -> str:
        """Analyze a legal document and return detailed analysis."""
        if not self.model:
            word_count = len(text.split())
            return f"""**Disclaimer:** I am an AI assistant and not a lawyer. This analysis is for informational purposes only and does not constitute legal advice. You should consult with a qualified legal professional for advice on your specific situation before taking any action.

### 1. Executive Summary & Risk Score
* **Quick Summary:** This document contains {word_count} words. Local analysis shows it's a legal document that requires professional review.
* **Risk Score (1-10):** 5
* **Justification:** Unable to perform full AI analysis - recommend professional legal review.

### 2. Document Overview
* **Document Length:** {word_count} words
* **Analysis Status:** Local mode - full AI analysis unavailable
* **Recommendation:** Consult with a qualified legal professional for comprehensive analysis

### 3. Next Steps
* **Immediate Action:** Review the document with a legal professional
* **Professional Consultation:** Recommended for all legal documents
* **Document Preparation:** Prepare specific questions about terms and obligations

**Note:** To enable full AI-powered analysis, please configure the appropriate API keys in the system settings."""

        prompt = f"""
        You are LegalLens AI, a specialized assistant designed to help non-lawyers understand complex legal documents.
        Your primary goal is to provide a clear, unbiased, and practical analysis. Your tone should be supportive, simple, and empowering.
        You must never provide legal advice, but rather empower the user to ask the right questions.
        Always begin your analysis with the following disclaimer in bold:
        "**Disclaimer:** I am an AI assistant and not a lawyer. This analysis is for informational purposes only and does not constitute legal advice. You should consult with a qualified legal professional for advice on your specific situation before taking any action."

        Analyze the legal document provided below. The user's jurisdiction is India.
        Generate your analysis in a clear, well-structured markdown format, following these sections precisely:

        ### 1. Executive Summary & Risk Score
        * **Quick Summary (2-3 sentences):**
        * **Risk Score (1-10):** [Assign a score from 1 to 10]
        * **Justification:** [Explain the score]

        ### 2. Your Role & Obligations
        * **Who You Are in This Document:**
        * **Your Core Obligations (Bulleted List):**
        * **Your Core Rights (Bulleted List):**

        ### 3. Red Flags & Clauses to Review
        *For each red flag:*
        * **Clause Reference:** [Clause Number and Title]
        * **What it Says:** [Plain English summary]
        * **The Red Flag:** [Why it's a concern]
        * **Potential Impact:** [Real-world negative scenario]
        * **Questions to Ask / Points to Negotiate:** [Suggested actions]

        ### 4. Key Terms Explained
        *Provide a markdown table for the 5 most important terms.*

        ### 5. Legal & Compliance Context (India)
        * **Relevant Laws:** [List key Indian laws]
        * **Compliance Check:** [Note any clauses that seem questionable under Indian law]

        ### 6. Potential Gaps & Omissions
        *Identify 1-2 important missing clauses.*

        ### 7. Actionable Next Steps
        *Provide a bulleted list of next steps.*

        ---
        DOCUMENT TEXT:
        {text}
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred during analysis: {e}")

    def is_legal_question(self, question: str) -> bool:
        """Check if the question is related to legal matters."""
        legal_keywords = [
            # Legal terms
            'contract', 'agreement', 'law', 'legal', 'clause', 'terms', 'conditions',
            'rights', 'obligations', 'liability', 'breach', 'lawsuit', 'court',
            'attorney', 'lawyer', 'advocate', 'judge', 'jurisdiction', 'compliance',
            
            # Document types
            'lease', 'rental', 'employment', 'nda', 'confidentiality', 'partnership',
            'shareholder', 'merger', 'acquisition', 'license', 'patent', 'trademark',
            'copyright', 'intellectual property', 'privacy policy', 'terms of service',
            
            # Legal processes
            'dispute', 'arbitration', 'mediation', 'litigation', 'settlement',
            'injunction', 'damages', 'compensation', 'penalty', 'fine',
            
            # Business/Legal entities
            'company', 'corporation', 'llc', 'partnership', 'proprietorship',
            'board', 'director', 'shareholder', 'stakeholder', 'regulatory',
            
            # Indian legal terms
            'indian law', 'ipc', 'crpc', 'contract act', 'companies act',
            'consumer protection', 'labour law', 'taxation', 'gst',
            
            # Legal actions/verbs
            'sue', 'prosecute', 'defend', 'appeal', 'file', 'claim', 'enforce',
            'terminate', 'void', 'valid', 'invalid', 'binding', 'non-binding'
        ]
        
        # Convert question to lowercase for checking
        question_lower = question.lower()
        
        # Check for legal keywords
        for keyword in legal_keywords:
            if keyword in question_lower:
                return True
        
        # Check for question patterns that might be legal
        legal_patterns = [
            'what does this mean',
            'what are my rights',
            'what are my obligations',
            'can i',
            'should i sign',
            'is this legal',
            'what happens if',
            'how to',
            'what is the penalty',
            'what is the risk'
        ]
        
        for pattern in legal_patterns:
            if pattern in question_lower:
                return True
                
        return False

    def extract_risk_score_from_analysis(self, analysis_text: str) -> int:
        """Extract risk score from analysis text."""
        match = re.search(r"Risk Score \(1-10\):\*\*.*?(\d+)", analysis_text, re.IGNORECASE | re.DOTALL)
        if match:
            return int(match.group(1))
        return 5

    def chat_response(self, question: str, document_text: Optional[str] = None) -> str:
        """Generate a response to a user question, optionally based on document context."""
        
        # First check if this is a legal question (unless we have document context)
        if not document_text and not self.is_legal_question(question):
            return """I'm LegalLens AI, a specialized legal document assistant. I'm designed specifically to help with legal matters and document analysis.

I can assist you with:
• Legal document analysis and review
• Contract terms and conditions explanation
• Rights and obligations clarification
• Legal compliance questions
• Risk assessment of agreements
• Legal terminology explanations
• Indian law-related queries

For non-legal questions, please consult other appropriate resources or AI assistants.

**Please ask me a legal-related question, and I'll be happy to help!**

**Disclaimer:** I am an AI assistant and not a lawyer. My responses are for informational purposes only and do not constitute legal advice."""
        
        if not self.model:
            # Provide a helpful response when AI model is not available
            return f"""Hello! I'm LegalLens AI, your local legal document assistant. 

Currently running in local mode without external AI connections. While I can still help with:
- PDF document analysis and text extraction
- Basic document structure understanding
- Risk assessment frameworks
- Legal terminology explanations

For your question: "{question}"

I recommend consulting with a qualified legal professional for specific advice. If you'd like to enable full AI capabilities, please configure your API keys in the environment settings.

**Disclaimer:** This is an AI assistant and not a lawyer. This response is for informational purposes only and does not constitute legal advice."""

        if document_text:
            prompt = f"""
            You are LegalLens AI, a helpful legal assistant.
            The user is asking a question about the following document.
            Provide a clear, concise answer based ONLY on the provided document's content.
            If the answer is not in the document, state that clearly.

            DOCUMENT:
            ---
            {document_text}
            ---

            USER'S QUESTION: "{question}"

            ANSWER:
            """
        else:
            prompt = f"""
            You are LegalLens AI, a helpful legal assistant.
            The user is asking a general legal question.
            Provide a helpful, informative response while making it clear that this is not legal advice.
            Always remind users to consult with a qualified legal professional for specific legal matters.

            USER'S QUESTION: "{question}"

            ANSWER:
            """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating response: {e}")

# Initialize the AI instance
legal_ai = LegalAI()

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "LegalLens AI Server is running", "status": "healthy"}

@app.post("/upload-pdf", response_model=AnalysisResponse)
async def upload_and_analyze_pdf(file: UploadFile = File(...)):
    """Upload a PDF file and get legal analysis."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Extract text from PDF
        text = legal_ai.extract_text_from_pdf(file_content)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Generate analysis
        analysis = legal_ai.analyze_document(text)
        risk_score = legal_ai.extract_risk_score_from_analysis(analysis)
        
        return AnalysisResponse(analysis=analysis, risk_score=risk_score)
        
    except HTTPException:
        raise
    except Exception as e:
        return AnalysisResponse(analysis="", risk_score=5, error=str(e))

@app.post("/upload-text", response_model=AnalysisResponse)
async def upload_and_analyze_text(file: UploadFile = File(...)):
    """Upload a text file and get legal analysis."""
    if file.content_type != "text/plain":
        raise HTTPException(status_code=400, detail="Only text files are supported")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Extract text from file
        text = legal_ai.extract_text_from_txt(file_content)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text file is empty")
        
        # Generate analysis
        analysis = legal_ai.analyze_document(text)
        risk_score = legal_ai.extract_risk_score_from_analysis(analysis)
        
        return AnalysisResponse(analysis=analysis, risk_score=risk_score)
        
    except HTTPException:
        raise
    except Exception as e:
        return AnalysisResponse(analysis="", risk_score=5, error=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """Chat with the AI, optionally with document context."""
    try:
        response = legal_ai.chat_response(request.question, request.document_text)
        return ChatResponse(response=response)
    except HTTPException:
        raise
    except Exception as e:
        return ChatResponse(response="", error=str(e))

@app.post("/analyze-text", response_model=AnalysisResponse)
async def analyze_text_directly(request: dict):
    """Analyze text content directly without file upload."""
    text = request.get("text", "")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text content is required")
    
    try:
        analysis = legal_ai.analyze_document(text)
        risk_score = legal_ai.extract_risk_score_from_analysis(analysis)
        return AnalysisResponse(analysis=analysis, risk_score=risk_score)
    except Exception as e:
        return AnalysisResponse(analysis="", risk_score=5, error=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)