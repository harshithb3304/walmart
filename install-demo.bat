@echo off
echo AI Shopping Agent - Simple Demo Setup
echo ======================================
echo.

echo [1/4] Creating Python virtual environment...
cd flask-backend
python -m venv venv
call venv\Scripts\activate

echo.
echo [2/4] Installing minimal Flask dependencies...
pip install Flask Flask-CORS requests
echo ✅ Flask backend ready!

echo.
echo [3/4] Installing frontend dependencies...
cd ..\frontend
npm install --no-optional
echo ✅ NextJS frontend ready!

echo.
echo [4/4] Setup complete! 🎉
echo.
echo To start the demo:
echo   1. Backend: cd flask-backend && venv\Scripts\activate && python app.py
echo   2. Frontend: cd frontend && npm run dev
echo   3. Open: http://localhost:3000
echo.
echo Or run: start-dev.bat
echo.
pause 