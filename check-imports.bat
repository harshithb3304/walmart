@echo off
echo Running Import Troubleshooter...
echo.

cd flask-backend

REM Activate virtual environment if it exists
if exist venv\Scripts\activate (
    echo Activating virtual environment...
    call venv\Scripts\activate
)

echo.
echo Running diagnostic script...
python ..\troubleshoot-imports.py

echo.
echo ================================
echo   TROUBLESHOOTING COMPLETE
echo ================================
echo.

if exist venv\Scripts\activate (
    echo Virtual environment is active
    echo All packages should be installed in: flask-backend\venv
) else (
    echo No virtual environment found
    echo Consider running: fix-imports.bat
)

echo.
pause 