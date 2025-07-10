@echo off
echo Starting AI Shopping Assistant (Simple Mode)...
echo.

cd flask-backend

echo Checking if virtual environment exists...
if exist venv\Scripts\activate (
    echo ✅ Activating virtual environment...
    call venv\Scripts\activate
) else (
    echo ⚠️  No virtual environment found - using global Python
    echo This may cause import issues
)

echo.
echo Starting Flask backend in Simple Mode...
echo This version works even with missing dependencies!
echo.

REM Try the simple version first
if exist app_simple.py (
    echo Running simplified app (no complex dependencies needed)...
    python app_simple.py
) else (
    echo Running original app...
    python app.py
)

echo.
echo Server stopped.
pause 