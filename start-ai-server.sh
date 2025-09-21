#!/bin/bash
echo "Starting LegalLens AI Server..."
echo ""
echo "Installing/updating dependencies..."
pip3 install -r local-ai-requirements.txt
echo ""
echo "Starting server on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""
python3 local-ai-server.py