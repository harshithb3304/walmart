@echo off
echo Setting up Gemini AI Integration...
echo.

cd flask-backend

echo Installing required dependencies...
pip install google-generativeai>=0.3.0 python-dotenv>=1.0.0

echo.
echo Dependencies installed!
echo.
echo IMPORTANT: You need to set up your Gemini API key:
echo 1. Go to https://makersuite.google.com/app/apikey
echo 2. Create a new API key
echo 3. Create a .env file in the flask-backend directory
echo 4. Add this line to the .env file:
echo    GEMINI_API_KEY=your_actual_api_key_here
echo.
echo You can copy the template from env_template.txt
echo.
pause 