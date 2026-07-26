@echo off
title JobHunt Backend Server
echo ========================================================
echo   Starting JobHunt FastAPI Backend Server (Firestore DB)
echo ========================================================
cd /d "c:\Users\pini_\Documents\Private\Pini\AntiGravity\JobHunt\backend"
call .\venv\Scripts\activate.bat
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause
