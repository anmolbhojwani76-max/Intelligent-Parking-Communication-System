@echo off
cd /d "%~dp0IntelligentParking"
where py >nul 2>nul
if %errorlevel% equ 0 (
    py -3 run_demo.py
) else (
    python run_demo.py
)
pause
