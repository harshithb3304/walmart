@echo off
echo Quick Start - AI Shopping Agent Demo
echo =====================================
echo.

echo [1/3] Installing basic Flask dependencies...
cd flask-backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
pip install Flask==3.0.0 Flask-CORS==4.0.0 requests==2.31.0
cd ..

echo.
echo [2/3] Installing Frontend dependencies...
cd frontend
if not exist node_modules (
    echo Installing npm packages...
    npm install
)
cd ..

echo.
echo [3/3] Starting Development Servers...
echo ✅ Backend: http://localhost:5000
echo ✅ Frontend: http://localhost:3000
echo.

start "Flask Backend" cmd /k "cd flask-backend && venv\Scripts\activate && python app.py"
timeout /t 3 /nobreak > nul
start "NextJS Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo 🚀 Both servers are starting!
echo 📱 Open http://localhost:3000 to view the demo
echo.
pause 