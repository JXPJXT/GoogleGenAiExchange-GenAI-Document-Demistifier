import streamlit as st
import os
from dotenv import load_dotenv
import PyPDF2
from io import BytesIO
import google.generativeai as genai
import re

# --- Load Environment Variables ---
load_dotenv()

# --- Page Configuration ---
st.set_page_config(page_title="LegalLens AI", page_icon="⚖️", layout="wide")

# --- Custom CSS Styling ---
css = """
<style>
.main-header {
    text-align: center;
    padding: 2rem 0;
    background: linear-gradient(90deg, #4a5eff 0%, #8a4af2 100%);
    color: #ffffff;
    border-radius: 10px;
    margin-bottom: 2rem;
    font-size: 2rem;
    font-weight: bold;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
}
.risk-high {
    background: #ffebee;
    color: #b71c1c;
    padding: 1rem;
    border-radius: 5px;
    border-left: 5px solid #b71c1c;
    font-size: 1.2rem;
    font-weight: bold;
}
.risk-medium {
    background: #fff3e0;
    color: #d84315;
    padding: 1rem;
    border-radius: 5px;
    border-left: 5px solid #d84315;
    font-size: 1.2rem;
    font-weight: bold;
}
.risk-low {
    background: #e8f5e9;
    color: #1b5e20;
    padding: 1rem;
    border-radius: 5px;
    border-left: 5px solid #1b5e20;
    font-size: 1.2rem;
    font-weight: bold;
}
.chat-message {
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 10px;
    font-size: 1.1rem;
    line-height: 1.5;
    max-width: 80%;
}
.user-message {
    background: #e3f2fd;
    color: #1e88e5;
    text-align: right;
    margin-left: auto;
}
.ai-message {
    background: #f3e5f5;
    color: #6a1b9a;
    margin-right: auto;
}
.stTextInput > div > input {
    color: #ffffff;
    background-color: #2c2c2c;
    border: 1px solid #444;
    padding: 0.7rem;
    font-size: 1.1rem;
    border-radius: 5px;
}
.stButton > button {
    background-color: #4a5eff;
    color: white;
    border: none;
    padding: 0.7rem 1.5rem;
    font-size: 1rem;
    border-radius: 5px;
    transition: background-color 0.3s;
}
.stButton > button:hover {
    background-color: #6a70ff;
}
.stMetric > div {
    color: #ffffff;
    font-size: 1.2rem;
}
.stTabs [data-baseweb="tab-list"] {
    background-color: #2c2c2c;
    border-bottom: 1px solid #444;
}
.stTabs [data-baseweb="tab"] {
    color: #bbbbbb;
    font-size: 1.1rem;
    padding: 0.7rem 1.2rem;
    border: none;
}
.stTabs [data-baseweb="tab"]:hover {
    background-color: #4a5eff;
    color: #ffffff;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background-color: #3a3a3a;
    color: #ffffff;
    border-bottom: 2px solid #4a5eff;
}
.sidebar .stFileUploader {
    background-color: #2c2c2c;
    padding: 1rem;
    border-radius: 5px;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# --- Core AI Class ---
class LegalAI:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key and api_key != 'your_gemini_api_key_here':
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            self.model = None

    def extract_text(self, uploaded_file):
        if uploaded_file.type == "application/pdf":
            try:
                reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
                return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
            except Exception as e:
                st.error(f"Error reading PDF: {e}")
                return ""
        return uploaded_file.read().decode('utf-8')

    def analyze_document(self, text):
        if not self.model:
            return f"AI analysis unavailable. Document has {len(text.split())} words."

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
            st.error(f"An error occurred during analysis: {e}")
            return "Failed to generate analysis. Please try again."

    def extract_risk_score_from_analysis(self, analysis_text):
        match = re.search(r"Risk Score \(1-10\):\*\*.*?(\d+)", analysis_text, re.IGNORECASE | re.DOTALL)
        if match:
            return int(match.group(1))
        return 5

    def chat_response(self, question, document_text):
        if not self.model:
            return "Chat unavailable - please check your API key."

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
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {e}"

# --- Streamlit App Main Logic ---
@st.cache_resource
def get_ai():
    return LegalAI()

def main():
    if not os.getenv('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY') == 'your_gemini_api_key_here':
        st.error("Your Gemini API key is not configured. Get a key from https://aistudio.google.com and add it to your .env file.")
        return

    ai = get_ai()

    with st.sidebar:
        st.header("Upload Your Document")
        uploaded_file = st.file_uploader("Supports PDF and TXT files", type=['pdf', 'txt'])

        if uploaded_file:
            st.success(f"Loaded: {uploaded_file.name}")

    st.markdown("<div class='main-header'><h1>LegalLens AI</h1></div>", unsafe_allow_html=True)

    if uploaded_file:
        if 'current_file' not in st.session_state or st.session_state.current_file != uploaded_file.name:
            with st.spinner("Reading and analyzing your document... This may take a moment."):
                text = ai.extract_text(uploaded_file)
                if text:
                    analysis = ai.analyze_document(text)
                    risk_score = ai.extract_risk_score_from_analysis(analysis)

                    st.session_state.update({
                        'text': text,
                        'analysis': analysis,
                        'risk_score': risk_score,
                        'current_file': uploaded_file.name,
                        'chat_history': []
                    })
                else:
                    st.session_state.clear()

        if 'analysis' in st.session_state:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Word Count", f"{len(st.session_state.text.split()):,}")
            with col2:
                st.metric("AI Risk Score", f"{st.session_state.risk_score}/10")
            with col3:
                level = "High" if st.session_state.risk_score >= 8 else "Medium" if st.session_state.risk_score >= 5 else "Low"
                st.metric("Risk Level", level)

            tab1, tab2, tab3 = st.tabs(["Full Analysis", "Risk Details", "Chat with Document"])

            with tab1:
                st.markdown("### Complete AI-Generated Analysis")
                st.markdown(st.session_state.analysis, unsafe_allow_html=True)

            with tab2:
                st.markdown("### Risk Assessment Overview")
                risk_class = f"risk-{'high' if st.session_state.risk_score >= 8 else 'medium' if st.session_state.risk_score >= 5 else 'low'}"
                st.markdown(f"<div class='{risk_class}'>This document has a risk score of <strong>{st.session_state.risk_score}/10</strong>. Refer to the 'Red Flags' section in the full analysis for specific details.</div>", unsafe_allow_html=True)

            with tab3:
                st.markdown("### Chat with Your Document")
                for msg in st.session_state.get('chat_history', []):
                    st.markdown(f"<div class='chat-message { 'user-message' if msg['role'] == 'user' else 'ai-message' }'>{msg['content']}</div>", unsafe_allow_html=True)

                question = st.text_input("Enter your question (e.g., 'What does the termination clause say?')")
                if st.button("Send") and question:
                    st.session_state.chat_history.append({"role": "user", "content": f"You: {question}"})
                    with st.spinner("Generating response..."):
                        response = ai.chat_response(question, st.session_state.text)
                    st.session_state.chat_history.append({"role": "ai", "content": f"AI: {response}"})
                    st.rerun()

    else:
        st.info("Upload a document using the sidebar to begin your analysis.")
        st.markdown("""
        ### How It Works
        1. **Upload:** Provide a legal document (PDF or TXT).
        2. **Analyze:** Our AI reads the entire document to identify key terms, obligations, and potential risks.
        3. **Review:** Get a clear, structured summary with a risk score and detailed explanations.
        4. **Inquire:** Use the chat to ask specific questions and get instant, context-aware answers.
        """)

if __name__ == "__main__":
    main()