@echo off
cd /d "E:\pessoal\Bot Discord"
start "" pythonw.exe launcher.py
if errorlevel 1 (
    echo Python GUI launcher failed, trying with console version...
    timeout /t 2 /nobreak >nul
    start "" python.exe launcher.py
    if errorlevel 1 (
        echo.
        echo Error: Could not start launcher
        echo Please check that Python is installed correctly
        pause
    )
)