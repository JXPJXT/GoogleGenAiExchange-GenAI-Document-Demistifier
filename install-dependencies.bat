@echo off
echo Installing Node.js dependencies for LegalLens AI Chatbot...
echo.

echo Checking if package-lock.json exists...
if exist package-lock.json (
    echo Using npm install...
    npm install
) else if exist pnpm-lock.yaml (
    echo Using pnpm install...
    pnpm install
) else (
    echo Using npm install...
    npm install
)

echo.
echo Dependencies installed successfully!
echo.
echo To start the application:
echo 1. Start the AI server: start-ai-server.bat
echo 2. Start the frontend: npm run dev
echo.
pause