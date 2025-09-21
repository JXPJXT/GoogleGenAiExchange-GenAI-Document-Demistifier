#!/bin/bash
echo "🔍 LegalLens AI Chatbot - Setup Verification"
echo "=============================================="
echo

# Check Python
echo "Checking Python..."
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    echo "✅ Python found: $python_version"
else
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check Node.js
echo "Checking Node.js..."
if command -v node &> /dev/null; then
    node_version=$(node --version)
    echo "✅ Node.js found: $node_version"
else
    echo "❌ Node.js not found. Please install Node.js 18 or higher."
    exit 1
fi

# Check npm
echo "Checking npm..."
if command -v npm &> /dev/null; then
    npm_version=$(npm --version)
    echo "✅ npm found: $npm_version"
else
    echo "❌ npm not found. Please install npm."
    exit 1
fi

# Check .env file
echo "Checking environment configuration..."
if [ -f ".env" ]; then
    if grep -q "your_actual_gemini_api_key_here" .env; then
        echo "⚠️  .env file exists but needs configuration"
        echo "   Please edit .env file and add your actual Gemini API key"
    else
        echo "✅ .env file configured"
    fi
else
    echo "⚠️  .env file not found. Please copy .env.example to .env and configure it"
fi

# Check required directories
echo "Checking directories..."
if [ -d "public/uploads" ]; then
    echo "✅ Upload directory exists"
else
    echo "📁 Creating uploads directory..."
    mkdir -p public/uploads
    echo "✅ Upload directory created"
fi

echo
echo "🎉 Setup verification complete!"
echo
echo "Next steps:"
echo "1. If any ❌ items above, please install the missing requirements"
echo "2. Configure your .env file with your Gemini API key"
echo "3. Run: ./install-dependencies.sh (to install Node.js packages)"
echo "4. Run: ./start-ai-server.sh (to start the AI server)"
echo "5. In another terminal, run: npm run dev (to start the frontend)"
echo
echo "Then open http://localhost:3000 in your browser!"
echo