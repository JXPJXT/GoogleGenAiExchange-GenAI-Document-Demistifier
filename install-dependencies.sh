#!/bin/bash
echo "Installing Node.js dependencies for LegalLens AI Chatbot..."
echo ""

echo "Checking package manager..."
if [ -f "pnpm-lock.yaml" ]; then
    echo "Using pnpm install..."
    pnpm install
elif [ -f "package-lock.json" ]; then
    echo "Using npm install..."
    npm install
else
    echo "Using npm install..."
    npm install
fi

echo ""
echo "Dependencies installed successfully!"
echo ""
echo "To start the application:"
echo "1. Start the AI server: ./start-ai-server.sh"
echo "2. Start the frontend: npm run dev"
echo ""