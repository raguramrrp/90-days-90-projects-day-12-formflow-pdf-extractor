@echo off
setlocal enabledelayedexpansion

echo ======================================================================
echo  FormFlow Setup — Day 12 of 90 Days 90 Projects Challenge
echo ======================================================================

:: 1. Check for Python
set "PYTHON_CMD="
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
) else (
    where python >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set "PYTHON_CMD=python"
    ) else (
        echo [ERROR] Python 3.10+ was not found on PATH or standard install directory.
        echo Please install Python from https://www.python.org/
        pause
        exit /b 1
    )
)

echo [1/5] Using Python: %PYTHON_CMD%

:: 2. Create or verify virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo [2/5] Creating dedicated virtual environment in .venv...
    "%PYTHON_CMD%" -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [2/5] Virtual environment already exists in .venv.
)

:: 3. Install dependencies
echo [3/5] Installing dependencies from requirements.txt...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Pip install returned non-zero. Continuing with installed site packages...
)

:: 4. Check for Tesseract OCR
echo [4/5] Checking Tesseract OCR Engine...
if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    echo [OK] Tesseract detected at: C:\Program Files\Tesseract-OCR\tesseract.exe
) else (
    where tesseract >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo [OK] Tesseract detected on system PATH.
    ) else (
        echo [INFO] Tesseract binary not detected in standard location.
        echo Selectable PDF text will extract normally.
        echo To enable OCR for scanned documents, install Tesseract from:
        echo https://github.com/UB-Mannheim/tesseract/wiki
    )
)

:: 5. Generate sample data and initialize DB
echo [5/5] Generating synthetic test PDFs and initializing database...
".venv\Scripts\python.exe" scripts\generate_sample_data.py
".venv\Scripts\python.exe" scripts\verify_system.py

echo ======================================================================
echo  Setup Complete! Start FormFlow with: run.bat
echo ======================================================================
pause
