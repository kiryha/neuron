@echo off
cd /d "%~dp0"
start "Neuron API" cmd /k ".venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
start "" http://127.0.0.1:5173
call npm run dev -- --host 127.0.0.1
pause
