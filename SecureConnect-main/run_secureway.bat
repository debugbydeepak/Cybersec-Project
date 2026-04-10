@echo off
echo ======================================
echo    Starting SECUREWAY Autonomous Logic Engine
echo    (Python 3.12 + FastAPI + HTML/CSS/JS Frontend)
echo ======================================

echo [+] Installing minimal dependencies...
cd /d "%~dp0backend"
pip install -r requirements.txt >nul 2>&1

echo [+] Launching Backend API (Port 8000)...
start "SECUREWAY Backend" cmd /k "python main.py"

echo [+] Launching Frontend (Port 8080)...
cd /d "%~dp0"
start "SECUREWAY Frontend" cmd /k "python manage.py runserver 8080"

echo ======================================
echo    System Operational!
echo    Frontend: http://localhost:8080
echo    Backend API: http://localhost:8000/docs
echo ======================================
pause
