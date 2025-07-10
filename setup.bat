@echo off
echo Setting up AI Shopping Agent Project...
echo.

echo [1/4] Setting up Python Backend...
cd flask-backend
echo Creating virtual environment...
python -m venv venv
echo Activating virtual environment...
call venv\Scripts\activate
echo Installing basic Python dependencies...
pip install -r requirements-basic.txt
echo.
echo Note: Full AI dependencies are in requirements.txt if needed later
cd ..

echo.
echo [2/4] Setting up NextJS Frontend...
cd frontend
echo Installing Node.js dependencies...
npm install
cd ..

echo.
echo [3/4] Creating directories...
if not exist "flask-backend\uploads" mkdir flask-backend\uploads
if not exist "flask-backend\data" mkdir flask-backend\data

echo.
echo [4/4] Setup Complete! ✅
echo.
echo To start the development environment, run:
echo   start-dev.bat
echo.
echo Or manually:
echo   Backend: cd flask-backend && venv\Scripts\activate && python app.py
echo   Frontend: cd frontend && npm run dev
echo.
pause 