@echo off
cd /d "%~dp0"
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found in venv folder!
    pause
    exit /b 1
)
call venv\Scripts\activate.bat
python manage.py makemigrations accounts assets dashboard reports scanner
python manage.py migrate
echo Server starting on http://127.0.0.1:8000
python manage.py runserver

