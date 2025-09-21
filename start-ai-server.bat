@echo off
echo Starting LegalLens AI Server...
echo.
echo Installing/updating dependencies...
pip install -r local-ai-requirements.txt
echo.
echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python local-ai-server.py