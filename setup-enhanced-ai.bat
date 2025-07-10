@echo off
echo Setting up Enhanced AI Shopping Assistant with Web Search...
echo.

cd flask-backend

echo Installing all required dependencies...
pip install Flask>=3.0.0 Flask-CORS>=4.0.0 requests>=2.31.0
pip install google-generativeai>=0.3.0 python-dotenv>=1.0.0
pip install beautifulsoup4>=4.12.0 selenium>=4.15.0 googlesearch-python>=1.2.3

echo.
echo Dependencies installed!
echo.
echo ================================
echo   ENHANCED AI CAPABILITIES
echo ================================
echo.
echo ✅ Web Search - General queries and tech support
echo ✅ Walmart Search - Real-time product searches  
echo ✅ Gemini AI - Smart responses with search context
echo ✅ Tech Support - Troubleshooting and guidance
echo ✅ Price Comparison - Live product prices
echo.
echo SETUP REQUIRED:
echo 1. Get your Gemini API key from: https://makersuite.google.com/app/apikey
echo 2. Create a .env file in the flask-backend directory
echo 3. Add this line to the .env file:
echo    GEMINI_API_KEY=your_actual_api_key_here
echo.
echo You can copy the template from env_template.txt
echo.
echo Example queries to try:
echo - "Find me laptops under $500"
echo - "How to fix WiFi connection issues"
echo - "Best gaming headphones on Walmart"
echo - "Compare iPhone vs Samsung"
echo.
echo Ready to start? Run: start-dev.bat
echo.
pause 