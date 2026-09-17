@echo off
title IPL Analytics Hub
cd /d "d:\IPL_statistics"
echo =========================================================
echo    ?? Launching IPL Analytics Hub Dashboard...
echo =========================================================
echo Activating virtual environment...
call .\venv\Scripts\activate.bat
echo Starting Streamlit server...
.\venv\Scripts\streamlit.exe run app.py
pause
