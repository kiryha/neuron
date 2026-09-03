@echo off
cd /d "%~dp0"
start "" http://127.0.0.1:5173
call npm run dev -- --host 127.0.0.1
pause
