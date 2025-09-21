# LegalLens AI Chatbot

A comprehensive legal document analysis chatbot powered by local AI integration with Google Gemini. This application can analyze PDF documents, answer legal questions, and provide detailed legal insights.

## 🚀 Features

- **PDF Document Analysis**: Upload and analyze legal documents
- **Legal Q&A**: Ask questions about contract law, legal principles, and document-specific queries
- **Local AI Integration**: Uses Google Gemini API for intelligent responses
- **Legal Question Filtering**: Only responds to legal-related questions
- **Document Context**: Maintains document context for follow-up questions
- **Real-time Chat Interface**: Modern React-based chat UI
- **File Upload Support**: Supports PDF and text file uploads

## 📋 Prerequisites

Before running the application, ensure you have:

- **Node.js** (version 18 or higher)
- **Python** (version 3.8 or higher)
- **npm** or **pnpm**
- **Google Gemini API Key** (free at [Google AI Studio](https://makersuite.google.com/app/apikey))

## 🛠️ Installation & Setup

### Step 1: Clone/Extract the Project
Extract the project folder to your desired location.

### Step 2: Get Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a free API key
3. Copy the API key for the next step

### Step 3: Configure Environment Variables
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file and add your API key:
   ```bash
   GEMINI_API_KEY=your_actual_api_key_here
   AUTH_SECRET=your_random_secret_here
   ```

### Step 4: Install Dependencies

#### Frontend (Next.js)
```bash
npm install
# or
pnpm install
```

#### Backend (Python AI Server)
```bash
pip install -r local-ai-requirements.txt
```

## 🚀 Running the Application

You need to run both the **Frontend** and **Backend** servers:

### Option 1: Manual Startup

#### Terminal 1 - Start the AI Server (Python)
```bash
# Windows
start-ai-server.bat

# Mac/Linux
chmod +x start-ai-server.sh
./start-ai-server.sh

# Or manually
python local-ai-server.py
```

#### Terminal 2 - Start the Frontend (Next.js)
```bash
npm run dev
# or
pnpm dev
```

### Option 2: Quick Start Scripts

**Windows:**
1. Double-click `start-ai-server.bat` to start the Python server
2. Open a new terminal and run `npm run dev` for the frontend

**Mac/Linux:**
1. Run `./start-ai-server.sh` to start the Python server
2. Open a new terminal and run `npm run dev` for the frontend

## 🌐 Access the Application

Once both servers are running:

- **Frontend**: http://localhost:3000
- **AI Server API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📖 Usage Guide

### 1. Basic Legal Questions
Ask questions like:
- "What are the basic principles of contract law?"
- "What should I know about employment contracts?"
- "Explain intellectual property rights"

### 2. Document Analysis
1. Click the **file upload** button
2. Select a PDF document (legal contracts, agreements, etc.)
3. Wait for the success message
4. Ask questions about the document:
   - "What should I know about this document?"
   - "What are the key terms and conditions?"
   - "Are there any red flags I should be aware of?"

### 3. Legal Question Filtering
The AI only responds to legal-related questions. Non-legal questions will be politely declined with guidance to ask legal questions.

## 🔧 Configuration

### AI Server Configuration
- **Port**: 8000 (configurable in `local-ai-server.py`)
- **Model**: Google Gemini Pro
- **Legal Keywords**: 40+ legal terms for question filtering

### Frontend Configuration
- **Port**: 3000 (Next.js default)
- **Database**: SQLite (local development)
- **File Uploads**: Stored in `public/uploads/`

## 🐛 Troubleshooting

### Common Issues

#### 1. "Cannot find module 'ai'" or TypeScript errors
```bash
npm install @ai-sdk/react ai --legacy-peer-deps
```

#### 2. Python server won't start
- Ensure Python 3.8+ is installed
- Install requirements: `pip install -r local-ai-requirements.txt`
- Check if port 8000 is available

#### 3. API Key errors
- Verify your `GEMINI_API_KEY` in `.env` file
- Ensure the API key is valid and active

#### 4. File upload errors
- Ensure `public/uploads/` directory exists
- Check file permissions

#### 5. Chat responses not appearing
- Verify both servers are running
- Check browser console for errors
- Ensure API server is accessible at http://localhost:8000

### Debug Mode
Enable debug logging by setting environment variables:
```bash
# In .env file
DEBUG=true
LOG_LEVEL=debug
```

## 📁 Project Structure

```
ai-chatbot/
├── app/                    # Next.js app directory
├── components/             # React components
├── lib/                   # Utility libraries
├── public/                # Static files and uploads
├── local-ai-server.py     # Python AI server
├── local-ai-requirements.txt  # Python dependencies
├── package.json           # Node.js dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## 🔐 Security Notes

- Keep your `GEMINI_API_KEY` secure and never commit it to version control
- The `.env` file is already in `.gitignore`
- For production deployment, use environment variables instead of `.env` files

## 📝 Development Notes

- The application uses Google Gemini Pro for AI responses
- PDF parsing is handled by PyPDF2
- Legal question filtering uses keyword detection
- File uploads are processed and analyzed locally
- Chat history is stored in SQLite database

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure both servers are running
4. Check the browser console and terminal for error messages

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Happy Coding! 🚀**