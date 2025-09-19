#!/usr/bin/env python3

import subprocess
import json
import os
import sys
from datetime import datetime

def run_command(command, description):
    """Run shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description} - SUCCESS")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return None

def create_gcp_project():
    """Create Google Cloud Project with unique name"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    project_id = f"legal-ai-hackathon-{timestamp}"
    
    print(f"🏗️ Creating GCP Project: {project_id}")
    
    # Create project
    create_cmd = f"gcloud projects create {project_id} --name='Legal AI Hackathon'"
    if run_command(create_cmd, "Creating GCP project"):
        
        # Set as current project
        set_cmd = f"gcloud config set project {project_id}"
        run_command(set_cmd, "Setting current project")
        
        return project_id
    return None

def enable_apis(project_id):
    """Enable required Google Cloud APIs"""
    apis = [
        "documentai.googleapis.com",
        "aiplatform.googleapis.com", 
        "storage.googleapis.com",
        "firestore.googleapis.com",
        "run.googleapis.com",
        "cloudbuild.googleapis.com"
    ]
    
    print("🔌 Enabling Google Cloud APIs...")
    for api in apis:
        cmd = f"gcloud services enable {api} --project={project_id}"
        run_command(cmd, f"Enabling {api}")

def create_service_account(project_id):
    """Create service account with required permissions"""
    sa_name = "legal-ai-service"
    sa_email = f"{sa_name}@{project_id}.iam.gserviceaccount.com"
    
    print("👤 Creating Service Account...")
    
    # Create service account
    create_sa_cmd = f"""gcloud iam service-accounts create {sa_name} \
        --display-name="Legal AI Service Account" \
        --description="Service account for Legal AI Hackathon" \
        --project={project_id}"""
    
    if run_command(create_sa_cmd, "Creating service account"):
        
        # Grant required roles
        roles = [
            "roles/documentai.apiUser",
            "roles/aiplatform.user",
            "roles/storage.admin", 
            "roles/datastore.user",
            "roles/run.admin",
            "roles/cloudbuild.builds.editor"
        ]
        
        print("🔐 Granting IAM roles...")
        for role in roles:
            role_cmd = f"""gcloud projects add-iam-policy-binding {project_id} \
                --member="serviceAccount:{sa_email}" \
                --role="{role}" """
            run_command(role_cmd, f"Granting {role}")
        
        return sa_email
    return None

def create_service_account_key(project_id, sa_email):
    """Create and download service account key"""
    key_file = "service-account-key.json"
    
    print("🔑 Creating service account key...")
    
    key_cmd = f"""gcloud iam service-accounts keys create {key_file} \
        --iam-account={sa_email} \
        --project={project_id}"""
    
    if run_command(key_cmd, "Creating service account key"):
        if os.path.exists(key_file):
            print(f"✅ Service account key saved as: {key_file}")
            return key_file
    return None

def create_env_file(project_id, key_file):
    """Create .env file with configuration"""
    env_content = f"""# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT={project_id}
GOOGLE_APPLICATION_CREDENTIALS={key_file}

# Gemini API Key (Get from https://aistudio.google.com)
GEMINI_API_KEY=your_gemini_api_key_here

# Document AI Processor ID (Create in console if needed)
DOCUMENT_AI_PROCESSOR_ID=your_processor_id_here

# Storage Bucket Name
STORAGE_BUCKET_NAME={project_id}-legal-docs
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with configuration")

def create_project_structure():
    """Create project folder structure"""
    folders = [
        "config", "src", "ui", "api", "utils", "static", 
        "models", "database", "tests", "docs", "sample_data"
    ]
    
    print("📁 Creating project structure...")
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    
    # Create empty __init__.py files
    init_files = [
        "config/__init__.py", "src/__init__.py", "ui/__init__.py",
        "api/__init__.py", "utils/__init__.py", "models/__init__.py"
    ]
    
    for init_file in init_files:
        with open(init_file, 'w') as f:
            f.write("# Python package initialization\n")
    
    print("✅ Project structure created")

def create_requirements_file():
    """Create requirements.txt file"""
    requirements = """streamlit>=1.28.0
google-cloud-documentai>=2.15.0
google-cloud-aiplatform>=1.35.0
google-cloud-storage>=2.10.0
google-cloud-firestore>=2.11.0
google-generativeai>=0.3.0
PyPDF2>=3.0.1
python-dotenv>=1.0.0
streamlit-chat>=0.1.1
pandas>=2.0.0
pydantic>=2.0.0
requests>=2.31.0
langchain>=0.1.0
faiss-cpu>=1.7.4
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    print("✅ Created requirements.txt")

def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = """# Environment variables
.env
.env.local
.env.production

# Service account keys
service-account-key.json
*.json

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Streamlit
.streamlit/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Cache
.cache/
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    print("✅ Created .gitignore")

def create_app_py():
    """Create complete app.py file"""
    app_content = '''import streamlit as st
import os
from dotenv import load_dotenv
import PyPDF2
from io import BytesIO
import google.generativeai as genai
import re
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="⚖️ Legal Document Simplifier",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .result-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
    .risk-score {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .risk-low { background: #d4edda; color: #155724; }
    .risk-medium { background: #fff3cd; color: #856404; }  
    .risk-high { background: #f8d7da; color: #721c24; }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
    }
    .user-message {
        background: #e3f2fd;
        text-align: right;
    }
    .ai-message {
        background: #f3e5f5;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

class LegalAI:
    def __init__(self):
        """Initialize Gemini AI model"""
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key and api_key != 'your_gemini_api_key_here':
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-pro')
        else:
            self.model = None
    
    def extract_text_from_pdf(self, uploaded_file):
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\\n"
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            return ""
    
    def extract_text(self, uploaded_file):
        """Extract text from uploaded file"""
        if uploaded_file.type == "application/pdf":
            return self.extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "text/plain":
            return uploaded_file.read().decode('utf-8')
        else:
            st.error("Unsupported file type. Please upload PDF or TXT files.")
            return ""
    
    def analyze_document(self, text, document_type="legal document"):
        """Analyze document using Gemini AI"""
        if not self.model:
            return self.get_fallback_analysis(text)
        
        prompt = f"""
        You are an expert legal analyst. Analyze this {document_type} and provide a comprehensive analysis in the following structured format:

        **DOCUMENT SUMMARY** (2-3 sentences in simple, clear language):
        [Provide summary here]

        **KEY TERMS & CONDITIONS** (Top 5 most important terms):
        1. [Term 1] - [Simple explanation]
        2. [Term 2] - [Simple explanation]
        3. [Term 3] - [Simple explanation]
        4. [Term 4] - [Simple explanation]  
        5. [Term 5] - [Simple explanation]

        **RISK ASSESSMENT**:
        Overall Risk Score: [X/10]
        Risk Level: [Low/Medium/High]
        Explanation: [Why this risk level]

        **IMPORTANT DATES & DEADLINES**:
        - [List any important dates, deadlines, or time-sensitive clauses]

        **USER RIGHTS & PROTECTIONS**:
        - [List rights and protections the user has]

        **RED FLAGS & CONCERNING CLAUSES**:
        - [List any problematic or unfavorable terms]

        **INDIAN LEGAL CONTEXT** (if applicable):
        - Relevant Laws: [Applicable Indian laws]
        - Consumer Protections: [Available protections under Indian law]

        **RECOMMENDATIONS**:
        - [Specific recommendations for the user]

        Document text (analyzing first 3000 characters): {text[:3000]}
        
        Please provide detailed, accurate analysis following the exact format above.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.error(f"AI analysis error: {e}")
            return self.get_fallback_analysis(text)
    
    def get_fallback_analysis(self, text):
        """Provide fallback analysis when AI is unavailable"""
        word_count = len(text.split())
        return f"""
        **DOCUMENT SUMMARY**: This legal document contains {word_count} words and appears to be a standard legal agreement.

        **KEY TERMS & CONDITIONS**: 
        AI analysis is currently unavailable. Please check your Gemini API key configuration.

        **RISK ASSESSMENT**:
        Overall Risk Score: Unable to assess
        Risk Level: Please review manually
        Explanation: AI analysis requires valid API key

        **RECOMMENDATIONS**:
        - Review the document manually with legal counsel
        - Check your API configuration in the .env file
        - Ensure internet connectivity for AI analysis
        """
    
    def calculate_risk_score(self, text):
        """Calculate risk score based on document content"""
        text_lower = text.lower()
        
        high_risk_terms = [
            'penalty', 'fine', 'forfeit', 'default', 'breach', 'terminate', 
            'liable', 'damages', 'non-refundable', 'irrevocable', 'waive'
        ]
        
        medium_risk_terms = [
            'may terminate', 'subject to', 'condition', 'restriction', 
            'limit', 'discretion', 'modification', 'amendment'
        ]
        
        high_risk_count = sum(1 for term in high_risk_terms if term in text_lower)
        medium_risk_count = sum(1 for term in medium_risk_terms if term in text_lower)
        
        # Calculate score (1-10 scale)
        risk_score = min(10, 2 + high_risk_count * 1.5 + medium_risk_count * 0.5)
        
        return {
            'score': round(risk_score, 1),
            'level': self.get_risk_level(risk_score),
            'high_risk_count': high_risk_count,
            'medium_risk_count': medium_risk_count
        }
    
    def get_risk_level(self, score):
        """Determine risk level based on score"""
        if score <= 3:
            return "Low"
        elif score <= 6:
            return "Medium"
        else:
            return "High"
    
    def chat_response(self, question, document_text, analysis_context=""):
        """Generate AI response for chat"""
        if not self.model:
            return "AI chat is currently unavailable. Please check your Gemini API key configuration."
        
        prompt = f"""
        You are a helpful legal AI assistant. Answer the user's question about their legal document clearly and accurately.
        
        User Question: {question}
        
        Document Context: {document_text[:2000]}
        
        Analysis Context: {analysis_context[:1000]}
        
        Provide a helpful, accurate answer in simple language. If you cannot answer based on the document provided, clearly state this limitation.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {e}. Please check your API configuration."

# Initialize AI (cached for performance)
@st.cache_resource
def get_legal_ai():
    return LegalAI()

def main():
    """Main application function"""
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>⚖️ Legal Document Simplifier</h1>
        <p>AI-Powered Legal Analysis for Everyone - Hackathon Demo</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check API configuration
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your_gemini_api_key_here':
        st.error("🔑 Gemini API key not configured!")
        st.info("📝 Steps to fix:")
        st.code("""
1. Go to https://aistudio.google.com
2. Click 'Get API Key' → 'Create API Key'  
3. Copy the key
4. Edit your .env file and replace:
   GEMINI_API_KEY=your_actual_api_key_here
5. Restart the Streamlit app
        """)
        return
    
    # Initialize AI
    legal_ai = get_legal_ai()
    
    # Sidebar for file upload
    with st.sidebar:
        st.markdown("### 📂 Upload Legal Document")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'txt'],
            help="Upload PDF or TXT files (max 10MB)"
        )
        
        if uploaded_file:
            st.success(f"✅ {uploaded_file.name}")
            st.info(f"📊 Size: {uploaded_file.size / 1024:.1f} KB")
            
            # Analysis options
            st.markdown("### ⚙️ Analysis Options")
            include_indian_context = st.checkbox("🇮🇳 Include Indian Legal Context", value=True)
            analysis_depth = st.selectbox("📊 Analysis Depth", ["Quick", "Detailed", "Comprehensive"])
        
        # Help section
        st.markdown("---")
        st.markdown("### ❓ About")
        st.markdown("""
        **Legal AI Hackathon Project**
        
        🎯 **Features:**
        - Document text extraction
        - AI-powered legal analysis  
        - Risk assessment scoring
        - Interactive Q&A chat
        - Indian legal context
        
        🏆 **Built for Google Gen AI Exchange Hackathon 2025**
        """)
    
    # Main content area
    if uploaded_file:
        process_document(uploaded_file, legal_ai, include_indian_context)
    else:
        show_welcome_screen()

def show_welcome_screen():
    """Display welcome screen when no document is uploaded"""
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        st.markdown("""
        ### 🎯 How Legal AI Works
        
        **1. 📄 Upload Document**  
        Upload your legal document (PDF or TXT format)
        
        **2. 🤖 AI Analysis**  
        Advanced AI analyzes key terms, risks, and clauses
        
        **3. ⚠️ Risk Assessment**  
        Get numerical risk scores and detailed explanations
        
        **4. 💬 Interactive Chat**  
        Ask specific questions about your document
        
        **5. 🇮🇳 Indian Context**  
        Specialized analysis for Indian legal framework
        
        ---
        
        ### 📋 Supported Documents
        - Employment contracts
        - Rental agreements  
        - Loan documents
        - Terms of service
        - Privacy policies
        - Purchase agreements
        - Insurance policies
        
        ### 🚀 Get Started
        **Upload a document in the sidebar to begin!**
        """)

def process_document(uploaded_file, legal_ai, include_indian_context):
    """Process the uploaded document and display results"""
    
    # Check if document needs processing
    if ('current_file' not in st.session_state or 
        st.session_state.current_file != uploaded_file.name):
        
        with st.spinner("🔄 Analyzing your document... This may take a few moments."):
            # Extract text
            document_text = legal_ai.extract_text(uploaded_file)
            
            if not document_text:
                st.error("❌ Could not extract text from the document. Please try a different file.")
                return
            
            # Store document info
            st.session_state.document_text = document_text
            st.session_state.current_file = uploaded_file.name
            st.session_state.upload_time = datetime.now()
            
            # Get AI analysis
            analysis = legal_ai.analyze_document(document_text)
            st.session_state.analysis = analysis
            
            # Calculate risk score
            risk_data = legal_ai.calculate_risk_score(document_text)
            st.session_state.risk_data = risk_data
        
        st.success("✅ Document analysis complete!")
    
    # Display results
    display_analysis_results()

def display_analysis_results():
    """Display the analysis results in organized tabs"""
    
    # Quick metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        word_count = len(st.session_state.document_text.split())
        st.metric("📄 Words", f"{word_count:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        chars = len(st.session_state.document_text)
        st.metric("📊 Characters", f"{chars:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        risk_score = st.session_state.risk_data['score']
        st.metric("⚠️ Risk Score", f"{risk_score}/10")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        risk_level = st.session_state.risk_data['level']
        st.metric("📈 Risk Level", risk_level)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 AI Analysis", 
        "⚠️ Risk Assessment", 
        "💬 Ask Questions", 
        "📊 Document Stats"
    ])
    
    with tab1:
        display_ai_analysis()
    
    with tab2:
        display_risk_assessment()
    
    with tab3:
        display_chat_interface()
    
    with tab4:
        display_document_statistics()

def display_ai_analysis():
    """Display AI analysis results"""
    st.markdown("### 🤖 AI Legal Analysis")
    
    st.markdown('<div class="result-section">', unsafe_allow_html=True)
    st.markdown(st.session_state.analysis)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Analysis metadata
    st.markdown("---")
    st.markdown("**Analysis Details:**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"📅 **Analyzed:** {st.session_state.upload_time.strftime('%Y-%m-%d %H:%M')}")
        st.write(f"📄 **Document:** {st.session_state.current_file}")
    
    with col2:
        text_length = len(st.session_state.document_text)
        st.write(f"📏 **Text Length:** {text_length:,} characters")
        st.write(f"⏱️ **Reading Time:** ~{len(st.session_state.document_text.split()) // 200} minutes")

def display_risk_assessment():
    """Display detailed risk assessment"""
    st.markdown("### ⚠️ Risk Assessment Details")
    
    risk_data = st.session_state.risk_data
    risk_score = risk_data['score']
    risk_level = risk_data['level']
    
    # Main risk display
    risk_class = f"risk-{risk_level.lower()}"
    st.markdown(f"""
    <div class="risk-score {risk_class}">
        🎯 Overall Risk Score: {risk_score}/10
        <br>
        📊 Risk Level: {risk_level}
    </div>
    """, unsafe_allow_html=True)
    
    # Risk breakdown
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "🔴 High Risk Terms", 
            risk_data['high_risk_count'],
            help="Terms like penalty, forfeit, liable, etc."
        )
    
    with col2:
        st.metric(
            "🟡 Medium Risk Terms", 
            risk_data['medium_risk_count'],
            help="Terms like conditions, restrictions, etc."
        )
    
    with col3:
        reading_difficulty = "Complex" if len(st.session_state.document_text) > 5000 else "Moderate"
        st.metric("📖 Complexity", reading_difficulty)
    
    # Risk recommendations
    st.markdown("### 💡 Risk-Based Recommendations")
    
    if risk_score <= 3:
        st.success("""
        ✅ **Low Risk Document**
        - This document appears to have standard terms
        - Proceed with normal caution
        - Review key terms before signing
        """)
    elif risk_score <= 6:
        st.warning("""
        ⚠️ **Medium Risk Document**
        - Several concerning clauses identified
        - Review highlighted terms carefully
        - Consider seeking clarification on unclear points
        - You may want to negotiate certain terms
        """)
    else:
        st.error("""
        🚨 **High Risk Document**  
        - Multiple concerning clauses detected
        - Strong recommendation to seek legal counsel
        - Understand all penalties and termination conditions
        - Consider negotiating unfavorable terms
        - Do not sign without professional review
        """)

def display_chat_interface():
    """Display interactive chat interface"""
    st.markdown("### 💬 Ask Questions About Your Document")
    
    legal_ai = get_legal_ai()
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": "👋 Hi! I'm here to help you understand your legal document. What would you like to know?"
            }
        ]
    
    # Display chat history
    for message in st.session_state.chat_history:
        role = message['role']
        content = message['content']
        
        if role == 'user':
            st.markdown(f'<div class="chat-message user-message">**You:** {content}</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message ai-message">**Legal AI:** {content}</div>', 
                       unsafe_allow_html=True)
    
    # Quick action buttons
    st.markdown("#### 🚀 Quick Questions:")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 Key Terms"):
            process_chat_question("What are the most important terms I should understand in this document?")
    
    with col2:
        if st.button("⚠️ Main Risks"):
            process_chat_question("What are the biggest risks or concerns in this document?")
    
    with col3:
        if st.button("❌ Exit Terms"):
            process_chat_question("How can I terminate or exit this agreement? What are the conditions?")
    
    with col4:
        if st.button("🇮🇳 Indian Law"):
            process_chat_question("What Indian laws are relevant to this document?")
    
    # Chat input
    st.markdown("#### 💭 Ask Your Own Question:")
    user_question = st.text_input(
        "Type your question about the document:",
        key="chat_input",
        placeholder="e.g., What happens if I miss a payment?"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Send 📤", type="primary") and user_question:
            process_chat_question(user_question)

def process_chat_question(question):
    """Process a chat question and get AI response"""
    legal_ai = get_legal_ai()
    
    # Add user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": question
    })
    
    # Get AI response
    with st.spinner("🤔 Thinking..."):
        response = legal_ai.chat_response(
            question,
            st.session_state.document_text,
            st.session_state.analysis
        )
    
    # Add AI response
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": response
    })
    
    # Rerun to update display
    st.rerun()

def display_document_statistics():
    """Display detailed document statistics"""
    st.markdown("### 📊 Document Statistics & Analysis")
    
    text = st.session_state.document_text
    words = text.split()
    
    # Basic statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Basic Stats")
        st.write(f"**Total Characters:** {len(text):,}")
        st.write(f"**Total Words:** {len(words):,}")
        st.write(f"**Unique Words:** {len(set(words)):,}")
        st.write(f"**Average Word Length:** {sum(len(word) for word in words) / len(words):.1f}")
        st.write(f"**Sentences (approx.):** {text.count('.') + text.count('!') + text.count('?')}")
    
    with col2:
        st.markdown("#### ⏱️ Reading Info")
        reading_time = len(words) // 200  # Average reading speed
        st.write(f"**Estimated Reading Time:** {reading_time} minutes")
        st.write(f"**Document Complexity:** {'High' if len(text) > 10000 else 'Medium' if len(text) > 3000 else 'Low'}")
        st.write(f"**File Type:** {st.session_state.current_file.split('.')[-1].upper()}")
        st.write(f"**Analysis Date:** {st.session_state.upload_time.strftime('%B %d, %Y')}")
    
    # Text preview
    st.markdown("#### 👀 Document Preview")
    preview_text = text[:1000] + "..." if len(text) > 1000 else text
    st.text_area(
        "First 1000 characters:",
        preview_text,
        height=200,
        disabled=True,
        help="Preview of your document content"
    )

if __name__ == "__main__":
    main()
'''
    
    with open('app.py', 'w') as f:
        f.write(app_content)
    
    print("✅ Created complete app.py file")

def main():
    """Main setup function"""
    print("🚀 LEGAL AI HACKATHON - AUTOMATED GOOGLE CLOUD SETUP")
    print("=" * 60)
    
    # Check if gcloud is installed
    if not run_command("gcloud --version", "Checking gcloud CLI"):
        print("❌ Google Cloud CLI not found!")
        print("📥 Install from: https://cloud.google.com/sdk/docs/install")
        sys.exit(1)
    
    # Check if user is authenticated
    auth_check = run_command("gcloud auth list --filter=status:ACTIVE --format='value(account)'", 
                             "Checking authentication")
    if not auth_check:
        print("🔐 Please authenticate with Google Cloud:")
        print("Run: gcloud auth login")
        sys.exit(1)
    
    print(f"👤 Authenticated as: {auth_check}")
    
    # Create project
    project_id = create_gcp_project()
    if not project_id:
        print("❌ Failed to create project")
        sys.exit(1)
    
    # Enable APIs
    enable_apis(project_id)
    
    # Create service account
    sa_email = create_service_account(project_id)
    if not sa_email:
        print("❌ Failed to create service account")
        sys.exit(1)
    
    # Create service account key
    key_file = create_service_account_key(project_id, sa_email)
    if not key_file:
        print("❌ Failed to create service account key")
        sys.exit(1)
    
    # Create project files
    create_project_structure()
    create_requirements_file()
    create_gitignore()
    create_env_file(project_id, key_file)
    create_app_py()  # Create complete app.py
    
    print("\n" + "=" * 60)
    print("🎉 COMPLETE SETUP FINISHED!")
    print("=" * 60)
    print(f"📋 Project ID: {project_id}")
    print(f"👤 Service Account: {sa_email}")
    print(f"🔑 Key File: {key_file}")
    print(f"📱 App File: app.py (READY TO RUN)")
    print()
    print("🚨 IMMEDIATE NEXT STEPS:")
    print("1. Get Gemini API key: https://aistudio.google.com")
    print("2. Edit .env file: Add your GEMINI_API_KEY")
    print("3. Install dependencies: pip install -r requirements.txt") 
    print("4. Run the app: streamlit run app.py")
    print()
    print("⏰ You're ready to start in 5 minutes!")
    print("🏆 TIME SAVED: ~45 minutes of setup work!")

if __name__ == "__main__":
    main()