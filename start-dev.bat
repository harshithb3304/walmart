@echo off
echo Starting AI Shopping Agent Development Environment...
echo.

echo [1/3] Checking Python Virtual Environment...
cd flask-backend
if not exist venv (
    echo Virtual environment not found. Please run install-demo.bat first.
    pause
    exit /b 1
)
call venv\Scripts\activate

echo [2/3] Starting Flask Backend Server...
start "Flask Backend" cmd /k "python app.py"

echo [3/3] Starting NextJS Frontend Server...
cd ..\frontend
start "NextJS Frontend" cmd /k "npm run dev"

echo.
echo ✅ Both servers are starting!
echo ✅ Backend: http://localhost:5000
echo ✅ Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul 