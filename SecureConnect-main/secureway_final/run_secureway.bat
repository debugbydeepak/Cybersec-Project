
@echo off
echo ===========================================
echo   Starting SECUREWAY Autonomous Logic Engine
echo   Hybrid Mode: Python 3.12 Backend + Static Frontend
echo ===========================================

echo [+] Installing Dependencies (This may take a moment)...
pip install fastapi uvicorn pydantic python-dotenv requests > nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Warning: Production dependencies failed to install.
    echo [!] Backend will launch in ALTERNATE SIMULATION MODE.
)

echo [+] Launching Backend Server (Port 8000)...
start "SECUREWAY Backend" cmd /k "cd backend && python main.py"

echo [+] Launching Frontend Interface (Port 8080)...
start "SECUREWAY Frontend" cmd /k "python -m http.server 8080 -d frontend"

echo ===========================================
echo   System Operational!
echo   > API: http://localhost:8000/docs
echo   > UI:  http://localhost:8080/index.html
echo ===========================================
echo   Note: If backend fails, check console for "Fallback Server" message.
pause
