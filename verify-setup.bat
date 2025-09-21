@echo off
echo.
echo 🔍 LegalLens AI Chatbot - Setup Verification
echo ==============================================
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('python --version') do set python_version=%%i
    echo ✅ Python found: !python_version!
)

REM Check Node.js
echo Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found. Please install Node.js 18 or higher.
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('node --version') do set node_version=%%i
    echo ✅ Node.js found: !node_version!
)

REM Check npm
echo Checking npm...
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm not found. Please install npm.
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('npm --version') do set npm_version=%%i
    echo ✅ npm found: !npm_version!
)

REM Check .env file
echo Checking environment configuration...
if exist .env (
    findstr "your_actual_gemini_api_key_here" .env >nul
    if %errorlevel% equ 0 (
        echo ⚠️  .env file exists but needs configuration
        echo    Please edit .env file and add your actual Gemini API key
    ) else (
        echo ✅ .env file configured
    )
) else (
    echo ⚠️  .env file not found. Please copy .env.example to .env and configure it
)

REM Check upload directory
echo Checking directories...
if exist "public\uploads" (
    echo ✅ Upload directory exists
) else (
    echo 📁 Creating uploads directory...
    mkdir "public\uploads"
    echo ✅ Upload directory created
)

echo.
echo 🎉 Setup verification complete!
echo.
echo Next steps:
echo 1. If any ❌ items above, please install the missing requirements
echo 2. Configure your .env file with your Gemini API key
echo 3. Run: install-dependencies.bat (to install Node.js packages)
echo 4. Run: start-ai-server.bat (to start the AI server)
echo 5. In another terminal, run: npm run dev (to start the frontend)
echo.
echo Then open http://localhost:3000 in your browser!
echo.
pause