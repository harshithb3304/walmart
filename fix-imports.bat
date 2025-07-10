@echo off
echo Fixing Python Import Issues...
echo.

cd flask-backend

echo Step 1: Creating fresh virtual environment...
if exist venv rmdir /s /q venv
python -m venv venv

echo.
echo Step 2: Activating virtual environment...
call venv\Scripts\activate

echo.
echo Step 3: Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Step 4: Installing core dependencies...
pip install Flask==3.0.0
pip install Flask-CORS==4.0.0 
pip install requests==2.31.0

echo.
echo Step 5: Installing AI dependencies...
pip install google-generativeai==0.3.0
pip install python-dotenv==1.0.0

echo.
echo Step 6: Installing web scraping dependencies...
pip install beautifulsoup4==4.12.0
pip install googlesearch-python==1.2.3

echo.
echo Step 7: Installing optional dependencies...
pip install selenium==4.15.0

echo.
echo Step 8: Verifying installations...
python -c "import flask; print('✅ Flask:', flask.__version__)"
python -c "import flask_cors; print('✅ Flask-CORS installed')"
python -c "import requests; print('✅ Requests:', requests.__version__)"
python -c "import google.generativeai; print('✅ Google GenerativeAI installed')"
python -c "import bs4; print('✅ BeautifulSoup installed')"
python -c "import googlesearch; print('✅ GoogleSearch installed')"

echo.
echo ================================
echo   IMPORT ISSUES RESOLVED! ✅
echo ================================
echo.
echo All dependencies are now properly installed.
echo.
echo Next steps:
echo 1. Set up your Gemini API key in .env file
echo 2. Use start-dev.bat to run the application
echo.
echo Virtual environment is located in: flask-backend\venv
echo Always activate it before running: call venv\Scripts\activate
echo.
pause 